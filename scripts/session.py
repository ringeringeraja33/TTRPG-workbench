"""Transactional local campaign ledger. Rules are adjudicated before application.

UTF-8 JSON in/out; SQLite transactions bind revision, event and state together.
No network, hooks, implicit dice, or model dependencies.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from vendor.sagasmith_resources import resize_bounded_resource


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(encode(value).encode('utf-8')).hexdigest()


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError('Expected bounded integer')
    return value


def validate(state):
    if not isinstance(state, dict) or set(state) != {'profile', 'actors', 'facts', 'private', 'pending', 'clock'}:
        raise ValueError('Invalid state fields')
    p = state['profile']
    if not isinstance(p, dict) or set(p) != {'system', 'edition', 'options'} or not all(isinstance(p[k], str) and p[k].strip() for k in ['system', 'edition']) or not isinstance(p['options'], dict):
        raise ValueError('Explicit system, edition and options required')
    integer(state['clock'])
    if not isinstance(state['actors'], dict) or not isinstance(state['facts'], list) or not isinstance(state['pending'], list) or not isinstance(state['private'], dict):
        raise ValueError('Invalid state containers')
    for actor in state['actors'].values():
        if set(actor) != {'name', 'audience', 'resources', 'conditions'} or not isinstance(actor['name'], str):
            raise ValueError('Invalid actor')
        audience(actor['audience'])
        if not isinstance(actor['conditions'], list) or not all(isinstance(x, str) for x in actor['conditions']):
            raise ValueError('Conditions must be strings')
        if not isinstance(actor['resources'], dict):
            raise ValueError('Resources must be an object')
        for resource in actor['resources'].values():
            if set(resource) != {'value', 'max'} or integer(resource['value']) > integer(resource['max']):
                raise ValueError('Resource out of bounds')
    for fact in state['facts']:
        if set(fact) != {'id', 'text', 'audience'} or not isinstance(fact['id'], str) or not isinstance(fact['text'], str):
            raise ValueError('Invalid fact')
        audience(fact['audience'])
    if len({f['id'] for f in state['facts']}) != len(state['facts']):
        raise ValueError('Duplicate fact ID')
    encode(state)


def audience(value):
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        raise ValueError('Audience must be explicit list; empty means GM only')


def connect(path):
    if not Path(path).is_file():
        raise ValueError('Campaign database missing; use init')
    db = sqlite3.connect(path, timeout=10)
    return db


def init(path, state):
    validate(state)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental replacement of an existing campaign.
    with path.open('xb'):
        pass
    db = sqlite3.connect(path)
    try:
        with db:
            db.execute('CREATE TABLE events (revision INTEGER PRIMARY KEY, id TEXT UNIQUE NOT NULL, request_hash TEXT NOT NULL, request TEXT NOT NULL, state TEXT NOT NULL)')
            db.execute('INSERT INTO events VALUES (0, ?, ?, ?, ?)', ('__init__', digest(state), encode({'kind': 'init'}), encode(state)))
    finally:
        db.close()
    return {'revision': 0, 'state_sha256': digest(state)}


def latest(db):
    row = db.execute('SELECT revision, state FROM events ORDER BY revision DESC LIMIT 1').fetchone()
    if not row:
        raise ValueError('Empty campaign')
    return row[0], json.loads(row[1])


def apply(path, event):
    required = {'id', 'revision', 'profile', 'input', 'resolution', 'sources', 'changes'}
    if not isinstance(event, dict) or set(event) != required or not isinstance(event['id'], str) or not event['id'] or event['id'].startswith('__'):
        raise ValueError('Invalid event contract')
    integer(event['revision'])
    if not isinstance(event['changes'], list) or not all(isinstance(c, dict) for c in event['changes']):
        raise ValueError('Changes must be a list of operations')
    if not isinstance(event['input'], str) or not event['input'] or not isinstance(event['resolution'], str) or not event['resolution']:
        raise ValueError('Player input and resolved outcome required')
    if not isinstance(event['sources'], list) or not event['sources'] or not all(isinstance(s, str) and s.strip() for s in event['sources']):
        raise ValueError('Rule anchors or explicit GM ruling required; missing rules must remain pending')
    request_hash = digest(event)
    db = connect(path)
    try:
        db.execute('BEGIN IMMEDIATE')
        previous = db.execute('SELECT revision, request_hash, state FROM events WHERE id=?', (event['id'],)).fetchone()
        if previous:
            if previous[1] != request_hash:
                raise ValueError('Event ID reused with different content')
            db.rollback()
            return {'revision': previous[0], 'duplicate': True, 'state_sha256': digest(json.loads(previous[2]))}
        revision, state = latest(db)
        if revision != event['revision']:
            raise ValueError('Stale revision; reload and adjudicate again')
        if state['profile'] != event['profile']:
            raise ValueError('Rules profile conflict; no implicit edition migration')
        for change in event['changes']:
            kind = change['kind']
            if kind == 'resource':
                if set(change) != {'kind', 'actor', 'resource', 'delta'} or type(change['delta']) is not int:
                    raise ValueError('Invalid resource change')
                resource = state['actors'][change['actor']]['resources'][change['resource']]
                resource['value'] += change['delta']
                # No silent clamping: the adjudicator must state actual healing/spend.
            elif kind == 'resize':
                if set(change) != {'kind', 'actor', 'resource', 'maximum'}:
                    raise ValueError('Invalid resource resize')
                maximum = integer(change['maximum'])
                resource = state['actors'][change['actor']]['resources'][change['resource']]
                resize_bounded_resource(resource, maximum=maximum)
                resource.pop('unlimited')  # Ledger uses finite counters only.
            elif kind == 'conditions':
                if set(change) != {'kind', 'actor', 'value'}:
                    raise ValueError('Invalid condition change')
                state['actors'][change['actor']]['conditions'] = change['value']
            elif kind == 'fact':
                if set(change) != {'kind', 'value'}:
                    raise ValueError('Invalid fact change')
                state['facts'].append(change['value'])
            elif kind == 'clock':
                if set(change) != {'kind', 'minutes'}:
                    raise ValueError('Invalid clock change')
                state['clock'] += integer(change['minutes'])
            elif kind in {'pending', 'private'}:
                if set(change) != {'kind', 'value'}:
                    raise ValueError('Invalid private state change')
                state[kind] = change['value']
            elif kind == 'restore':
                if set(change) != {'kind', 'revision'} or len(event['changes']) != 1:
                    raise ValueError('Restore must be the only change')
                integer(change['revision'])
                row = db.execute('SELECT state FROM events WHERE revision=?', (change['revision'],)).fetchone()
                if not row:
                    raise ValueError('Restore target missing')
                state = json.loads(row[0])
            else:
                raise ValueError('Unsupported change; no implicit rule resolution')
        validate(state)
        db.execute('INSERT INTO events VALUES (?, ?, ?, ?, ?)', (revision + 1, event['id'], request_hash, encode(event), encode(state)))
        db.commit()
        return {'revision': revision + 1, 'duplicate': False, 'state_sha256': digest(state)}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def view(path, player=None, gm=False):
    db = connect(path)
    try:
        revision, state = latest(db)
    finally:
        db.close()
    validate(state)
    if gm:
        return {'revision': revision, 'state': state}
    def visible(item):
        return 'all' in item['audience'] or (player is not None and player in item['audience'])
    return {'revision': revision, 'actors': {k: copy.deepcopy(v) for k, v in state['actors'].items() if visible(v)},
            'facts': [copy.deepcopy(f) for f in state['facts'] if visible(f)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init').add_argument('--config', type=Path, required=True)
    sub.add_parser('apply').add_argument('--event', type=Path, required=True)
    v = sub.add_parser('view')
    v.add_argument('--gm', action='store_true')
    v.add_argument('--player')
    args = parser.parse_args()
    if args.command == 'init':
        result = init(args.database, json.loads(args.config.read_text(encoding='utf-8-sig')))
    elif args.command == 'apply':
        result = apply(args.database, json.loads(args.event.read_text(encoding='utf-8-sig')))
    else:
        result = view(args.database, args.player, args.gm)
    print(encode(result))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as error:
        print(encode({'error': str(error)}), file=sys.stderr)
        raise SystemExit(2)
