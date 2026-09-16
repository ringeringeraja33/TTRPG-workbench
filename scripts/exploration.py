"""Explicit game-time activities, supply costs and persistent deadline reminders.

One campaign minute clock. No wall-clock scheduling or implicit system rules.
"""
import argparse
import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
from actions import fields,text,check_costs,TERMINAL

STORE='exploration'


def whole(value,minimum=0):
    if type(value) is not int or value<minimum:raise ValueError('Expected bounded integer minutes')
    return value


def visible(audience,player):return 'all' in audience or player is not None and player in audience


def validate_store(store,state):
    from session import audience
    fields(store,'schema audience activities reminders history')
    if type(store['schema']) is not int or store['schema']!=1:raise ValueError('Unsupported exploration schema')
    audience(store['audience'])
    if not isinstance(store['activities'],list) or not isinstance(store['reminders'],dict) or not isinstance(store['history'],list):
        raise ValueError('Invalid exploration containers')
    previous_end=0
    for activity in store['activities']:
        fields(activity,'summary participants audience start end costs event_id')
        text(activity['summary']);text(activity['event_id']);audience(activity['audience'])
        whole(activity['start']);whole(activity['end'])
        if not previous_end<=activity['start']<activity['end']<=state['clock']:
            raise ValueError('Invalid activity interval')
        previous_end=activity['end']
        participants(activity['participants'],state)
        validate_cost_records(activity['costs'],activity['participants'],state)
    for rid,r in store['reminders'].items():
        text(rid);fields(r,'label audience due every blocking status acknowledgements created_event')
        text(r['label']);text(r['created_event']);audience(r['audience']);whole(r['due']);whole(r['every'])
        if type(r['blocking']) is not bool or r['status'] not in {'pending','due','acknowledged','cancelled'} or not isinstance(r['acknowledgements'],list):
            raise ValueError('Invalid reminder')
        if r['status']=='pending' and r['due']<=state['clock'] or r['status']=='due' and r['due']>state['clock']:
            raise ValueError('Reminder status disagrees with game time')
        for ack in r['acknowledgements']:
            fields(ack,'due at resolution event_id');whole(ack['due']);whole(ack['at'])
            text(ack['resolution']);text(ack['event_id'])
            if not ack['due']<=ack['at']<=state['clock']:raise ValueError('Invalid acknowledgement time')
        if r['status']=='acknowledged' and (r['every'] or not r['acknowledgements']):
            raise ValueError('Invalid closed reminder')
    for item in store['history']:
        fields(item,'step event_id revision');text(item['event_id']);whole(item['revision'],1)
        if item['step'] not in {'setup','advance','schedule','ack','cancel','reschedule'}:raise ValueError('Invalid exploration history')


def participants(actors,state):
    if not isinstance(actors,list) or not actors or any(not isinstance(a,str) or a not in state['actors'] for a in actors) or len(set(actors))!=len(actors):
        raise ValueError('Explicit distinct activity participants required')


def validate_cost_records(costs,actors,state):
    # Historical receipts describe past spending, not current affordability.
    if not isinstance(costs,list):raise ValueError('Costs must be a list')
    for cost in costs:
        fields(cost,'kind actor resource delta')
        text(cost['actor']);text(cost['resource'])
        if cost['kind']!='resource' or type(cost['delta']) is not int or cost['delta']>=0:
            raise ValueError('Declared costs must be negative resource deltas')
        if cost['actor'] not in actors or cost['resource'] not in state['actors'][cost['actor']]['resources']:
            raise ValueError('Supply costs must reference participant resources')


def move_clock(state,minutes):
    whole(minutes)
    store=state['private'].get(STORE)
    if store is None:
        state['clock']+=minutes;return
    validate_store(store,state)
    if minutes:
        combat=state['private'].get('combat')
        if combat and combat['phase']!='finished':raise ValueError('Finish the encounter before advancing exploration time')
        if any(a['status'] not in TERMINAL for a in state['private'].get('action_workflow',{'actions':{}})['actions'].values()):
            raise ValueError('Resolve pending actions before advancing the shared campaign clock')
        for r in store['reminders'].values():
            if r['blocking'] and r['status'] in {'pending','due'} and r['due']<state['clock']+minutes:
                raise ValueError('A blocking game-time reminder must be reached and resolved before advancing further')
    state['clock']+=minutes
    for r in store['reminders'].values():
        if r['status']=='pending' and r['due']<=state['clock']:r['status']='due'


