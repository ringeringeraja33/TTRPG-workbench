"""Recoverable local actions inside the campaign ledger transaction.

Trusted operator interface, not user authentication. Rule legality remains an
explicit adjudication. Evidence and internal choices are GM-only by default.
"""
import argparse
import copy
import json
from pathlib import Path
import sqlite3
import sys
from vendor.dice_rd import Expression, roll

STORE = 'action_workflow'
TERMINAL = {'settled', 'cancelled'}
EFFECTS = {'resource', 'resize', 'conditions', 'fact', 'clock', 'combat_effect', 'investigation_effect', 'exploration_effect'}


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 20000:
        raise ValueError('Nonempty bounded text required')
    return value


def fields(value, names):
    if not isinstance(value, dict) or set(value) != set(names.split()):
        raise ValueError('Invalid action fields; expected: ' + names)


def validate_store(store):
    fields(store, 'schema actions')
    if type(store['schema']) is not int or store['schema'] != 1 or not isinstance(store['actions'], dict):
        raise ValueError('Unsupported action workflow schema')
    for aid, action in store['actions'].items():
        text(aid)
        if not isinstance(action, dict) or action.get('status') not in {'declared','rolled','waiting','ready',*TERMINAL}:
            raise ValueError('Invalid saved action')
        required = {'actor','summary','intent','method','stakes','audience','roll','costs',
                    'status','evidence','decision','outcome','decisions','sources','profile','history'}
        if not required <= set(action):
            raise ValueError('Incomplete saved action')
        for key in ('actor','summary','intent','method','stakes'): text(action[key])
        if not isinstance(action['audience'],list) or any(not isinstance(x,str) or not x for x in action['audience']):
            raise ValueError('Invalid action audience')
        if not isinstance(action['history'],list) or not action['history'] or not isinstance(action['decisions'],list):
            raise ValueError('Invalid action history')
        if not isinstance(action['sources'],list) or not action['sources'] or any(not isinstance(x,str) or not x.strip() for x in action['sources']):
            raise ValueError('Invalid action sources')
        if 'reserved' in action and type(action['reserved']) is not bool:
            raise ValueError('Reservation marker must be boolean')
        validate_roll(action['roll'])
        if not isinstance(action['costs'],list) or not isinstance(action['profile'],dict):
            raise ValueError('Invalid action costs/profile')
        if action['evidence'] is not None and (not isinstance(action['evidence'],dict) or action['evidence'].get('origin') not in {'tool','manual','dice-local'}):
            raise ValueError('Invalid action evidence')
        for decision in action['decisions'] + ([action['decision']] if action['decision'] is not None else []):
            fields(decision, 'actor prompt options selected')
            text(decision['actor']); text(decision['prompt'])
            if not isinstance(decision['options'],dict) or not decision['options']:
                raise ValueError('Invalid stored decision options')
        if action['status'] == 'waiting' and action['decision'] is None:
            raise ValueError('Waiting action requires a decision')
        if action['status'] == 'settled' and not {'resolution','applied_effects','settlement_event','settlement_sources'} <= set(action):
            raise ValueError('Settlement receipt missing')


def check_costs(state, costs, exclude=None):
    if not isinstance(costs, list):
        raise ValueError('Costs must be a list')
    totals = {}
    for cost in costs:
        fields(cost, 'kind actor resource delta')
        if cost['kind'] != 'resource' or type(cost['delta']) is not int or cost['delta'] >= 0:
            raise ValueError('Declared costs must be negative resource deltas')
        key = (text(cost['actor']), text(cost['resource']))
        totals[key] = totals.get(key, 0) + cost['delta']
    held = reservations(state, exclude)
    for (actor, resource), delta in totals.items():
        if state['actors'][actor]['resources'][resource]['value'] - held.get((actor,resource),0) + delta < 0:
            raise ValueError('Insufficient resource for declared cost')


