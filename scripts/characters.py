"""Strict character JSON import with private preview and ledger-owned resources.

Imports record explicit operator decisions; they do not certify character legality.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
from actions import fields, text

STORE='characters'


def canonical(value):
    return ' '.join(unicodedata.normalize('NFC',text(value)).casefold().split())


def stable_id(value):
    if not isinstance(value,str) or not re.fullmatch(r'[a-z][a-z0-9_.-]{0,63}',value):
        raise ValueError('Stat IDs must be stable lowercase ASCII identifiers, at most 64 characters')
    return value


def validate_stats(stats):
    if not isinstance(stats,dict) or len(stats)>500:
        raise ValueError('Stats must be an object with at most 500 entries')
    names={}
    for sid,stat in stats.items():
        stable_id(sid);fields(stat,'label aliases value');text(stat['label'])
        if type(stat['value']) is not int or not -999<=stat['value']<=999:
            raise ValueError('Stat values must be integers -999..999; this storage bound is not a system rule')
        if not isinstance(stat['aliases'],list) or len(stat['aliases'])>20:
            raise ValueError('Stat aliases must be a list of at most 20 names')
        for word in [sid,stat['label'],*stat['aliases']]:
            name=canonical(word)
            if name in names and names[name]!=sid:
                raise ValueError('Ambiguous stat name or alias')
            names[name]=sid
    return names


def validate_store(store,state):
    from session import audience
    fields(store,'schema records')
    if type(store['schema']) is not int or store['schema']!=1 or not isinstance(store['records'],dict):
        raise ValueError('Unsupported character schema')
    for actor,record in store['records'].items():
        if actor not in state['actors']:raise ValueError('Character metadata has no actor')
        fields(record,'stats sheet_audience gm_notes sources updated_event')
        validate_stats(record['stats']);audience(record['sheet_audience'])
        if not isinstance(record['gm_notes'],str):raise ValueError('GM notes must be text')
        if not isinstance(record['sources'],list) or not record['sources'] or any(not isinstance(s,str) or not s.strip() for s in record['sources']):
            raise ValueError('Character sources required')
        text(record['updated_event'])


def resolve_stat(state,actor,query):
    records=state['private'].get(STORE,{'records':{}})['records']
    if actor not in records:raise ValueError('Actor has no imported stat sheet')
    record=records[actor];names=validate_stats(record['stats']);name=canonical(query)
    if name not in names:raise ValueError('Unknown stat name')
    sid=names[name];stat=record['stats'][sid]
    return {'actor':actor,'id':sid,'label':stat['label'],'value':stat['value'],
            'sheet_event':record['updated_event']}


def transition(state,change,event):
    from session import audience, integer
    from combat import actor_pending
    from vendor.sagasmith_resources import resize_bounded_resource
    fields(change,'kind manifest');manifest=change['manifest']
    fields(manifest,'schema profile sources characters')
    if type(manifest['schema']) is not int or manifest['schema']!=1:
        raise ValueError('Unsupported character manifest schema')
    if manifest['profile']!=state['profile'] or manifest['profile']!=event['profile']:
        raise ValueError('Character import profile mismatch')
    sources=manifest['sources']
    if not isinstance(sources,list) or not sources or any(not isinstance(s,str) or not s.strip() for s in sources):
        raise ValueError('Manifest source anchors or explicit GM ruling required')
    entries=manifest['characters']
    if not isinstance(entries,list) or not 1<=len(entries)<=100:
        raise ValueError('Import requires 1..100 characters')
    store=state['private'].setdefault(STORE,{'schema':1,'records':{}})
    validate_store(store,state)
    seen=set()
    for entry in entries:
        fields(entry,'mode id name audience sheet_audience stats resources gm_notes')
        actor=text(entry['id']);text(entry['name']);audience(entry['audience']);audience(entry['sheet_audience'])
        if actor in seen:raise ValueError('Duplicate actor in import')
        seen.add(actor)
        if not isinstance(entry['gm_notes'],str):raise ValueError('GM notes must be text')
        validate_stats(entry['stats'])
        if not isinstance(entry['resources'],dict):raise ValueError('Resources must be an object')
        previous=state['actors'].get(actor)
        if entry['mode']=='create':
            if previous is not None:raise ValueError('Create cannot overwrite an existing actor')
        elif entry['mode']=='update':
            if previous is None:raise ValueError('Update requires an existing actor')
            if not set(previous['resources'])<=set(entry['resources']):
                raise ValueError('Import cannot remove existing resources')
        else:raise ValueError('Import mode must be create or update')
        resources={}
        for key,resource in entry['resources'].items():
            text(key)
            old=previous['resources'].get(key) if previous else None
            if old is None:
                fields(resource,'value max')
                if integer(resource['value'])>integer(resource['max']):raise ValueError('Initial resource exceeds capacity')
                resources[key]=copy.deepcopy(resource)
            else:
                fields(resource,'max');maximum=integer(resource['max'])
                value=copy.deepcopy(old)
                resize_bounded_resource(value,maximum=maximum);value.pop('unlimited')
                resources[key]=value
        old_record=store['records'].get(actor)
        mechanical=previous is not None and (resources!=previous['resources'] or entry['stats']!=(old_record['stats'] if old_record else {}))
        if mechanical:
            if actor_pending(state,actor):raise ValueError('Resolve pending actions and costs before mechanical character updates')
            combat=state['private'].get('combat')
            if combat and combat['phase']!='finished' and actor in combat['order']:
                raise ValueError('Mechanical character updates require leaving or finishing the encounter')
        # Current conditions remain ledger-owned, not a hidden side effect of imports.
        state['actors'][actor]={'name':entry['name'],'audience':copy.deepcopy(entry['audience']),
                                'resources':resources,'conditions':copy.deepcopy(previous['conditions']) if previous else []}
        store['records'][actor]={'stats':copy.deepcopy(entry['stats']),'sheet_audience':copy.deepcopy(entry['sheet_audience']),
                                'gm_notes':entry['gm_notes'],'sources':copy.deepcopy(sources),'updated_event':event['id']}
    validate_store(store,state)


def diff(before,after,path=''):
    changes=[]
    if isinstance(before,dict) and isinstance(after,dict):
        for key in sorted(set(before)|set(after)):
            changes.extend(diff(before.get(key),after.get(key),path+'/'+key.replace('~','~0').replace('/','~1')))
    elif before!=after:
        changes.append({'path':path,'before':copy.deepcopy(before),'after':copy.deepcopy(after)})
    return changes


def preview(path,manifest,event_id):
    import session
    saved=session.view(path,gm=True)
    return preview_snapshot(saved,manifest,event_id)


def preview_snapshot(saved,manifest,event_id):
    import session
    event={'id':text(event_id),'revision':saved['revision'],'profile':copy.deepcopy(saved['state']['profile']),
           'input':'Import explicitly supplied structured character records',
           'resolution':'Apply reviewed character fields; preserve spent resources and existing conditions',
           'sources':copy.deepcopy(manifest.get('sources')) if isinstance(manifest,dict) else [],
           'changes':[{'kind':'characters','manifest':copy.deepcopy(manifest)}]}
    if event_id.startswith('__'):raise ValueError('Reserved event ID')
    after=copy.deepcopy(saved['state']);transition(after,event['changes'][0],event);session.validate(after)
    plan={'revision':saved['revision'],'event':event,'changes':diff(saved['state'],after),
          'scope':'Validated storage and state compatibility; not complete rules legality'}
    plan['plan_sha256']=session.digest(plan)
    return plan


def apply_plan(path,plan):
    import session
    fields(plan,'revision event changes scope plan_sha256')
    unsigned={k:v for k,v in plan.items() if k!='plan_sha256'}
    if session.digest(unsigned)!=plan['plan_sha256']:
        raise ValueError('Preview plan changed; regenerate the preview')
    event=plan['event'];changes=event.get('changes') if isinstance(event,dict) else None
    if not isinstance(changes,list) or len(changes)!=1 or not isinstance(changes[0],dict) or changes[0].get('kind')!='characters':
        raise ValueError('Character plan requires one characters change')
    return session.apply(path,event)


def project(state,player=None):
    result={}
    for actor,record in state['private'].get(STORE,{'records':{}})['records'].items():
        if 'all' in record['sheet_audience'] or player is not None and player in record['sheet_audience']:
            # Sheet disclosure is explicitly independent of actor resource disclosure.
            result[actor]={'name':state['actors'][actor]['name'],'stats':{
                sid:{'label':stat['label'],'aliases':list(stat['aliases']),'value':stat['value']}
                for sid,stat in record['stats'].items()}}
    return result


def export_manifest(path,actor,mode='update'):
    import session
    if mode not in {'create','update'}:raise ValueError('Export mode must be create or update')
    saved=session.view(path,gm=True)
    return manifest_from_state(saved['state'],actor,mode)


def manifest_from_state(state,actor,mode='update'):
    base=state['actors'][actor]
    record=state['private'].get(STORE,{'records':{}})['records'].get(actor)
    if record is None:raise ValueError('Actor has no imported sheet; supply explicit metadata before exporting')
    resources={key:(copy.deepcopy(value) if mode=='create' else {'max':value['max']}) for key,value in base['resources'].items()}
    entry={'mode':mode,'id':actor,'name':base['name'],'audience':copy.deepcopy(base['audience']),
           'sheet_audience':copy.deepcopy(record['sheet_audience']),'stats':copy.deepcopy(record['stats']),
           'resources':resources,'gm_notes':record['gm_notes']}
    return {'schema':1,'profile':copy.deepcopy(state['profile']),'sources':copy.deepcopy(record['sources']),
            'characters':[entry]}


def preview_update(path,actor,patch,event_id):
    """Merge an explicit partial update against one revision, then validate normally."""
    import session
    fields(patch,'schema sources changes')
    if type(patch['schema']) is not int or patch['schema']!=1:raise ValueError('Character patch schema 1 required')
    changes=patch['changes']
    allowed={'name','audience','sheet_audience','gm_notes','stats','resources','remove_stats'}
    if not isinstance(changes,dict) or not changes or not set(changes)<=allowed:
        raise ValueError('Supply supported character patch fields')
    saved=session.view(path,gm=True)
    manifest=manifest_from_state(saved['state'],text(actor))
    manifest['sources']=copy.deepcopy(patch['sources'])
    entry=manifest['characters'][0]
    for key in ('name','audience','sheet_audience','gm_notes'):
        if key in changes:entry[key]=copy.deepcopy(changes[key])
    for key in ('stats','resources'):
        if key in changes:
            if not isinstance(changes[key],dict):raise ValueError('Partial stats/resources must be objects')
            entry[key].update(copy.deepcopy(changes[key]))
    removals=changes.get('remove_stats',[])
    if not isinstance(removals,list) or any(not isinstance(s,str) for s in removals) or len(set(removals))!=len(removals):
        raise ValueError('Removed stats must be distinct existing IDs')
    for sid in removals:
        stable_id(sid)
        if sid not in entry['stats']:raise ValueError('Cannot remove an unknown stat')
        if sid in changes.get('stats',{}):raise ValueError('Cannot update and remove the same stat')
        del entry['stats'][sid]
    # Use the same snapshot for merging and previewing; a concurrent update then
    # makes this plan stale instead of silently overwriting its untouched fields.
    return preview_snapshot(saved,manifest,event_id)


def main():
    import session
    from dice_local import save_private_output
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('database',type=Path)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('preview');p.add_argument('--manifest',type=Path,required=True);p.add_argument('--event-id',required=True);p.add_argument('--private-output',type=Path,required=True)
    u=sub.add_parser('preview-update');u.add_argument('--actor',required=True);u.add_argument('--patch',type=Path,required=True);u.add_argument('--event-id',required=True);u.add_argument('--private-output',type=Path,required=True)
    a=sub.add_parser('apply');a.add_argument('--plan',type=Path,required=True)
    e=sub.add_parser('export');e.add_argument('--actor',required=True);e.add_argument('--mode',choices=['create','update'],default='update');e.add_argument('--private-output',type=Path,required=True)
    v=sub.add_parser('view');v.add_argument('--player')
    args=parser.parse_args()
    try:
        if args.command in {'preview','preview-update'}:
            if args.command=='preview':
                plan=preview(args.database,json.loads(args.manifest.read_text(encoding='utf-8-sig')),args.event_id)
            else:
                plan=preview_update(args.database,args.actor,json.loads(args.patch.read_text(encoding='utf-8-sig')),args.event_id)
            save_private_output(args.private_output,plan)
            result={'revision':plan['revision'],'changes':len(plan['changes']),'private_preview_saved':True}
        elif args.command=='apply':
            plan=json.loads(args.plan.read_text(encoding='utf-8-sig'))
            result=apply_plan(args.database,plan)
        elif args.command=='export':
            value=export_manifest(args.database,args.actor,args.mode);save_private_output(args.private_output,value)
            result={'private_export_saved':True}
        else:
            saved=session.view(args.database,gm=True)
            result={'revision':saved['revision'],'characters':project(saved['state'],args.player)}
        print(session.encode(result))
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as exc:
        print(session.encode({'error':str(exc)}),file=sys.stderr);raise SystemExit(2)


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    main()
