"""Ledger-backed clue delivery and hypotheses; dependency analysis stays GM-only."""
import argparse
import copy
import json
from pathlib import Path
import sqlite3
import sys
import investigation
from actions import fields,text

STORE='investigation'


def validate_plan(plan):
    fields(plan,'schema evidence conclusions')
    if type(plan['schema']) is not int or plan['schema']!=1:
        raise ValueError('Investigation schema 1 required')
    if not isinstance(plan['evidence'],list) or not isinstance(plan['conclusions'],list) or len(plan['evidence'])+len(plan['conclusions'])>2000:
        raise ValueError('Supply bounded evidence and conclusion lists')
    for row in plan['evidence']:fields(row,'id text audience available')
    for row in plan['conclusions']:fields(row,'id text audience essential routes')
    investigation.validate(plan)


def recipients(state,value):
    if not isinstance(value,list) or not value or any(not isinstance(a,str) or a not in state['actors'] for a in value) or len(set(value))!=len(value):
        raise ValueError('Recipients must be distinct existing actor IDs; public/future recipients are not implicit')


def validate_store(store,state):
    fields(store,'schema plan knowledge hypotheses history')
    if type(store['schema']) is not int or store['schema']!=1:raise ValueError('Unsupported investigation runtime schema')
    validate_plan(store['plan'])
    ids={e['id'] for e in store['plan']['evidence']}
    if not isinstance(store['knowledge'],dict) or not isinstance(store['hypotheses'],dict) or not isinstance(store['history'],list):
        raise ValueError('Invalid investigation containers')
    for actor,known in store['knowledge'].items():
        if actor not in state['actors'] or not isinstance(known,dict):raise ValueError('Invalid knowledge owner')
        for eid,receipt in known.items():
            if eid not in ids:raise ValueError('Unknown acquired evidence')
            fields(receipt,'text events')
            if not isinstance(receipt['text'],str) or not isinstance(receipt['events'],list) or not receipt['events']:
                raise ValueError('Invalid acquisition receipt')
    for hid,hypothesis in store['hypotheses'].items():
        text(hid);fields(hypothesis,'actor text evidence status public_resolution gm_reason created_event resolved_event')
        if hypothesis['actor'] not in state['actors'] or hypothesis['status'] not in {'open','confirmed','refuted'}:
            raise ValueError('Invalid hypothesis')
        text(hypothesis['text'])
        if not isinstance(hypothesis['evidence'],list) or any(e not in store['knowledge'].get(hypothesis['actor'],{}) for e in hypothesis['evidence']):
            raise ValueError('Hypothesis cites evidence unknown to its actor')


