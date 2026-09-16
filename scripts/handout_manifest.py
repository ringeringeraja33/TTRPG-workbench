"""Validate private handout variants and project only explicitly released player text."""
import argparse
import hashlib
import json
from pathlib import Path


def string_list(value):
    return isinstance(value,list) and all(isinstance(x,str) and x.strip() for x in value)


def validate(pack, root=None):
    issues, ids = [], set()
    if not isinstance(pack,dict) or not isinstance(pack.get('handouts'),list):
        return ['Manifest requires a handouts list']
    revealed=pack.get('revealed_facts',[])
    if not string_list(revealed): return ['revealed_facts must be a list of IDs']
    for h in pack['handouts']:
        if not isinstance(h,dict):
            issues.append('Handout must be an object'); continue
        hid=h.get('id')
        if not isinstance(hid,str) or not hid.strip():
            issues.append('Missing handout id'); continue
        if hid in ids: issues.append('Duplicate handout id')
        ids.add(hid)
        audience=h.get('audience')
        if audience not in ('gm','players','individual'): issues.append(hid+': invalid audience')
        released=h.get('released',False)
        if type(released) is not bool: issues.append(hid+': released must be a boolean')
        recipients=h.get('recipients',[])
        if not string_list(recipients) or (audience=='individual' and not recipients):
            issues.append(hid+': recipients must be a list of complete player IDs')
        requires=h.get('requires',[])
        if not string_list(requires): issues.append(hid+': requires must be a list of IDs')
        for key in ('player_title','player_text'):
            if key in h and not isinstance(h[key],str): issues.append(hid+': '+key+' must be text')
        variants=h.get('variants',{})
        selected_name=h.get('selected_variant')
        if not isinstance(variants,dict) or not variants:
            issues.append(hid+': variants must be a nonempty object'); continue
        if not isinstance(selected_name,str) or selected_name not in variants:
            issues.append(hid+': select an existing variant'); continue
        for name,v in variants.items():
            if not isinstance(name,str) or not isinstance(v,dict):
                issues.append(hid+': invalid variant'); continue
            if v.get('review') not in ('unreviewed','player-safe','gm-only'):
                issues.append(hid+'/'+name+': missing visual review state')
            if root:
                value=v.get('path')
                if not isinstance(value,str) or not value:
                    issues.append(hid+'/'+name+': missing asset path'); continue
                try:
                    p=(Path(root)/value).resolve()
                    if not p.is_relative_to(Path(root).resolve()) or not p.is_file():
                        issues.append(hid+'/'+name+': missing or out-of-root asset')
                    elif hashlib.sha256(p.read_bytes()).hexdigest()!=v.get('sha256'):
                        issues.append(hid+'/'+name+': asset hash mismatch')
                except (OSError,ValueError) as exc:
                    issues.append(hid+'/'+name+': unreadable asset: '+str(exc))
        if released is True:
            selected=variants[selected_name]
            if audience!='gm' and (not isinstance(selected,dict) or selected.get('review')!='player-safe'):
                issues.append(hid+': unsafe selected variant')
            if string_list(requires) and not set(requires)<=set(revealed):
                issues.append(hid+': reveal prerequisites unmet')
            if audience!='gm' and (not isinstance(h.get('player_title'),str) or not h['player_title'].strip()):
                issues.append(hid+': missing player title')
    return issues


def project(pack, player, root=None):
    if not isinstance(player,str) or not player.strip(): raise ValueError('Explicit player ID required')
    issues = validate(pack, root)
    if issues: raise ValueError('; '.join(issues))
    visible = []
    for h in pack.get('handouts', []):
        if h.get('released') is not True or h['audience'] == 'gm': continue
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
