"""Explicit, rule-profile-bound encounter boundaries and timed effects.

This is a timing ledger, not an automatic D&D/CoC legality engine. Refresh rules
and expiry boundaries are supplied by the adjudicator with event sources.
"""
import argparse
import copy
import json
from pathlib import Path
import sqlite3
import sys
from actions import fields, text, TERMINAL


def positive(value):
    if type(value) is not int or value < 1:
        raise ValueError('Expected positive integer')
    return value


def visible(audience, player):
    return 'all' in audience or player is not None and player in audience


def validate_store(store, state):
    names='schema id profile audience order round index turn phase counts refresh effects history past_ids'
    if isinstance(store,dict) and store.get('schema') == 2: names+=' current round_used'
    fields(store,names)
    if type(store['schema']) is not int or store['schema'] not in {1,2}:
        raise ValueError('Unsupported combat schema')
    text(store['id'])
    if not isinstance(store['past_ids'],list) or any(not isinstance(x,str) for x in store['past_ids']):
        raise ValueError('Invalid encounter identity history')
    if store['profile'] != state['profile']:
        raise ValueError('Combat profile conflict')
    from session import audience
    audience(store['audience'])
    order = store['order']
    if not isinstance(order,list) or not order or any(not isinstance(a,str) or a not in state['actors'] for a in order) or len(set(order)) != len(order):
        raise ValueError('Order requires distinct existing actors')
    if type(store['index']) is not int or not -1 <= store['index'] < len(order):
        raise ValueError('Invalid combat index')
    if store['schema']==1 and store['index']<0:
        raise ValueError('Invalid legacy combat index')
    positive(store['round']); positive(store['turn'])
    if store['phase'] not in {'active','ended','finished'}:
        raise ValueError('Invalid turn phase')
    if not isinstance(store['counts'],dict) or not set(order)<=set(store['counts']) or any(a not in state['actors'] for a in store['counts']):
        raise ValueError('Invalid boundary counters')
    if store['schema']==1 and set(store['counts'])!=set(order):
        raise ValueError('Legacy counters must match the fixed order')
    if store['schema']==2:
        if store['current'] not in store['counts'] or (store['phase']=='active' and store['current'] not in order):
            raise ValueError('Invalid current actor')
        expected=order.index(store['current']) if store['current'] in order else -1
        if store['index'] != expected: raise ValueError('Current actor/index conflict')
        used=store['round_used']
        if not isinstance(used,list) or any(not isinstance(a,str) or a not in store['counts'] for a in used) or len(set(used))!=len(used):
            raise ValueError('Invalid round eligibility')
        if store['current'] not in used: raise ValueError('Current turn must be recorded in round eligibility')
    for count in store['counts'].values():
        fields(count,'start end')
        if any(type(v) is not int or v < 0 for v in count.values()):
            raise ValueError('Invalid boundary count')
    if not isinstance(store['refresh'],list) or not isinstance(store['effects'],dict) or not isinstance(store['history'],list):
        raise ValueError('Invalid combat containers')
    seen = set()
    for rule in store['refresh']:
        fields(rule,'actor resource at value')
        if rule['actor'] not in store['counts'] or rule['at'] not in {'start','end'} or type(rule['value']) is not int:
            raise ValueError('Invalid refresh rule')
        resource = state['actors'][rule['actor']]['resources'][rule['resource']]
        if not 0 <= rule['value'] <= resource['max']:
            raise ValueError('Refresh value outside resource capacity')
        key=(rule['actor'],rule['resource'],rule['at'])
        if key in seen: raise ValueError('Duplicate refresh rule')
        seen.add(key)
    for eid,effect in store['effects'].items():
        text(eid)
        fields(effect,'label targets audience expires status sources created_event expired_event')
        text(effect['label']); audience(effect['audience'])
        if not isinstance(effect['targets'],list) or not effect['targets'] or any(a not in store['counts'] for a in effect['targets']):
            raise ValueError('Effect targets must be encounter participants')
        expires=effect['expires']; fields(expires,'actor at occurrence')
        if expires['actor'] not in store['counts'] or expires['at'] not in {'start','end'}:
            raise ValueError('Invalid expiry boundary')
        positive(expires['occurrence'])
        if effect['status'] not in {'active','expired','removed'}:
            raise ValueError('Invalid effect state')
        if effect['status']=='active' and (expires['actor'] not in order or any(a not in order for a in effect['targets'])):
            raise ValueError('Active effect refers to a departed actor')


