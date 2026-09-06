"""Explicit historical design pack audit; CoC7 arithmetic via existing adapter."""
import argparse
from collections import deque
import json
from pathlib import Path
import background_chargen


def walk(pack, failure=False, start=None):
    """Find an ordinary route to END with no special skills or equipment."""
    scenes = {s['id']: s for s in pack['scenes']}
    queue = deque([(start or pack['start'], [])])
    seen = set()
    while queue:
        current, path = queue.popleft()
        if current == 'END':
            return path + ['END']
        if current in seen or current not in scenes:
            continue
        seen.add(current)
        for route in scenes[current]['routes']:
            if not route['skills'] and not route['items']:
                queue.append((route['failure' if failure else 'success'], path+[current]))
    return []


def audit(pack, spec):
    errors, pending = [], []
    def need(ok, message):
        if not ok: errors.append(message)
    def text_fields(obj, names, label):
        for name in names:
            need(isinstance(obj.get(name), str) and bool(obj[name].strip()), label+' missing '+name)
    def indexed(name):
        rows=pack[name]
        if not isinstance(rows,list) or not rows: raise ValueError(name+' must be a nonempty list')
        result={}
        for row in rows:
            if not isinstance(row,dict) or not isinstance(row.get('id'),str) or not row['id'].strip():
                raise ValueError('invalid '+name+' record')
            need(row['id'] not in result,'duplicate '+name+' ID: '+row['id'])
            need(row['id'] != 'END','reserved ID END')
            result[row['id']]=row
        return result
    try:
        cards=background_chargen.audit(spec)
        errors.extend(cards['errors']);pending.extend(cards['pending'])
        need(pack['profile']==spec['profile'],'profile conflict')
        text_fields(pack,['premise','gm_secret'],'pack')
        sources=pack['sources']
        if not isinstance(sources,dict) or not sources: pending.append('Missing evidence sources')
        def evidence(ref):
            source=sources.get(ref,{}) if isinstance(sources,dict) else {}
            if source.get('status')!='read' or not source.get('locator') or not source.get('scope'):
                pending.append('Unverified source: '+str(ref))
        evidence('history')
        if isinstance(sources,dict):
            for ref in sources:evidence(ref)
        skills,items,scenes=indexed('skills'),indexed('items'),indexed('scenes')
        for k,skill in skills.items():
            text_fields(skill,['name','treatment','use','limit'],'skill '+k)
            need(k in spec['skill_bases'],'unknown skill: '+k)
            need(type(skill.get('base')) is type(spec['skill_bases'].get(k)) and skill.get('base')==spec['skill_bases'].get(k),'skill base conflict: '+k)
            need(type(skill.get('cap')) is int and skill['cap']==spec['skill_cap'],'skill cap conflict: '+k)
            evidence(skill.get('source'))
        for k,item in items.items():
            text_fields(item,['name','acquisition','price_basis','procedure','effect','limits','upkeep','substitute'],'item '+k)
            need(item.get('availability') in ('scenario allocation','source verified'),'unreviewed availability: '+k)
            need(type(item.get('quantity')) is int and item['quantity']>0,'invalid quantity: '+k)
            evidence(item.get('source'))
        need(pack['start'] in scenes,'unknown start')
        used_skills,used_items=set(),set()
        graph={k:set() for k in scenes}
        for k,scene in scenes.items():
            text_fields(scene,['title','purpose','entry','exit_condition','npc','objects','clue','pressure'],'scene '+k)
            need(type(scene.get('exit')) is bool,'invalid exit: '+k)
            routes=scene['routes'];need(isinstance(routes,list) and bool(routes),'no routes: '+k)
            ids=set();has_end=False
            for route in routes:
                text_fields(route,['id','method','cost','outcome'],'route '+k)
                need(route['id'] not in ids,'duplicate route ID: '+k);ids.add(route['id'])
                for field,known,used in [('skills',skills,used_skills),('items',items,used_items)]:
                    if not isinstance(route[field],list) or any(not isinstance(x,str) for x in route[field]):
                        raise ValueError('invalid route requirements')
                    used.update(route[field])
                    for ref in route[field]:need(ref in known,'unknown route '+field+': '+ref)
                for outcome in ('success','failure'):
                    target=route[outcome]
                    need(target in scenes or target=='END','unknown destination: '+str(target))
                    graph[k].add(target);has_end |= target=='END'
            need(not scene.get('exit') or has_end,'exit has no END route: '+k)
            need(not has_end or scene.get('exit') is True,'END route not marked exit: '+k)
            for failure in (False,True):
                need(bool(walk(pack,failure,k)),'no ordinary '+('failure' if failure else 'success')+' path: '+k)
        seen=set();todo=[pack['start']]
        while todo:
            node=todo.pop()
            if node in seen or node not in graph:continue
            seen.add(node);todo.extend(graph[node])
        for node in set(scenes)-seen:errors.append('unreachable scene: '+node)
        for skill in set(skills)-used_skills:errors.append('unused skill: '+skill)
        for item in set(items)-used_items:errors.append('unused item: '+item)
    except (KeyError,ValueError,TypeError,AttributeError) as exc:
        errors.append('invalid pack or creation input: '+str(exc))
        cards={'cards':[]}
    return {'status':'invalid' if errors else 'draft' if pending else 'passed explicit checks',
            'errors':errors,'pending':sorted(set(pending)), 'characters':cards.get('cards',[]),
            'scope':'Configured CoC7 arithmetic and route checks; history and clue semantics require review'}


def player_view(pack,result):
    if result['status']=='invalid':return {'status':'invalid'}
    return {'status':result['status'],'premise':pack['premise'],
            'skills':[{k:s[k] for k in ('id','name','treatment','base','cap','use','limit')} for s in pack['skills']],
            'items':[{k:i[k] for k in ('id','name','availability','acquisition','quantity','price_basis','procedure','effect','limits','upkeep','substitute')} for i in pack['items']]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack',type=Path);parser.add_argument('--chargen',type=Path,required=True)
    parser.add_argument('--player',action='store_true');args=parser.parse_args()
    try:
        pack=json.loads(args.pack.read_text(encoding='utf-8-sig'))
        spec=json.loads(args.chargen.read_text(encoding='utf-8-sig'))
        result=audit(pack,spec)
        output=player_view(pack,result) if args.player else result
    except (ValueError,OSError) as exc:
        result=output={'status':'invalid','errors':[str(exc)]}
    print(json.dumps(output,ensure_ascii=False,indent=2))
    return result['status']!='passed explicit checks'

if __name__=='__main__':
    raise SystemExit(main())
