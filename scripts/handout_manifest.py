"""Validate private handout variants and project only explicitly released player text."""
import argparse
import hashlib
import json
from pathlib import Path


def validate(pack, root=None):
    issues, ids = [], set()
    for h in pack.get('handouts', []):
        hid = h.get('id')
        if not hid or hid in ids: issues.append('Missing or duplicate handout id')
        ids.add(hid)
        if h.get('audience') not in {'gm', 'players', 'individual'}: issues.append(f'{hid}: invalid audience')
        if h.get('audience') == 'individual' and not h.get('recipients'): issues.append(f'{hid}: missing recipients')
        variants = h.get('variants', {})
        if not variants or h.get('selected_variant') not in variants: issues.append(f'{hid}: select an existing variant')
        for name, v in variants.items():
            if v.get('review') not in {'unreviewed', 'player-safe', 'gm-only'}: issues.append(f'{hid}/{name}: missing visual review state')
            if root:
                p = (Path(root) / v.get('path', '')).resolve()
                if not p.is_relative_to(Path(root).resolve()) or not p.is_file():
                    issues.append(f'{hid}/{name}: missing or out-of-root asset')
                elif hashlib.sha256(p.read_bytes()).hexdigest() != v.get('sha256'):
                    issues.append(f'{hid}/{name}: asset hash mismatch')
        if h.get('released'):
            selected = variants.get(h.get('selected_variant'), {})
            if h.get('audience') != 'gm' and selected.get('review') != 'player-safe': issues.append(f'{hid}: unsafe selected variant')
            if not set(h.get('requires', [])).issubset(set(pack.get('revealed_facts', []))): issues.append(f'{hid}: reveal prerequisites unmet')
            if not h.get('player_title') and h.get('audience') != 'gm': issues.append(f'{hid}: missing player title')
    return issues


def project(pack, player, root=None):
    issues = validate(pack, root)
    if issues: raise ValueError('; '.join(issues))
    visible = []
    for h in pack.get('handouts', []):
        if not h.get('released') or h['audience'] == 'gm': continue
        if h['audience'] == 'individual' and player not in h['recipients']: continue
        # Do not publish GM filenames, hidden variants, source notes or prerequisites.
        visible.append({'id': h['id'], 'title': h['player_title'], 'text': h.get('player_text', '')})
    return {'player': player, 'handouts': visible}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest', type=Path); ap.add_argument('--root', type=Path)
    ap.add_argument('--player'); ap.add_argument('--output', type=Path)
    a = ap.parse_args(); pack = json.loads(a.manifest.read_text(encoding='utf-8'))
    result = project(pack, a.player, a.root) if a.player else {'issues': validate(pack, a.root)}
    value = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if a.output:
        if a.output.resolve() == a.manifest.resolve(): raise ValueError('Keep GM manifest separate')
        a.output.write_text(value, encoding='utf-8')
        assert a.output.read_text(encoding='utf-8') == value
    else: print(value)
