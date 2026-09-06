"""Private, hash-bound corpus index and bounded multilingual source retrieval."""
import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from corpus_readers import extract
from library import classify

EXCLUDE = {'索引', '.git', '__pycache__', '.obsidian'}
REVIEW = {'unreviewed', 'structure-reviewed', 'passage-verified', 'adopted', 'conflict', 'unreadable'}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript('''
      CREATE TABLE IF NOT EXISTS sources(
        id TEXT PRIMARY KEY, path TEXT NOT NULL, sha256 TEXT NOT NULL,
        system_candidate TEXT, status TEXT, error TEXT, unit_count INTEGER);
      CREATE TABLE IF NOT EXISTS units(
        source_id TEXT, anchor TEXT, text TEXT, metadata TEXT,
        PRIMARY KEY(source_id, anchor));
      CREATE TABLE IF NOT EXISTS reviews(
        source_id TEXT, anchor TEXT, state TEXT, note TEXT,
        PRIMARY KEY(source_id, anchor));
      CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY, value TEXT);
    ''')
    return db


def build(root, output, *, cache_dir=None, chm_root=None, ocr=False):
    root, output = Path(root).resolve(), Path(output).resolve()
    skill = Path(__file__).resolve().parents[1]
    if output.is_relative_to(skill):
        raise ValueError('Full-text index must stay outside the distributable skill')
    if not root.is_dir():
        raise ValueError('Source root is not a directory')
    output.parent.mkdir(parents=True, exist_ok=True)
    db = connect(output)
    seen = set()
    try:
        for file in sorted(root.rglob('*')):
            if not file.is_file() or file.resolve() == output or any(p in EXCLUDE for p in file.relative_to(root).parts):
                continue
            rel = file.relative_to(root).as_posix()
            sha = digest(file)
            # Path identity preserves separate copies; content hash preserves review validity.
            sid = hashlib.sha256(rel.encode('utf-8')).hexdigest()[:16]
            seen.add(sid)
            previous = db.execute('SELECT * FROM sources WHERE id=?', (sid,)).fetchone()
            cached = Path(cache_dir) / (sha[:16] + '.jsonl') if cache_dir else None
            # Always re-extract/re-import; a previous sparse extraction is not final.
            try:
                if cached and cached.is_file():
                    units = [json.loads(line) for line in cached.read_text(encoding='utf-8').split('\n') if line]
                else:
                    units = list(extract(file, chm_root=chm_root, ocr_enabled=ocr))
                if not units:
                    raise ValueError('Reader returned no units')
                anchors = [u['anchor'] for u in units]
                if len(anchors) != len(set(anchors)):
                    raise ValueError('Duplicate source anchors')
                state = 'extracted'
                if any('sparse' in u.get('method', '') or 'metadata;' in u.get('method', '') for u in units):
                    state = 'partial'
                error = None
            except Exception as exc:
                units, state, error = [], 'error', f'{type(exc).__name__}: {exc}'
            with db:
                if previous and previous['sha256'] != sha:
                    db.execute('DELETE FROM reviews WHERE source_id=?', (sid,))
                db.execute('DELETE FROM units WHERE source_id=?', (sid,))
                db.execute('INSERT OR REPLACE INTO sources VALUES(?,?,?,?,?,?,?)',
                           (sid, rel, sha, classify(file.name), state, error, len(units)))
                db.executemany('INSERT INTO units VALUES(?,?,?,?)', [
                    (sid, u['anchor'], u['text'], json.dumps({k: v for k, v in u.items() if k not in {'anchor', 'text'}}, ensure_ascii=False, default=str)) for u in units])
        with db:
            for row in db.execute('SELECT id FROM sources').fetchall():
                if row['id'] not in seen:
                    for table in ('units', 'reviews'):
                        db.execute(f'DELETE FROM {table} WHERE source_id=?', (row['id'],))
                    db.execute('DELETE FROM sources WHERE id=?', (row['id'],))
            db.execute('INSERT OR REPLACE INTO config VALUES(?,?)', ('root', str(root)))
        return [dict(row) for row in db.execute('SELECT * FROM sources ORDER BY path')]
    finally:
        db.close()