def reservations(state, exclude=None):
    totals = {}
    for aid, action in state['private'].get(STORE, {'actions':{}})['actions'].items():
        if aid == exclude or action['status'] in TERMINAL or not action.get('reserved', False):
            continue
        for cost in action['costs']:
            fields(cost, 'kind actor resource delta')
            if cost['kind'] != 'resource' or type(cost['delta']) is not int or cost['delta'] >= 0:
                raise ValueError('Invalid reserved cost')
            key = (cost['actor'],cost['resource'])
            totals[key] = totals.get(key,0) - cost['delta']
    return totals


def validate_reservations(state):
    for (actor, resource), amount in reservations(state).items():
        if state['actors'][actor]['resources'][resource]['value'] < amount:
            raise ValueError('Resource change conflicts with a pending reservation; explicitly release or settle it first')


def availability(state, player=None, gm=False):
    held = reservations(state)
    return [{'actor':actor,'resource':key,'current':value['value'],
             'reserved':held.get((actor,key),0), 'available':value['value']-held.get((actor,key),0)}
            for actor,record in state['actors'].items() if gm or actor == player
            for key,value in record['resources'].items()]


def validate_roll(spec):
    if spec is None:
        return
    if not isinstance(spec, dict):
        raise ValueError('Roll must be null or a specification')
    mode = spec.get('mode')
    fields(spec, 'mode expression source' if mode == 'receipt' else 'mode expression')
    if mode not in {'tool', 'manual', 'receipt'}:
        raise ValueError('Roll mode must be tool, manual or receipt')
    expression = text(spec['expression'])
    # One bounded expression, explicitly bound before any randomness is consumed.
    parsed = Expression(expression)
    if mode == 'receipt':
        if any(token == 'd' or (token[:-1].isdigit() and token.endswith('d')) for token in parsed.tokens):
            raise ValueError('Imported rolls require explicit die sizes')
        fields(spec['source'], 'database scope actor operation')
        for value in spec['source'].values(): text(value)
        if not Path(spec['source']['database']).is_absolute():
            raise ValueError('Dice receipt database must be an absolute path')


def imported_receipt(spec):
    from dice_commands import parse_command
    from session import digest
    source = spec['source']
    path = Path(source['database']).resolve(strict=True)
    db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    try:
        row = db.execute('SELECT request,response FROM requests WHERE scope=? AND operation=?',
                         (source['scope'], source['operation'])).fetchone()
    finally:
        db.close()
    if row is None:
        raise ValueError('Dice operation is not committed yet')
    request, response = json.loads(row[0]), json.loads(row[1])
    command = parse_command(request[1])
    if request[0] != source['actor'] or response['operation'] != source['operation']:
        raise ValueError('Dice receipt identity mismatch')
    if command.head not in {'r','rh'}:
        raise ValueError('Bridge accepts raw .r/.rh receipts only; resource-changing commands cannot be imported')
    evidence = response['result']
    if evidence.get('expression') != spec['expression'] or len(evidence.get('results', [])) != 1:
        raise ValueError('Dice expression does not match the declared action')
    return {'origin':'dice-local', 'source':copy.deepcopy(source),
            'request_sha256':digest(request), 'response_sha256':digest(response),
            'audience':copy.deepcopy(response['audience']), 'roll':copy.deepcopy(evidence)}