def current_actor(store):
    return store['current'] if store['schema']==2 else store['order'][store['index']]


def upgrade(store):
    if store['schema']==1:
        store['current']=store['order'][store['index']]
        store['round_used']=list(store['order'][:store['index']+1])
        store['schema']=2


def actor_pending(state, actor):
    for action in state['private'].get('action_workflow',{'actions':{}})['actions'].values():
        if action['status'] in TERMINAL:continue
        if action['actor']==actor or any(c['actor']==actor for c in action['costs']) or (action['status']=='waiting' and action['decision']['actor']==actor):
            return True
    return False


def check_binding(state, timing, actor):
    fields(timing,'encounter turn')
    positive(timing['turn'])
    combat=state['private'].get('combat')
    if not combat or combat['id'] != timing['encounter'] or combat['turn'] != timing['turn'] or combat['phase'] != 'active':
        raise ValueError('Action timing must match the active encounter turn')
    if actor not in combat['order']:
        raise ValueError('Timed action actor must participate in encounter')
    # The actor can differ from the current turn actor for adjudicated reactions.


def pending(state, combat):
    return [aid for aid,a in state['private'].get('action_workflow',{'actions':{}})['actions'].items()
            if a['status'] not in TERMINAL and (a.get('timing') or {}).get('encounter') == combat['id']]


def boundary(state, combat, at, event):
    actor=current_actor(combat)
    combat['counts'][actor][at]+=1
    count=combat['counts'][actor][at]
    for effect in combat['effects'].values():
        expiry=effect['expires']
        if effect['status']=='active' and expiry['actor']==actor and expiry['at']==at and expiry['occurrence']<=count:
            effect.update(status='expired',expired_event=event['id'])
    effects=[]
    for rule in combat['refresh']:
        if rule['actor']==actor and rule['at']==at:
            current=state['actors'][actor]['resources'][rule['resource']]['value']
            effects.append({'kind':'resource','actor':actor,'resource':rule['resource'],'delta':rule['value']-current})
    return effects