def transition(state,change,event):
    fields(change,'kind step data');step,data=change['step'],change['data']
    store=state['private'].get(STORE)
    if step=='setup':
        fields(data,'plan')
        if store is not None:raise ValueError('Investigation already configured; restore or use explicit runtime changes')
        validate_plan(data['plan'])
        store={'schema':1,'plan':copy.deepcopy(data['plan']),'knowledge':{},'hypotheses':{},'history':[]}
        state['private'][STORE]=store
    else:
        if store is None:raise ValueError('Set up the investigation first')
        validate_store(store,state)
        evidence={e['id']:e for e in store['plan']['evidence']}
        if step=='extend':
            fields(data,'evidence conclusions routes reason');text(data['reason'])
            if any(not isinstance(data[k],list) for k in ('evidence','conclusions','routes')):
                raise ValueError('Extension requires evidence, conclusion and route lists')
            if not any(data[k] for k in ('evidence','conclusions','routes')):
                raise ValueError('Empty investigation extension')
            candidate=copy.deepcopy(store['plan'])
            candidate['evidence'].extend(copy.deepcopy(data['evidence']))
            candidate['conclusions'].extend(copy.deepcopy(data['conclusions']))
            # Validate record shapes and references before indexing the new plan.
            validate_plan(candidate)
            conclusions={c['id']:c for c in candidate['conclusions']}
            for addition in data['routes']:
                fields(addition,'conclusion route');text(addition['conclusion'])
                if addition['conclusion'] not in conclusions:raise ValueError('Unknown route conclusion')
                route=addition['route']
                if not isinstance(route,list) or not route or any(not isinstance(i,str) for i in route) or len(set(route))!=len(route):
                    raise ValueError('Route requires distinct dependency IDs')
                target=conclusions[addition['conclusion']]['routes']
                if any(set(route)==set(existing) for existing in target):raise ValueError('Route already exists')
                target.append(copy.deepcopy(route))
            validate_plan(candidate)
            store['plan']=candidate
        elif step=='edit_unseen':
            fields(data,'evidence text reason');text(data['evidence']);text(data['text']);text(data['reason'])
            if data['evidence'] not in evidence:raise ValueError('Unknown evidence')
            if any(data['evidence'] in known for known in store['knowledge'].values()):
                raise ValueError('Delivered evidence cannot be rewritten; add a new observation with a new ID')
            evidence[data['evidence']]['text']=data['text']
        elif step=='available':
            fields(data,'evidence available reason');text(data['reason'])
            if type(data['available']) is not bool:raise ValueError('Availability must be boolean')
            evidence[data['evidence']]['available']=data['available']
        elif step in {'discover','share'}:
            fields(data,'evidence recipients method' if step=='discover' else 'evidence recipients sender method')
            text(data['method']);recipients(state,data['recipients']);eid=data['evidence']
            if eid not in evidence:raise ValueError('Unknown evidence')
            if step=='discover':
                if not evidence[eid]['available']:raise ValueError('Evidence is currently unavailable')
                delivered_text=evidence[eid]['text']
            else:
                sender=data['sender']
                if sender not in store['knowledge'] or eid not in store['knowledge'][sender]:
                    raise ValueError('Sender has not acquired this evidence')
                delivered_text=store['knowledge'][sender][eid]['text']
            for actor in data['recipients']:
                receipt=store['knowledge'].setdefault(actor,{}).setdefault(eid,{'text':delivered_text,'events':[]})
                receipt['events'].append({'kind':step,'event_id':event['id'],'revision':event['revision']+1})
        elif step=='hypothesize':
            fields(data,'id actor text evidence');hid=text(data['id']);text(data['text'])
            if hid in store['hypotheses']:raise ValueError('Hypothesis ID already exists')
            if data['actor'] not in state['actors']:raise ValueError('Unknown hypothesis actor')
            if not isinstance(data['evidence'],list) or len(set(data['evidence']))!=len(data['evidence']):
                raise ValueError('Supporting evidence must be distinct IDs')
            if any(e not in store['knowledge'].get(data['actor'],{}) for e in data['evidence']):
                raise ValueError('Actor cannot cite undelivered evidence')
            store['hypotheses'][hid]={k:copy.deepcopy(data[k]) for k in ('actor','text','evidence')}
            store['hypotheses'][hid].update(status='open',public_resolution='',gm_reason='',created_event=event['id'],resolved_event=None)
        elif step=='resolve':
            fields(data,'id status public_resolution gm_reason')
            if data['status'] not in {'confirmed','refuted'}:raise ValueError('Explicit confirmed/refuted verdict required')
            text(data['public_resolution']);text(data['gm_reason'])
            hypothesis=store['hypotheses'][data['id']]
            if hypothesis['status']!='open':raise ValueError('Hypothesis already resolved; use an explicit restore for a correction')
            hypothesis.update(status=data['status'],public_resolution=data['public_resolution'],gm_reason=data['gm_reason'],resolved_event=event['id'])
        else:raise ValueError('Unknown investigation transition')
    store['history'].append({'step':step,'event_id':event['id'],'revision':event['revision']+1})
    validate_store(store,state)


def project(store,player=None):
    if player is None:return {'evidence':[],'hypotheses':[]}
    return {'evidence':[{'id':eid,'text':r['text']} for eid,r in store['knowledge'].get(player,{}).items()],
            'hypotheses':[{'id':hid,**{k:copy.deepcopy(h[k]) for k in ('text','evidence','status','public_resolution')}}
                          for hid,h in store['hypotheses'].items() if h['actor']==player]}


def analysis(store,state):
    per_actor={}
    for actor in state['actors']:
        plan=copy.deepcopy(store['plan']);known=store['knowledge'].get(actor,{})
        for e in plan['evidence']:
            e['available']=e['id'] in known
            e['audience']=[actor]
        per_actor[actor]=investigation.audit(plan,player=actor)
    return {'preparation':investigation.audit(store['plan']),'actual_knowledge':per_actor,
            'open_hypotheses':[hid for hid,h in store['hypotheses'].items() if h['status']=='open'],
            'scope':'GM-only declared dependency support. No automatic deduction, revelation, or proof of truth.'}


def main():
    import session
    from dice_local import save_private_output
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('database',type=Path)
    sub=parser.add_subparsers(dest='command',required=True)
    a=sub.add_parser('apply');a.add_argument('--event',required=True,type=Path)
    v=sub.add_parser('view');v.add_argument('--player');v.add_argument('--private-output',type=Path)
    args=parser.parse_args()
    try:
        if args.command=='apply':
            event=json.loads(args.event.read_text(encoding='utf-8-sig'))
            changes=event.get('changes') if isinstance(event,dict) else None
            if not isinstance(changes,list) or len(changes)!=1 or not isinstance(changes[0],dict) or changes[0].get('kind')!='investigation':
                raise ValueError('Investigation CLI requires one investigation change')
            result=session.apply(args.database,event)
        else:
            saved=session.view(args.database,gm=True);state=saved['state'];store=state['private'].get(STORE)
            if args.private_output:
                if args.player:raise ValueError('Choose player output or private GM output')
                result={'revision':saved['revision'],'investigation':store,
                        'analysis':analysis(store,state) if store else None}
                save_private_output(args.private_output,result)
                result={'revision':saved['revision'],'private_result_saved':True}
            else:result={'revision':saved['revision'],'investigation':project(store,args.player) if store else None}
        print(session.encode(result))
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as exc:
        print(session.encode({'error':str(exc)}),file=sys.stderr);raise SystemExit(2)


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    main()