def transition(state, change, event):
    """Called only while session.apply holds BEGIN IMMEDIATE; returns effects."""
    from session import audience
    fields(change, 'kind action step data')
    aid, step, data = text(change['action']), change['step'], change['data']
    store = state['private'].setdefault(STORE, {'schema':1, 'actions':{}})
    validate_store(store)
    actions = store['actions']
    if step == 'declare':
        declaration = dict(data) if isinstance(data,dict) else data
        timing = declaration.pop('timing',None) if isinstance(declaration,dict) else None
        stat_ref = declaration.pop('stat_ref',None) if isinstance(declaration,dict) else None
        fields(declaration, 'actor summary intent method stakes audience roll costs')
        stat_snapshot=None
        if stat_ref is not None:
            fields(stat_ref,'actor stat')
            if stat_ref['actor']!=data['actor']:raise ValueError('Action stat must belong to its actor')
            from characters import resolve_stat
            stat_snapshot=resolve_stat(state,stat_ref['actor'],stat_ref['stat'])
        if timing is not None:
            from combat import check_binding
            check_binding(state, timing, data['actor'])
        if aid in actions:
            raise ValueError('Action ID already exists')
        if data['actor'] not in state['actors']:
            raise ValueError('Action actor must exist in this campaign')
        for key in ('summary','intent','method','stakes'): text(data[key])
        audience(data['audience'])
        validate_roll(data['roll'])
        check_costs(state, data['costs'])
        if data['roll'] and data['roll']['mode'] == 'receipt':
            source = data['roll']['source']
            identity = (str(Path(source['database']).resolve()), source['scope'], source['operation'])
            for prior in actions.values():
                old = prior['roll']
                if old and old['mode'] == 'receipt':
                    other = old['source']
                    if identity == (str(Path(other['database']).resolve()), other['scope'], other['operation']):
                        raise ValueError('Dice operation already bound to another action')
        actions[aid] = dict(copy.deepcopy(data), status='declared', evidence=None, decision=None,
                           outcome=None, decisions=[], reserved=True, sources=copy.deepcopy(event['sources']), profile=copy.deepcopy(event['profile']),
                           history=[{'step':step,'event_id':event['id'],'revision':event['revision']+1}])
        if stat_snapshot is not None:actions[aid]['stat_snapshot']=stat_snapshot
        return []
    if aid not in actions:
        raise ValueError('Unknown action')
    action = actions[aid]
    if action['profile'] != state['profile']:
        raise ValueError('Action rules profile conflict')
    if action['status'] in TERMINAL:
        raise ValueError('Action already finished; repeat the original event ID for an idempotent retry')
    effects = []
    if step == 'roll':
        if action['status'] != 'declared' or action['roll'] is None:
            raise ValueError('Action is not waiting for a roll')
        check_costs(state, action['costs'], exclude=aid)
        spec = action['roll']
        if spec['mode'] == 'manual':
            fields(data, 'total note')
            if type(data['total']) is not int or abs(data['total']) > 10**12:
                raise ValueError('Manual total must be a bounded integer')
            text(data['note'])
            evidence = {'origin':'manual', 'expression':spec['expression'],
                        'total':data['total'], 'note':data['note'], 'verified_randomness':False}
        else:
            fields(data, '')
            evidence = (imported_receipt(spec) if spec['mode'] == 'receipt'
                        else {'origin':'tool', 'roll':roll(spec['expression'])})
        if evidence['origin'] == 'dice-local':
            roll_id = evidence['roll']['event_id']
            if any(a.get('evidence') and a['evidence'].get('roll',{}).get('event_id') == roll_id for a in actions.values()):
                raise ValueError('Dice evidence already used by another action')
        action.update(status='rolled', evidence=evidence)
    elif step == 'wait':
        fields(data, 'actor prompt options')
        if action['status'] not in {'rolled','ready'} and not (action['status']=='declared' and action['roll'] is None):
            raise ValueError('Resolve the declared roll before requesting a choice')
        if data['actor'] not in state['actors']:
            raise ValueError('Decision actor must exist')
        if data['actor'] not in action['audience'] and 'all' not in action['audience']:
            raise ValueError('Decision actor must be in the action audience')
        text(data['prompt'])
        if not isinstance(data['options'], dict) or not 1 <= len(data['options']) <= 20:
            raise ValueError('Supply 1..20 explicitly adjudicated options')
        for key, label in data['options'].items(): text(key); text(label)
        action.update(status='waiting', decision=dict(copy.deepcopy(data), selected=None))
    elif step == 'choose':
        fields(data, 'actor option')
        if action['status'] != 'waiting' or data['actor'] != action['decision']['actor']:
            raise ValueError('Not the pending decision actor')
        if data['option'] not in action['decision']['options']:
            raise ValueError('Unknown decision option')
        action['decision']['selected'] = data['option']
        action['decisions'].append(copy.deepcopy(action['decision']))
        action['status'] = 'ready'
    elif step == 'settle':
        fields(data, 'outcome effects')
        if action['status'] not in {'rolled','ready'} and not (action['status']=='declared' and action['roll'] is None):
            raise ValueError('Action has an unresolved roll or choice')
        if data['outcome'] not in {'success','failure','mixed','no-check'}:
            raise ValueError('Explicit outcome required')
        if not isinstance(data['effects'], list) or any(not isinstance(c,dict) or c.get('kind') not in EFFECTS for c in data['effects']):
            raise ValueError('Settlement permits resource, resize, conditions, fact, clock, combat_effect and investigation_effect operations only')
        check_costs(state, action['costs'], exclude=aid)
        effects = copy.deepcopy(action['costs'] + data['effects'])
        action.update(status='settled', reserved=False, outcome=data['outcome'], resolution=event['resolution'],
                      applied_effects=copy.deepcopy(effects), settlement_event=event['id'],
                      settlement_sources=copy.deepcopy(event['sources']))
    elif step in {'reserve','release'}:
        fields(data, 'reason')
        text(data['reason'])
        if step == 'reserve': check_costs(state, action['costs'], exclude=aid)
        action['reserved'] = step == 'reserve'
        action.setdefault('reservation_history',[]).append({'step':step,'reason':data['reason'],'event_id':event['id']})
    elif step == 'cancel':
        fields(data, 'reason')
        if action['evidence'] is not None:
            raise ValueError('A rolled attempt must be settled, not cancelled to avoid its costs')
        text(data['reason'])
        action.update(status='cancelled', reserved=False, cancellation=data['reason'])
    else:
        raise ValueError('Unknown action step')
    action['history'].append({'step':step,'event_id':event['id'],'revision':event['revision']+1})
    return effects