def transition(state,change,event):
    fields(change,'kind step data')
    step,data=change['step'],change['data']
    combat=state['private'].get('combat')
    effects=[]
    if step=='start':
        fields(data,'id audience order refresh')
        if combat and combat['phase']!='finished':
            raise ValueError('Finish the current encounter first')
        if combat and data['id'] in [combat['id'],*combat['past_ids']]:
            raise ValueError('A new encounter needs a different ID')
        # Validate types before deriving counters from the declared order.
        if not isinstance(data['order'],list) or any(not isinstance(a,str) for a in data['order']):
            raise ValueError('Order must be actor IDs')
        past_ids=[*combat['past_ids'],combat['id']] if combat else []
        combat=dict(copy.deepcopy(data),past_ids=past_ids,schema=2,profile=copy.deepcopy(event['profile']),
                    round=1,index=0,turn=1,phase='active',effects={},history=[],
                    current=data['order'][0] if data['order'] else None,round_used=data['order'][:1],
                    counts={a:{'start':0,'end':0} for a in data['order']})
        validate_store(combat,state)
        state['private']['combat']=combat
        effects=boundary(state,combat,'start',event)
    else:
        if not combat or combat['phase']=='finished':
            raise ValueError('No running encounter')
        validate_store(combat,state)
        upgrade(combat)
        if step=='end_turn':
            fields(data,'')
            if combat['phase']!='active': raise ValueError('Turn already ended')
            if pending(state,combat): raise ValueError('Resolve or cancel timed actions before ending the turn')
            effects=boundary(state,combat,'end',event)
            combat['phase']='ended'
        elif step=='next_turn':
            fields(data,'')
            if combat['phase']!='ended': raise ValueError('End the current turn first')
            remaining=[a for a in combat['order'] if a not in combat['round_used']]
            if not remaining:
                combat['round']+=1
                combat['round_used']=[]
                remaining=list(combat['order'])
            combat['current']=remaining[0]
            combat['index']=combat['order'].index(combat['current'])
            combat['round_used'].append(combat['current'])
            combat['turn']+=1
            combat['phase']='active'
            effects=boundary(state,combat,'start',event)
        elif step=='join':
            fields(data,'actor position participation refresh reason')
            text(data['reason']);actor=text(data['actor'])
            if actor not in state['actors'] or actor in combat['order']:
                raise ValueError('Join requires an existing actor outside the current order')
            if type(data['position']) is not int or not 0<=data['position']<=len(combat['order']):
                raise ValueError('Join position outside order')
            if data['participation'] not in {'this-round','next-round'} or not isinstance(data['refresh'],list):
                raise ValueError('Explicit round participation and refresh list required')
            if actor_pending(state,actor):raise ValueError('Resolve actor pending actions before joining')
            if any(not isinstance(r,dict) or r.get('actor')!=actor for r in data['refresh']):
                raise ValueError('Join refresh rules must belong to the joining actor')
            combat['order'].insert(data['position'],actor)
            combat['counts'].setdefault(actor,{'start':0,'end':0})
            # Returning actors keep counters and cannot gain a second turn this round.
            if data['participation']=='next-round' and actor not in combat['round_used']:
                combat['round_used'].append(actor)
            combat['refresh']=[r for r in combat['refresh'] if r['actor']!=actor]+copy.deepcopy(data['refresh'])
            combat['index']=combat['order'].index(combat['current']) if combat['current'] in combat['order'] else -1
        elif step=='leave':
            fields(data,'actor reason')
            text(data['reason']);actor=text(data['actor'])
            if actor not in combat['order']:raise ValueError('Actor is not in the order')
            if len(combat['order'])==1:raise ValueError('Use finish for the last participant')
            if actor==current_actor(combat) and combat['phase']=='active':
                raise ValueError('End the active turn before removing its actor')
            if actor_pending(state,actor):raise ValueError('Resolve actor pending actions before leaving')
            if any(e['status']=='active' and (actor in e['targets'] or actor==e['expires']['actor']) for e in combat['effects'].values()):
                raise ValueError('Explicitly remove or retime dependent effects before leaving')
            combat['order'].remove(actor)
            combat['refresh']=[r for r in combat['refresh'] if r['actor']!=actor]
            combat['index']=combat['order'].index(combat['current']) if combat['current'] in combat['order'] else -1
        elif step=='reorder':
            fields(data,'order reason');text(data['reason'])
            order=data['order']
            if not isinstance(order,list) or any(not isinstance(a,str) for a in order) or len(order)!=len(combat['order']) or set(order)!=set(combat['order']):
                raise ValueError('Reorder must contain each active participant exactly once')
            combat['order']=list(order)
            combat['index']=order.index(combat['current']) if combat['current'] in order else -1
        elif step=='retime_effect':
            fields(data,'id expires reason');text(data['reason'])
            effect=combat['effects'][data['id']]
            if effect['status']!='active':raise ValueError('Effect is not active')
            expires=data['expires'];fields(expires,'actor at occurrence');positive(expires['occurrence'])
            if expires['actor'] not in combat['order'] or expires['at'] not in {'start','end'}:
                raise ValueError('Expiry actor must participate')
            if expires['occurrence']<=combat['counts'][expires['actor']][expires['at']]:
                raise ValueError('Expiry boundary has already passed')
            effect['expires']=copy.deepcopy(expires)
        elif step=='add_effect':
            fields(data,'id label targets audience expires')
            if text(data['id']) in combat['effects']: raise ValueError('Effect ID already exists')
            expires=data['expires']; fields(expires,'actor at occurrence')
            positive(expires['occurrence'])
            if expires['actor'] not in combat['order'] or expires['at'] not in {'start','end'}:
                raise ValueError('Invalid expiry boundary')
            if expires['occurrence']<=combat['counts'][expires['actor']][expires['at']]:
                raise ValueError('Expiry boundary has already passed')
            if not isinstance(data['targets'],list) or any(a not in combat['order'] for a in data['targets']):
                raise ValueError('New effect targets must currently participate')
            combat['effects'][data['id']]={k:copy.deepcopy(data[k]) for k in ('label','targets','audience','expires')}
            combat['effects'][data['id']].update(status='active',sources=copy.deepcopy(event['sources']),
                                               created_event=event['id'],expired_event=None)
        elif step=='remove_effect':
            fields(data,'id reason');text(data['reason'])
            effect=combat['effects'][data['id']]
            if effect['status']!='active':raise ValueError('Effect is not active')
            effect.update(status='removed',expired_event=event['id'])
        elif step=='finish':
            fields(data,'reason');text(data['reason'])
            if pending(state,combat):raise ValueError('Resolve pending timed actions before finishing')
            combat['phase']='finished'
            for effect in combat['effects'].values():
                if effect['status']=='active':effect.update(status='expired',expired_event=event['id'])
        else:
            raise ValueError('Unknown combat transition')
    combat['history'].append({'step':step,'event_id':event['id'],'revision':event['revision']+1})
    validate_store(combat,state)
    return effects