def search(db, query, *, source=None, limit=8, chars=1600, anchor=None):
    if not query and not anchor:
        raise ValueError('Supply a nonempty query or exact anchor')
    if not 1 <= limit <= 100 or not 1 <= chars <= 12000:
        raise ValueError('Output bounds exceeded')
    clauses, args = ['instr(lower(u.text), lower(?)) > 0'], [query]
    if not query:
        clauses, args = ['1=1'], []
    if source:
        clauses.append('(s.id=? OR instr(lower(s.path),lower(?))>0)')
        args.extend([source, source])
    if anchor:
        clauses.append('u.anchor=?')
        args.append(anchor)
    args.append(limit)
    sql = '''SELECT s.id,s.path,s.sha256,u.anchor,u.text,u.metadata,
      coalesce(r.state,'unreviewed') review_state,r.note
      FROM units u JOIN sources s ON s.id=u.source_id
      LEFT JOIN reviews r ON r.source_id=u.source_id AND r.anchor=u.anchor
      WHERE ''' + ' AND '.join(clauses) + ' ORDER BY s.path,u.rowid LIMIT ?'
    root = Path(db.execute("SELECT value FROM config WHERE key='root'").fetchone()[0])
    checked = {}
    results = []
    for row in db.execute(sql, args):
        item = dict(row)
        if item['id'] not in checked:
            file = root / item['path']
            checked[item['id']] = file.is_file() and digest(file) == item['sha256']
        item['source_current'] = checked[item['id']]
        pos = item['text'].lower().find(query.lower()) if query else 0
        start = max(0, pos - 150)
        item['text'] = item['text'][start:start + chars]
        item['metadata'] = json.loads(item['metadata'])
        results.append(item)
    return results


def review(db, source, anchor, state, note):
    if state not in REVIEW or not note.strip():
        raise ValueError('Review needs a valid state and a substantive note')
    if not db.execute('SELECT 1 FROM units WHERE source_id=? AND anchor=?', (source, anchor)).fetchone():
        raise ValueError('Review target must be an existing source unit')
    row = db.execute('SELECT path,sha256 FROM sources WHERE id=?', (source,)).fetchone()
    root = Path(db.execute("SELECT value FROM config WHERE key='root'").fetchone()[0])
    file = root / row['path']
    if not file.is_file() or digest(file) != row['sha256']:
        raise ValueError('Rebuild or relocate the changed source before recording a review')
    with db:
        db.execute('INSERT OR REPLACE INTO reviews VALUES(?,?,?,?)', (source, anchor, state, note))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    commands = ap.add_subparsers(dest='command', required=True)
    b = commands.add_parser('build')
    b.add_argument('root', type=Path); b.add_argument('--output', required=True, type=Path)
    b.add_argument('--cache-dir', type=Path, help='Trusted local SHA-256-prefix JSONL extraction cache')
    b.add_argument('--chm-root', type=Path); b.add_argument('--ocr', action='store_true')
    s = commands.add_parser('search')
    s.add_argument('index', type=Path); s.add_argument('query', nargs='?', default='')
    s.add_argument('--source'); s.add_argument('--anchor')
    s.add_argument('--limit', type=int, default=8); s.add_argument('--chars', type=int, default=1600)
    r = commands.add_parser('review')
    r.add_argument('index', type=Path); r.add_argument('source'); r.add_argument('anchor')
    r.add_argument('state', choices=sorted(REVIEW)); r.add_argument('note')
    a = ap.parse_args()
    if a.command == 'build':
        result = build(a.root, a.output, cache_dir=a.cache_dir, chm_root=a.chm_root, ocr=a.ocr)
        result = {'files': len(result), 'statuses': {status: sum(r['status'] == status for r in result) for status in ('extracted', 'partial', 'error')}, 'errors': [r for r in result if r['status'] == 'error']}
    else:
        if not a.index.is_file():
            raise ValueError('Index does not exist')
        db = connect(a.index)
        try:
            if a.command == 'search': result = search(db, a.query, source=a.source, limit=a.limit, chars=a.chars, anchor=a.anchor)
            else:
                review(db, a.source, a.anchor, a.state, a.note)
                result = {'recorded': True}
        finally: db.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
