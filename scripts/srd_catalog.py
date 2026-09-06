"""Read every SRD 5.2.1 class and spell from the verified official PDF.

No PDF text is bundled. Output is source text, not an adjudicated execution card.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

PDF_SHA256 = '8974902d109d6e63672d7c490bde9ccf052410503d9cfa768237154fbc5e3d87'
CLASSES = {'Barbarian': (28, 30), 'Bard': (31, 35), 'Cleric': (36, 40),
           'Druid': (41, 46), 'Fighter': (47, 49), 'Monk': (49, 52),
           'Paladin': (53, 57), 'Ranger': (57, 61), 'Rogue': (61, 64),
           'Sorcerer': (64, 70), 'Warlock': (70, 76), 'Wizard': (77, 82)}
SPELL_META = re.compile(r'^(?:Level [1-9] \w+|\w+ Cantrip) \(')


def key(name):
    return ' '.join(name.casefold().split())


def parse_spells(pages):
    """Keep page anchors and line order; retain the unabridged spell body."""
    lines = []
    for number, text in pages:
        for line in text.splitlines():
            if line.strip() in {str(number), 'System Reference Document 5.2.1', 'Spell Descriptions'}:
                continue
            lines.append((number, line))
    starts = [i-1 for i, (_, line) in enumerate(lines) if SPELL_META.match(line.strip())]
    entries = []
    for index, start in enumerate(starts):
        stop = starts[index+1] if index+1 < len(starts) else len(lines)
        segment = lines[start:stop]
        name = ' '.join(segment[0][1].split()).title()
        body = '\n'.join(t for _, t in segment).strip()
        if 'Casting Time:' not in body or 'Duration:' not in body:
            raise ValueError('Incomplete extracted spell: '+name)
        entries.append({'name': name, 'pdf_pages': sorted({n for n, _ in segment}), 'text': body})
    if len({key(e['name']) for e in entries}) != len(entries):
        raise ValueError('Ambiguous duplicate spell names')
    return entries


def load(pdf):
    from pypdf import PdfReader
    data = pdf.read_bytes()
    if hashlib.sha256(data).hexdigest() != PDF_SHA256:
        raise ValueError('Unverified PDF/edition: this reader requires the official SRD 5.2.1 bytes')
    reader = PdfReader(pdf)
    pages = [(n, reader.pages[n-1].extract_text()) for n in range(107, 176)]
    spells = parse_spells(pages)
    casting_headers = sum(t.count('Casting Time:') for _, t in pages)
    if len(spells) != 339 or casting_headers != len(spells):
        raise ValueError('Extraction coverage changed; do not treat this as a complete catalog')
    for spell in spells:
        if spell['text'].count('Casting Time:') != 1 or 'Range:' not in spell['text'] or not re.search(r'\bComponents?:', spell['text']):
            raise ValueError('Incomplete or merged source entry: '+spell['name'])
    return reader, spells


def select(spells, name):
    matches = [s for s in spells if key(s['name']) == key(name)]
    if len(matches) != 1:
        raise ValueError('Exact SRD spell not found: '+name)
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('index')
    sub.add_parser('spell').add_argument('name')
    sub.add_parser('class').add_argument('name', choices=list(CLASSES))
    args = parser.parse_args()
    reader, spells = load(args.pdf)
    if args.command == 'index':
        result = {'classes': CLASSES, 'spells': [{k: v for k, v in s.items() if k != 'text'} for s in spells]}
    elif args.command == 'spell':
        result = select(spells, args.name)
    else:
        first, last = CLASSES[args.name]
        result = {'class': args.name, 'pages': [{'pdf_page': n, 'text': reader.pages[n-1].extract_text()}
                  for n in range(first, last+1)], 'note': 'Boundary pages may also contain the adjacent class.'}
    print(json.dumps({'edition': 'SRD 5.2.1', 'source_sha256': PDF_SHA256, 'result': result}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