def project(combat,state,player=None,gm=False):
    if gm:return copy.deepcopy(combat)
    if not visible(combat['audience'],player):return None
    order=[a for a in combat['order'] if visible(state['actors'][a]['audience'],player)]
    active=current_actor(combat)
    # Do not expose hidden turn indexes, actor IDs or expiration triggers.
    return {'id':combat['id'],'round':combat['round'],'phase':combat['phase'],
            'current_actor':active if active in order and combat['phase']=='active' else None,
            'order':order,'effects':{eid:{'label':e['label'],'targets':[a for a in e['targets'] if a in order]}
                for eid,e in combat['effects'].items() if e['status']=='active' and visible(e['audience'],player)}}


def main():
    import session
    from dice_local import save_private_output
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database',type=Path)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('apply').add_argument('--event',type=Path,required=True)
    v=sub.add_parser('view');v.add_argument('--player');v.add_argument('--private-output',type=Path)
    args=parser.parse_args()
    try:
        if args.command=='apply':
            event=json.loads(args.event.read_text(encoding='utf-8-sig'))
            changes=event.get('changes') if isinstance(event,dict) else None
            if not isinstance(changes,list) or len(changes)!=1 or not isinstance(changes[0],dict) or changes[0].get('kind')!='combat':
                raise ValueError('Combat CLI requires exactly one combat transition')
            result=session.apply(args.database,event)
        else:
            saved=session.view(args.database,gm=True);state=saved['state'];combat=state['private'].get('combat')
            if args.private_output and args.player:raise ValueError('Choose player or private GM output')
            result={'revision':saved['revision'],'combat':project(combat,state,args.player,bool(args.private_output)) if combat else None}
            if args.private_output:
                save_private_output(args.private_output,result)
                result={'revision':saved['revision'],'private_result_saved':True}
        print(session.encode(result))
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as exc:
        print(session.encode({'error':str(exc)}),file=sys.stderr);raise SystemExit(2)


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    main()