def project(store, player=None, gm=False):
    validate_store(store)
    result = {}
    for aid, action in store['actions'].items():
        if gm:
            result[aid] = copy.deepcopy(action)
        elif 'all' in action['audience'] or player is not None and player in action['audience']:
            # Evidence, stakes, internal methods and history are never auto-published.
            item = {k:copy.deepcopy(action[k]) for k in ('summary','status')}
            if action['status'] == 'waiting' and player == action['decision']['actor']:
                item['decision'] = {k:copy.deepcopy(action['decision'][k]) for k in ('prompt','options')}
            result[aid] = item
    return result


def view(path, player=None, gm=False):
    from session import view as session_view
    saved = session_view(path, gm=True)
    store = saved['state']['private'].get(STORE, {'schema':1,'actions':{}})
    return {'revision':saved['revision'], 'actions':project(store, player, gm),
            'resource_availability':availability(saved['state'],player,gm)}


def main():
    from session import apply, encode
    from dice_local import save_private_output
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('apply').add_argument('--event', required=True, type=Path)
    v = sub.add_parser('view')
    v.add_argument('--player')
    v.add_argument('--private-output', type=Path, help='Save full GM action state privately; stdout contains only revision')
    args = parser.parse_args()
    try:
        if args.command == 'apply':
            event = json.loads(args.event.read_text(encoding='utf-8-sig'))
            if not isinstance(event,dict) or not isinstance(event.get('changes'),list) or len(event['changes']) != 1 or not isinstance(event['changes'][0],dict) or event['changes'][0].get('kind') != 'action':
                raise ValueError('Action CLI requires exactly one action transition')
            result = apply(args.database, event)
        elif args.private_output:
            if args.player:
                raise ValueError('Choose a player view or a full private GM output')
            result = view(args.database, gm=True)
            if args.private_output.resolve() == args.database.resolve():
                raise ValueError('Private output must not replace the database')
            save_private_output(args.private_output, result)
            result = {'revision':result['revision'], 'private_result_saved':True}
        else:
            result = view(args.database, player=args.player)
        print(encode(result))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        print(encode({'error':str(exc)}), file=sys.stderr)
        raise SystemExit(2)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