def transition(state,change,event):
    from session import audience
    fields(change,'kind step data');step,data=change['step'],change['data']
    store=state['private'].get(STORE)
    effects=[]
    if step=='setup':
        fields(data,'audience');audience(data['audience'])
        if store is not None:raise ValueError('Exploration already configured')
        store={'schema':1,'audience':copy.deepcopy(data['audience']),'activities':[],'reminders':{},'history':[]}
        state['private'][STORE]=store
    else:
        if store is None:raise ValueError('Set up exploration first')
        validate_store(store,state)
        if step=='advance':
            fields(data,'minutes participants summary costs audience')
            minutes=whole(data['minutes'],1)
            if minutes>10080:raise ValueError('Advance at most 10080 minutes per activity')
            text(data['summary']);audience(data['audience']);actors=data['participants']
            participants(actors,state)
            validate_cost_records(data['costs'],actors,state)
            check_costs(state,data['costs'])
            start=state['clock'];move_clock(state,minutes)
            store['activities'].append({'summary':data['summary'],'participants':copy.deepcopy(actors),'audience':copy.deepcopy(data['audience']),
                'start':start,'end':state['clock'],'costs':copy.deepcopy(data['costs']),'event_id':event['id']})
            effects=copy.deepcopy(data['costs'])
        elif step=='schedule':
            fields(data,'id label audience due every blocking');rid=text(data['id']);text(data['label']);audience(data['audience'])
            if rid in store['reminders']:raise ValueError('Reminder ID already exists')
            whole(data['due']);whole(data['every'])
            if data['due']<state['clock'] or type(data['blocking']) is not bool:raise ValueError('Reminder requires a current/future deadline and boolean blocking flag')
            store['reminders'][rid]={k:copy.deepcopy(data[k]) for k in ('label','audience','due','every','blocking')}
            store['reminders'][rid].update(status='due' if data['due']==state['clock'] else 'pending',acknowledgements=[],created_event=event['id'])
        elif step=='reschedule':
            fields(data,'id due every reason');text(data['id']);text(data['reason'])
            whole(data['due']);whole(data['every']);r=store['reminders'][data['id']]
            if r['status']!='pending':raise ValueError('Only a pending reminder can be rescheduled; resolve due occurrences first')
            if data['due']<state['clock']:raise ValueError('Reminder cannot be scheduled in the past')
            r['due']=data['due'];r['every']=data['every']
            r['status']='due' if data['due']==state['clock'] else 'pending'
        elif step=='ack':
            fields(data,'id resolution');text(data['id']);text(data['resolution']);r=store['reminders'][data['id']]
            if r['status']!='due':raise ValueError('Only a due reminder can be acknowledged')
            r['acknowledgements'].append({'due':r['due'],'at':state['clock'],'resolution':data['resolution'],'event_id':event['id']})
            if r['every']:
                r['due']+=r['every'];r['status']='due' if r['due']<=state['clock'] else 'pending'
            else:r['status']='acknowledged'
        elif step=='cancel':
            fields(data,'id reason');text(data['id']);text(data['reason']);r=store['reminders'][data['id']]
            if r['status'] not in {'pending','due'}:raise ValueError('Reminder is already closed')
            r['status']='cancelled'
        else:raise ValueError('Unknown exploration transition')
    store['history'].append({'step':step,'event_id':event['id'],'revision':event['revision']+1})
    validate_store(store,state)
    return effects


def project(store,state,player=None):
    if not visible(store['audience'],player):return None
    return {'minutes':state['clock'],
        'activities':[{k:copy.deepcopy(a[k]) for k in ('summary','start','end')} for a in store['activities'] if visible(a['audience'],player)],
        'reminders':[{k:copy.deepcopy(r[k]) for k in ('label','due','status')} for r in store['reminders'].values()
                     if r['status'] in {'pending','due'} and visible(r['audience'],player)]}


def summary(store,state):
    return {'minutes':state['clock'],'due':{rid:copy.deepcopy(r) for rid,r in store['reminders'].items() if r['status']=='due'},
            'next_blocking_minute':min((r['due'] for r in store['reminders'].values() if r['blocking'] and r['status'] in {'pending','due'}),default=None)}


def require_event(event):
    changes=event.get('changes') if isinstance(event,dict) else None
    if not isinstance(changes,list) or len(changes)!=1 or not isinstance(changes[0],dict) or changes[0].get('kind')!='exploration':
        raise ValueError('Exploration CLI requires exactly one exploration change')


def preview(database,event):
    """Validate on a consistent SQLite copy; leave the source ledger untouched."""
    import session
    require_event(event)
    with tempfile.TemporaryDirectory(prefix='ttrpg-exploration-preview-') as folder:
        target=Path(folder)/'preview.sqlite'
        source=session.connect(database)
        destination=sqlite3.connect(target)
        try:source.backup(destination)
        finally:destination.close();source.close()
        before=session.view(target,gm=True)
        receipt=session.apply(target,event)
        after=session.view(target,gm=True)
        old,new=before['state'],after['state']
        deltas=[]
        for actor,record in new['actors'].items():
            for resource,balance in record['resources'].items():
                previous=old['actors'][actor]['resources'][resource]['value']
                if balance['value']!=previous:
                    deltas.append({'actor':actor,'resource':resource,'before':previous,'after':balance['value']})
        return {'preview':True,'base_revision':before['revision'],'event':copy.deepcopy(event),
                'receipt':receipt,'minutes':{'before':old['clock'],'after':new['clock']},
                'resources':deltas,'timing':summary(new['private'][STORE],new)}


def main():
    import session
    from dice_local import save_private_output
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('database',type=Path)
    sub=parser.add_subparsers(dest='command',required=True)
    a=sub.add_parser('apply');a.add_argument('--event',required=True,type=Path)
    p=sub.add_parser('preview');p.add_argument('--event',required=True,type=Path);p.add_argument('--private-output',required=True,type=Path)
    v=sub.add_parser('view');v.add_argument('--player');v.add_argument('--private-output',type=Path)
    args=parser.parse_args()
    try:
        if args.command in {'apply','preview'}:
            event=json.loads(args.event.read_text(encoding='utf-8-sig'));require_event(event)
            if args.command=='preview':
                result=preview(args.database,event);save_private_output(args.private_output,result)
                result={'base_revision':result['base_revision'],'private_preview_saved':True}
            else:result=session.apply(args.database,event)
        else:
            saved=session.view(args.database,gm=True);state=saved['state'];store=state['private'].get(STORE)
            if args.private_output:
                if args.player:raise ValueError('Choose player view or private GM output')
                result={'revision':saved['revision'],'exploration':store,'timing':summary(store,state) if store else None}
                save_private_output(args.private_output,result);result={'revision':saved['revision'],'private_result_saved':True}
            else:result={'revision':saved['revision'],'exploration':project(store,state,args.player) if store else None}
        print(session.encode(result))
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as exc:
        print(session.encode({'error':str(exc)}),file=sys.stderr);raise SystemExit(2)


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    main()
