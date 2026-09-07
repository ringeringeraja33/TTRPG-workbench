"""Validate capability records and generate the current coverage page."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('source', 'retrieval', 'procedure', 'arithmetic', 'interaction')


def render(root=ROOT):
    data = json.loads((root / 'references/capabilities.json').read_text(encoding='utf-8'))
    lines = ['# Current capability coverage', '',
             'Generated from `capabilities.json` by `scripts/capabilities.py`. Edit the JSON, then regenerate.', '',
             'Statuses are scoped claims: supported, partial, none, or not-applicable. Source access, retrieval, procedures, arithmetic and interaction checks are independent. No row certifies an entire system.', '',
             '| Capability | Source | Retrieval | Procedure | Arithmetic | Interaction | Scope and limits |',
             '|---|---|---|---|---|---|---|']
    ids = set()
    for row in data['capabilities']:
        if row['id'] in ids:
            raise ValueError('Duplicate capability ID')
        ids.add(row['id'])
        for field in FIELDS:
            if row[field] not in {'supported', 'partial', 'none', 'not-applicable'}:
                raise ValueError('Invalid status')
        ref = root / 'references' / row['reference']
        if not ref.resolve().is_relative_to(root.resolve()) or not ref.is_file():
            raise ValueError('Missing or escaping capability reference')
        cells = [f"[{row['name']}]({row['reference']})"] + [row[f] for f in FIELDS] + [row['limits']]
        lines.append('| ' + ' | '.join(c.replace('|', '\\|').replace('\n', ' ') for c in cells) + ' |')
    lines += ['', '## Verification and history', '',
              'See [current verification](validation.md) for commands and the latest executed results. Live-player evaluation is outside the requested acceptance scope. Simulated cases do not establish play quality or exhaustive interaction coverage.', '',
              'Earlier coverage and acceptance records are retained in [coverage history](coverage-history.md) and [validation history](validation-history.md); historical gaps and counts are not current status.', '']
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true', help='Fail if generated coverage is stale')
    a = p.parse_args()
    target = ROOT / 'references/coverage.md'
    content = render()
    if a.check:
        if target.read_text(encoding='utf-8') != content:
            p.exit(1, 'Coverage is stale; run capabilities.py\n')
    else:
        target.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
