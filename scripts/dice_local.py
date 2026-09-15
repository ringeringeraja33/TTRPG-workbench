"""Local Dice! adaptation and Tower-inspired table services (AGPL-3.0-or-later).

Trusted local operator interface; actor IDs are not authentication credentials.
No network, QQ connection, cloud federation, outgoing messages or auto-update.
"""
import argparse
import copy
import difflib
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import secrets
import sqlite3
import sys
import time
import zipfile
from vendor.dice_rd import Expression, roll, pool
from dicebot import key, NAME, dispatch as legacy_dispatch
from rules_math import coc_result, coc_development, coc_sanity
from dice_services import validate_decks, draw_deck, actor_timers


def fresh():
    return dict(revision=0, gm=None, players={}, npcs={}, monsters={}, team={}, initiative={},
                clues={}, logs={}, active_log=None, observers=[], default_die=100,
                house_range=5, config={}, decks={}, custom={}, scenes={}, replies={}, clocks={})


def read(path, scope):
    if not Path(path).exists(): return fresh()
    db=sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        row = db.execute('SELECT state FROM tables WHERE scope=?', (scope,)).fetchone()
    finally: db.close()
    return json.loads(row[0]) if row else fresh()


def player(state, actor):
    return state['players'].setdefault(actor, {'active': None, 'cards': {}})


def card(state, actor, name=None):
    p = player(state, actor)
    name = name or p['active']
    if name in p['cards']: return p['cards'][name]
    if actor == state['gm']:
        for store in ('monsters', 'npcs'):
            if name in state[store]: return state[store][name]
    raise ValueError('Unknown card for this actor; select or register it first')


def require_gm(state, actor):
    if state['gm'] != actor: raise ValueError('Local Keeper role required')


def number(expression, default=100):
    event = roll(expression, default)
    if len(event['results']) != 1: raise ValueError('One result required')
    value = event['results'][0]['total']
    if type(value) is not int: raise ValueError('An integer result is required for stored stats')
    return value, event


def update_stats(target, text):
    pattern = re.compile(r'(' + NAME + r')\s*([=+-]?)\s*(\d+(?:[dD]\d+)?(?:\*\d+)?)')
    pos, edits, seen = 0, [], set()
    while pos < len(text):
        if text[pos] in ' ,，;；': pos += 1; continue
        m = pattern.match(text, pos)
        if not m: raise ValueError('Use stat50, stat=50, stat+1d3 or stat-1d3')
        name, op, expr = key(m[1]), m[2], m[3]
        if name in seen: raise ValueError('Duplicate canonical stat in batch')
        if op in ('+', '-') and name not in target['stats']: raise ValueError('Missing stat for adjustment')
        Expression(expr)
        edits.append((name, op, expr)); seen.add(name); pos = m.end()
    if not edits: raise ValueError('No assignments')
    result, evidence = dict(target['stats']), []
    for name, op, expr in edits:
        value, event = number(expr)
        before = result.get(name)
        value = before + (value if op == '+' else -value) if op in ('+', '-') else value
        if not 0 <= value <= 999: raise ValueError('Stored numeric value outside0..999; no clamping')
        result[name] = value
        evidence.append(dict(stat=name, before=before, after=value, roll=event))
    target['stats'] = result
    return {'stats': result, 'changes': evidence, 'legality': 'not audited'}


def check(state, actor, text, house=False, extra=None):
    target_card = None
    if ':' in text:
        cname, text = text.split(':', 1); target_card = card(state, actor, cname.strip())
    match = re.fullmatch(r'(' + NAME + r')(?:\s+(\d+))?\s*([+*/-]\s*\d+)?', text)
    if match:
        stat = key(match[1])
        target_card = target_card or card(state, actor)
        # This adapter requires explicit edits rather than silently ignoring an explicit threshold.
        target = int(match[2]) if match[2] else target_card['stats'].get(stat)
        if target is None: raise ValueError('Stat not recorded')
        target = number(str(target) + (match[3] or ''))[0]
    else:
        stat, target = None, number(text)[0]
    if not 1 <= target <= 100: raise ValueError('Check target must be1..100')
    event = roll(extra or 'd100')
    total = event['results'][0]['total']
    outcome = coc_result(target, total)
    if house:
        n = state['house_range']
        if total <= n: outcome = 'critical'
        elif total >= 101 - n: outcome = 'fumble'
    if stat and target_card and not extra and outcome not in ('failure', 'fumble') and state['active_log'] and actor in state['team']:
        if stat not in ('STR','CON','SIZ','DEX','APP','INT','POW','EDU','LUCK','SAN','HP','MP'):
            marks = target_card.setdefault('development_candidates', [])
            if stat not in marks: marks.append(stat)
    return dict(stat=stat, target=target, outcome=outcome, roll=event,
                profile='tower-house' if house else 'coc7-core', effects_applied=False)


def sanity(target, expression):
    if target.get('in_bout'):
        return {'before':target['stats'].get('SAN'),'after':target['stats'].get('SAN'),
                'loss':0,'reason':'Active bout: no additional SAN loss; no dice rolled'}
    parts = expression.split('/')
    if len(parts) != 2: raise ValueError('Use success-loss/failure-loss')
    for part in parts:
        if not re.fullmatch(r'\d+(?:d\d+)?(?:[+]\d+)?', part, re.I):
            raise ValueError('SAN loss supports nonnegative integer or NdS[+integer]; use stc SAN+N for recovery')
        Expression(part)
    before = target['stats'].get('SAN')
    if before is None or not 0 <= before <= 99: raise ValueError('Record SAN0..99 first')
    result = roll('d100'); die = result['results'][0]['total']
    outcome = coc_result(before, die)
    chosen = parts[0] if die <= before else parts[1]
    if outcome == 'fumble':
        loss_result = Expression(chosen).evaluate(maximum=True)
        loss_result['mode'] = 'maximum loss on fumble; not a random roll'
        loss = loss_result['total']
    else: loss, loss_result = number(chosen)
    day = target.setdefault('sanity_day', {'start': before, 'loss': 0})
    if day['start']==0: raise ValueError('Zero SAN requires permanent-insanity resolution')
    calculation=coc_sanity(before,day['start'],day['loss'],loss)
    after=calculation['san']; day['loss']=calculation['day_loss']
    target['stats']['SAN'] = after
    return dict(before=before, after=after, loss=loss, check=result, outcome=outcome, loss_roll=loss_result,
                int_check_required=calculation['int_required'], indefinite_threshold_reached=calculation['indefinite'],
                permanent=after == 0, next='Resolve applicable bout/INT rules with the Keeper; no automatic symptom or control transfer')


def visible_log(state, actor, name):
    if name not in state['logs']: raise ValueError('Unknown log')
    return [x for x in state['logs'][name] if x['audience'] == 'table' or actor in x['audience']]


def dispatch(state, actor, command):
    p = player(state, actor)
    command = command.strip()
    if command and command[0] in '。!！': command = '.' + command[1:]
    if command == '.kp':
        if state['gm'] not in (None, actor): raise ValueError('Keeper already assigned')
        state['gm'] = actor; return {'keeper': actor}
    if command == '.help':
        return {'reference': 'references/dice-local.md', 'engine': 'Dice! RD Python adaptation', 'network': False}
    if command == '.join' or command.startswith('.join '):
        name = command[5:].strip() or actor
        if len(name) > 100: raise ValueError('Display name exceeds100 characters')
        already = p.get('present', False)
        p.update(present=True, display_name=name)
        result = {'joined': actor, 'display_name': name, 'already_present': already, 'external_delivery': False}
        if not already and state['config'].get('welcome_enabled'):
            result['welcome'] = state['config'].get('welcome', '').replace('{name}', name).replace('{actor}', actor)
        return result
    if command == '.leave':
        p['present'] = False
        return {'left': actor, 'cards_preserved': True, 'external_delivery': False}
    if command=='.hiy': return {'history':copy.deepcopy(p.get('check_history',[]))}
    if command in ('.algo get', '.admin state'):
        return {'algorithm': 'OS secrets; independent draws', 'revision': state['revision'], 'default_die': state['default_die'], 'cloud': False}
    if command.startswith('.algo set'): raise ValueError('Historical Tower algorithms unavailable; OS RNG cannot be changed')
    if command.startswith('.set') and not command.startswith('.setcoc'):
        require_gm(state, actor); value = int(command[4:].strip())
        if not 2 <= value <= 1000: raise ValueError('Default faces2..1000')
        state['default_die'] = value; return {'default_die': value}
    if command == '.crule get': return {'house_range': state['house_range']}
    if command.startswith('.crule set '):
        require_gm(state, actor); n = int(command[11:])
        if not 1 <= n <= 5: raise ValueError('House range1..5')
        state['house_range'] = n; return {'house_range': n}
    m=re.fullmatch(r'\.(ral|rcl)\s*(\d+)\s+(\d+)',command)
    if m:
        kind,threshold,count=m.groups(); count=int(count)
        if not 1<=count<=100: raise ValueError('Check count1..100')
        return {'checks':[check(state,actor,threshold,house=kind=='ral') for _ in range(count)]}
    m=re.fullmatch(r'\.(rav|rcv)\s+(.+)',command)
    if m:
        kind,text=m.groups(); pending=state.get('opposed_pending')
        if pending and pending['kind']!=kind: raise ValueError('Pending opposition uses a different profile')
        current=check(state,actor,text,house=kind=='rav')
        if not pending:
            state['opposed_pending']={'actor':actor,'kind':kind,'check':current}
            return {'pending':True,'first':current}
        if pending['actor']==actor: raise ValueError('Second side requires another actor; use ordinary checks for Keeper NPCs')
        ranks={'fumble':0,'failure':1,'regular':2,'hard':3,'extreme':4,'critical':5}
        left,right=pending['check'],current
        # General CoC opposition only: successful rank, then skill; combat needs its own procedure.
        a=(ranks[left['outcome']],left['target']); b=(ranks[right['outcome']],right['target'])
        winner=None if max(a[0],b[0])<2 or a==b else pending['actor'] if a>b else actor
        state['opposed_pending']=None
        return {'first':left,'second':right,'winner':winner,'tie_or_both_failed':winner is None,
                'rule':'General opposition only; equal rank compares skill. Combat dodge/fight-back excluded; Tower roll-value tie-break not adopted.'}
    if command=='.opposed cancel':
        require_gm(state,actor); state['opposed_pending']=None; return {'cancelled':True}
    if command.startswith('.coc'):
        if not re.fullmatch(r'\.coc(?:\d*| show b\d+| take b\d+ \d+ [A-Za-z0-9_-]+ .+)', command):
            raise ValueError('Use local .coc / .coc5 / .coc show bN / .coc take bN index id name; not Tower edition syntax')
        shell = dict(revision=state['revision'], cards=p['cards'], active=p['active'], chargen_batches=p.setdefault('chargen_batches', {}))
        result = legacy_dispatch(shell, command)
        p['active'] = shell['active']; return result
    if command.startswith('.card '):
        shell = dict(revision=state['revision'], cards=p['cards'], active=p['active'])
        result = legacy_dispatch(shell, command); p['active'] = shell['active']; return result
    if command.startswith('.dnd'):
        n = int(command[4:].strip() or 1)
        if not 1 <= n <= 10: raise ValueError('Candidate count1..10')
        return {'method': 'Six unassigned 4d6 keep-highest3 scores; edition and table permission required',
                'candidates': [roll('6#4d6k3') for _ in range(n)]}
    if command.startswith('.name'):
        text=command[5:].strip() or 'en'; parts=text.split()
        count=int(parts[0]) if parts[0].isdigit() else 1
        locale=parts[1] if len(parts)>1 else 'en' if parts[0].isdigit() else parts[0]
        banks={'en':['Ada Bell','Edwin Marsh','Clara Finch','Martha Reed','Henry Vale'],
               'ch':['林舟','陈秋','周岚','顾宁','沈安'], 'jp':['森直人','木村葵','佐藤遥','小川光','山田春']}
        if locale not in banks or not 1<=count<=100: raise ValueError('Use .name [count] [en/ch/jp]')
        return {'names':[secrets.choice(banks[locale]) for _ in range(count)],'note':'Small original fictional name bank; not historical-name research'}
    if command.startswith('.lookup import '):
        require_gm(state,actor); profile,raw=command[15:].split(' ',1); data=json.loads(raw)
        if not isinstance(data,dict) or set(data)!={'source','entries'} or not isinstance(data['source'],str) or not data['source'].strip(): raise ValueError('Supply source and entries fields with bibliographic attribution')
        if not isinstance(data['entries'],dict) or len(data['entries'])>1000 or not all(isinstance(k,str) and isinstance(v,str) and len(v)<=20000 for k,v in data['entries'].items()): raise ValueError('Bounded string entries required')
        state.setdefault('lookups',{})[profile]=data; return {'profile':profile,'entries':len(data['entries']),'network':False}
    m=re.fullmatch(r'\.(magic5e|magic3r|3ry|5ey|rule|dw|pfy)\s+(.+)',command)
    if m:
        kind,query=m.groups(); profile={'magic5e':'dnd5e-2014','magic3r':'dnd3r','3ry':'dnd3r','5ey':'dnd5e-2014','rule':'coc7','dw':'deathwatch','pfy':'pf1'}[kind]
        data=state.get('lookups',{}).get(profile)
        if data is None: raise ValueError('No supplied source dataset for '+profile+'; use .lookup import or the skill rule lookup workflow')
        if query not in data['entries']: return {'matches':difflib.get_close_matches(query,data['entries'],n=5),'profile':profile,'source':data['source']}
        return {'text':data['entries'][query],'profile':profile,'source':data['source']}
    if command.startswith('.con '):
        edition,query=command[5:].split(' ',1)
        if edition not in ('5e','3r'): raise ValueError('Explicit historical5e or3r profile required')
        return dispatch(state,actor,('.5ey ' if edition=='5e' else '.3ry ')+query)
    if command.startswith('.getbook '):
        topic=command[9:].strip()
        refs={'card':'https://www.chaosium.com/cthulhu-character-sheets/',
              'make':'references/systems/coc7-procedures.md',
              'kp':'https://www.chaosium.com/call-of-cthulhu-rules/',
              'rp':'references/characters.md'}
        if topic not in refs: raise ValueError('Unknown book topic')
        return {'reference':refs[topic],'note':'Source/procedure pointer only; no licensed full-book or RP360 redistribution'}
    if command in ('.ti','.li','.bg','.gas','.tz'):
        name=command[1:]
        if name not in state['decks']: raise ValueError('Install a source-checked '+name+' deck first; no invented official table')
        result=dispatch(state,actor,'.draw '+name)
        result['note']='Table suggestion only; edition, duration and applicability need separate rule resolution'
        return result
    if command.startswith('.dr '):
        table,_,count=command[4:].partition(' ')
        if table not in 'abcdefghi' or len(table)!=1: raise ValueError('Historical DMG table a..i required')
        return dispatch(state,actor,'.draw dnd5e-dr-'+table+' '+(count or '1'))
    if command in ('.st list',): return {'active': p['active'], 'cards': list(p['cards'])}
    if command.startswith('.nn'):
        name = command[3:].strip()
        if not name: raise ValueError('Provide an explicit character name')
        if name not in p['cards']: p['cards'][name] = {'name': name, 'profile': 'coc7-core', 'stats': {}}
        p['active'] = name; return {'active': name}
    if command in ('.st show', '.st get', '.st'):
        return copy.deepcopy(card(state, actor))
    if command.startswith('.st show'):
        name = key(command[8:].strip()); stats = card(state, actor)['stats']
        if name not in stats: raise ValueError('Missing stat')
        return {'stat': name, 'value': stats[name]}
    if command == '.st export':
        return {'command': '.st ' + ' '.join(k + '=' + str(v) for k,v in card(state,actor)['stats'].items()), 'dialect': 'workbench-local'}
    if command.startswith('.st rm '):
        name = command[7:].strip()
        if name == p['active']: raise ValueError('Select another card before deleting the active card')
        if name not in p['cards']: raise ValueError('Unknown card')
        if any(x == [actor,name] for x in state['team'].values()): raise ValueError('Remove team binding first')
        del p['cards'][name]; return {'removed': name}
    if command == '.st clr':
        name = 'temporary'
        if any(x == [actor,name] for x in state['team'].values()): raise ValueError('Remove temporary card team binding first')
        p['cards'][name] = {'name': name, 'profile': 'coc7-core', 'stats': {}}; p['active']=name
        return {'active': name, 'cleared': True}
    if command in ('.st lock', '.st unlock'):
        return {'scope_isolation': 'Cards and selection are always scoped to this local table; cross-table switching cannot affect them'}
    if command.startswith('.st rename '):
        new = command[11:].strip(); old = p['active']; current = card(state, actor)
        if not new or new in p['cards']: raise ValueError('New unique name required')
        p['cards'][new] = p['cards'].pop(old); current['name']=new; p['active']=new
        for owner, binding in state['team'].items():
            if binding == [actor, old]: state['team'][owner]=[actor,new]
        return {'renamed': new}
    if command.startswith('.st cp '):
        name, recipient = command[7:].rsplit(' ',1); recipient=recipient.lstrip('@')
        recipient_cards=player(state,recipient)['cards']
        if name in recipient_cards: raise ValueError('Recipient already has that card')
        recipient_cards[name]=copy.deepcopy(card(state,actor,name)); return {'copied':name,'recipient':recipient}
    if command.startswith('.stc '): return update_stats(card(state,actor),command[5:])
    if command.startswith('.st') and not command.startswith('.str'):
        text=command[3:].strip()
        if text in p['cards']: p['active']=text; return {'active':text}
        m=re.match(r'^([^=+\-\d]+)-(.*)$',text)
        if m and re.match(NAME+r'\s*\d',m[2]):
            name=m[1].strip()
            if name not in p['cards']: p['cards'][name]={'name':name,'profile':'coc7-core','stats':{}}
            p['active']=name; text=m[2]
        return update_stats(card(state,actor),text)
    if command.startswith('.sn'):
        return {'nickname_preview': command[3:].strip() or card(state,actor)['name'], 'external_change':False}
    m=re.fullmatch(r'\.(ra|rc|rb|rp)\s*(.*)',command)
    if m:
        kind,text=m.groups(); extra=None
        if kind in ('rb','rp'):
            n=1; parts=text.split(maxsplit=1)
            if len(parts)==2 and parts[0].isdigit(): n=int(parts[0]); text=parts[1]
            if not 1 <= n <= 2: raise ValueError('Core CoC extra dice1..2')
            extra=kind[1]+str(n)
            if not text: return roll(extra)
        result=check(state,actor,text,house=kind=='ra',extra=extra)
        p.setdefault('check_history',[]).append(copy.deepcopy(result))
        return result
    if command.startswith('.sc '): return sanity(card(state,actor),command[4:].strip())
    if command=='.san day':
        target=card(state,actor); san=target['stats'].get('SAN')
        if san is None: raise ValueError('Missing SAN')
        target['sanity_day']={'start':san,'loss':0}; return target['sanity_day']
    if command in ('.san bout on','.san bout off'):
        target=card(state,actor); target['in_bout']=command.endswith(' on')
        return {'in_bout':target['in_bout'],'note':'Record the Keeper-resolved bout; this toggle does not establish duration or recovery legality'}
    if command.startswith('.en '):
        stat=key(command[4:].strip()); target=card(state,actor)
        if stat not in target.get('development_approved',[]): raise ValueError('Keeper must approve an eligible development mark first')
        value=target['stats'][stat]; d,event=number('d100'); gain,gain_event=number('d10') if d>value or d>=96 else (0,None)
        new=coc_development(value,d,gain) if gain else value
        target['stats'][stat]=new; target['development_approved'].remove(stat)
        if stat in target.get('development_candidates',[]): target['development_candidates'].remove(stat)
        return {'stat':stat,'before':value,'after':new,'roll':event,'gain_roll':gain_event}
    if command.startswith('.mark '):
        require_gm(state,actor); owner,stat=command[6:].split(maxsplit=1); stat=key(stat)
        target=card(state,owner.lstrip('@'))
        if stat not in target['stats'] or stat in ('STR','CON','SIZ','DEX','APP','INT','POW','EDU','LUCK','SAN','HP','MP'):
            raise ValueError('Mark a recorded skill, not an attribute/resource')
        marks=target.setdefault('development_approved',[])
        if stat not in marks: marks.append(stat)
        return {'approved':stat,'owner':owner}
    if command.startswith('.team'):
        require_gm(state,actor); text=command[5:].strip()
        if not text:
            rows=[]
            for owner,(_,name) in state['team'].items(): rows.append({'owner':owner,'card':name,'stats':card(state,owner,name)['stats']})
            return {'members':sorted(rows,key=lambda x:x['stats'].get('DEX',0),reverse=True)}
        parts=text.split(); action=parts[0]
        if action=='set':
            for who in parts[1:]:
                who=who.lstrip('@'); card(state,who); state['team'][who]=[who,player(state,who)['active']]
        elif action=='rm':
            for who in parts[1:]:
                if who.lstrip('@') not in state['team']: raise ValueError('Unknown team member')
                del state['team'][who.lstrip('@')]
        elif action=='clr': state['team']={}
        elif action in ('lock','rename','call'): return {'bindings':state['team'],'external_change':False,'note':'Stable card bindings; names/mentions are previews only'}
        elif action in ('en','desc'):
            return {who:copy.deepcopy(card(state,who,binding[1]) if action=='desc' else card(state,who,binding[1]).get('development_candidates',[])) for who,binding in state['team'].items()}
        elif action in ('hp','san'):
            if len(parts)<3: raise ValueError('Use .team hp/san all|@ids expression')
            owners=list(state['team']) if parts[1:-1]==['all'] else [x.lstrip('@') for x in parts[1:-1]]
            if not owners or len(set(owners))!=len(owners) or any(x not in state['team'] for x in owners): raise ValueError('Unique existing team members required')
            expr=parts[-1]; targets=[card(state,x,state['team'][x][1]) for x in owners]
            if action=='san' and '/' in expr: return {'members':{who:sanity(c,expr) for who,c in zip(owners,targets)}}
            stat=action.upper(); sign='+' if expr.startswith('+') else '-'; expr=expr.lstrip('+')
            return {'members':{who:update_stats(c,stat+sign+expr) for who,c in zip(owners,targets)}}
        else: raise ValueError('Unsupported team subcommand')
        return {'team':state['team']}
    m=re.fullmatch(r'\.(npc|monster)(?:\s+(.*))?',command)
    if m:
        require_gm(state,actor); kind,text=m.groups(); store=state['npcs' if kind=='npc' else 'monsters']
        if not text: return {'names':list(store)}
        if text=='clr': store.clear(); return {'cleared':kind}
        if text=='get': return copy.deepcopy(store)
        if text=='make' and kind=='npc':
            names=['The night clerk','The retired mechanic','The visiting researcher']
            aims=['recover a missing keepsake','protect a colleague','settle an old debt']
            return {'name':secrets.choice(names),'goal':secrets.choice(aims),
                    'knowledge':'Define from established scenario evidence',
                    'numeric_card':None,'source':'Original brainstorming seed; not a generated legal character'}
        if text.startswith('rm '):
            name=text[3:].strip()
            if name not in store: raise ValueError('Unknown entity')
            del store[name]; return {'removed':name}
        if text.startswith('st'):
            name,stats=text[2:].strip().split('-',1)
            target=store.setdefault(name,{'name':name,'stats':{},'profile':'coc7-core'})
            return update_stats(target,stats)
        raise ValueError('NPC generation requires a supplied template; use st/get/rm/clr')
    if command.startswith('.ri'):
        text=command[3:].strip(); parts=text.split(maxsplit=1)
        expr=parts[0] if parts else '0'; name=parts[1] if len(parts)>1 else actor
        if not re.search(r'\d',expr): name=text; expr='0'
        if 'd' not in expr.lower(): expr='d20'+('' if expr.startswith(('+','-')) else '+')+expr
        if name in state['initiative']: raise ValueError('Initiative exists; use init set or rm explicitly')
        value,event=number(expr); state['initiative'][name]={'value':value,'roll':event,'owner':actor}
        return {'name':name,**state['initiative'][name]}
    if command=='.init': return sorted([{'name':k,**v} for k,v in state['initiative'].items()],key=lambda x:-x['value'])
    if command.startswith('.init '):
        require_gm(state,actor); text=command[6:]
        if text=='clr': state['initiative']={}
        elif text.startswith('rm '):
            if text[3:] not in state['initiative']: raise ValueError('Unknown initiative entry')
            del state['initiative'][text[3:]]
        elif text.startswith('set '):
            name,value=text[4:].rsplit(' ',1)
            state['initiative'][name]={'value':int(value),'owner':actor,'manual':True}
        else: raise ValueError('Invalid initiative command')
        return {'initiative':state['initiative']}
    if command.startswith('.clue'):
        text=command[5:].strip()
        if text=='show': return copy.deepcopy(state['clues'])
        if text=='clr': require_gm(state,actor); state['clues']={}; return {'cleared':True}
        if text.startswith('rm '):
            cid=text[3:]
            if cid not in state['clues']: raise ValueError('Unknown clue ID')
            if state['clues'][cid]['owner']!=actor: require_gm(state,actor)
            del state['clues'][cid]; return {'removed':cid}
        if not text: raise ValueError('Provide clue text')
        cid='c'+str(state['revision']+1); state['clues'][cid]={'text':text,'owner':actor}
        return {'id':cid,**state['clues'][cid]}
    if command.startswith('.log'):
        text=command[4:].strip()
        if text in ('','list'): return {'active':state['active_log'],'logs':list(state['logs'])}
        if text.startswith('get '): return {'name':text[4:],'entries':visible_log(state,actor,text[4:])}
        require_gm(state,actor)
        if text.startswith('on '):
            name=text[3:].strip()
            if not name: raise ValueError('Log name required')
            if state['active_log'] not in (None,name): raise ValueError('Close current log first')
            state['logs'].setdefault(name,[]); state['active_log']=name
        elif text=='off' or text.startswith('off '):
            if text!='off' and text[4:]!=state['active_log']: raise ValueError('Log name does not match active log')
            state['active_log']=None
        elif text.startswith('rm '):
            name=text[3:]
            if name==state['active_log']: raise ValueError('Close log before deletion')
            if name not in state['logs']: raise ValueError('Unknown log')
            del state['logs'][name]
        else: raise ValueError('Unknown log command; cross-table export is not implicit')
        return {'active':state['active_log'],'logs':list(state['logs'])}
    if command.startswith('.des') or command.startswith('.custom') or command.startswith('.reply'):
        prefix=next(x for x in ('.custom','.reply','.des') if command.startswith(x)); text=command[len(prefix):].strip()
        store=state[{'.custom':'custom','.reply':'replies','.des':'scenes'}[prefix]].setdefault(actor,{})
        if prefix == '.reply' and text.startswith(('enable ', 'disable ', 'publish ', 'unpublish ')):
            action, name = text.split(' ', 1)
            rules = state.setdefault('reply_rules', {})
            own = rules.setdefault(actor, {})
            shared = state.setdefault('table_replies', {})
            if action in ('publish', 'unpublish'): require_gm(state, actor)
            if action in ('enable', 'publish') and name not in store: raise ValueError('Save reply text first')
            if action == 'enable': own[name] = True
            elif action == 'disable': own.pop(name, None)
            elif action == 'publish': shared[name] = {'owner': actor, 'text': store[name]}
            else: shared.pop(name, None)
            return {'keyword': name, 'action': action, 'match': 'exact', 'external_delivery': False}
        if text=='list': return {'entries':list(store)}
        if text.startswith(('set ','input ')):
            content=text.split(' ',1)[1]
            name,value=content.split('|',1) if '|' in content else content.split(' ',1)
            if not name.strip() or len(name)>100 or len(value)>5000: raise ValueError('Bounded nonempty key and text required')
            store[name]=value; return {'saved':name,'scope':'actor/table; not uploaded'}
        if text.startswith('rm '):
            if text[3:] not in store: raise ValueError('Unknown entry')
            if prefix == '.reply': state.get('reply_rules', {}).get(actor, {}).pop(text[3:], None)
            del store[text[3:]]; return {'removed':text[3:]}
        if text not in store: raise ValueError('Unknown local entry')
        return {'name':text,'text':store[text]}
    if command.startswith(('.deck','.draw')):
        text=command[5:].strip()
        if text in ('list','help',''): return {'decks':list(state['decks'])}
        if text.startswith('install '):
            require_gm(state,actor); name,raw=text[8:].split(' ',1); entries=json.loads(raw)
            candidate = dict(state['decks']); candidate[name] = entries; validate_decks(candidate)
            state['decks'][name]=entries; return {'installed':name,'source':'user-supplied local data'}
        if text.startswith('remove '):
            require_gm(state,actor)
            if text[7:] not in state['decks']: raise ValueError('Unknown deck')
            candidate = dict(state['decks']); del candidate[text[7:]]; validate_decks(candidate)
            del state['decks'][text[7:]]; return {'removed':text[7:]}
        name,_,n=text.partition(' '); n=int(n or 1)
        return draw_deck(state['decks'], name, n)
    if command=='.jrrp':
        date=datetime.now(timezone.utc).date().isoformat(); values=p.setdefault('jrrp',{})
        if date not in values: values[date]=secrets.randbelow(100)+1
        return {'utc_date':date,'value':values[date],'mechanical_effect':False}
    if command.startswith('.clock'):
        text=command[6:].strip()
        now = time.time()
        if text in ('list', 'poll'):
            return {'clocks': actor_timers(state, actor, now, due_only=text=='poll'),
                    'now': now, 'requires_ack': text=='poll', 'background_notification': False}
        if text.startswith(('ack ', 'cancel ')):
            action, cid = text.split(' ', 1)
            if cid not in state['clocks'] or state['clocks'][cid]['owner'] != actor:
                raise ValueError('Timer belongs to another actor or does not exist')
            clock = state['clocks'][cid]
            if action == 'ack' and (clock['due'] > now or clock.get('status') == 'cancelled'):
                raise ValueError('Only a due, noncancelled timer can be acknowledged')
            clock['status'] = 'acknowledged' if action == 'ack' else 'cancelled'
            return {'id': cid, 'status': clock['status']}
        seconds, _, label = text.partition(' '); seconds=int(seconds)
        if not 1<=seconds<=86400: raise ValueError('Seconds1..86400')
        if len(label)>500: raise ValueError('Timer label exceeds500 characters')
        cid='t'+str(state['revision']+1); state['clocks'][cid]={'owner':actor,'due':now+seconds,'label':label,'status':'pending'}
        return {'id':cid,**state['clocks'][cid],'background_notification':False}
    if command.startswith('.ob'):
        require_gm(state,actor); text=command[3:].strip()
        if text=='list': return {'observers':state['observers']}
        if text=='clr': state['observers']=[]
        elif text.startswith('set '): state['observers']=list(dict.fromkeys(text[4:].split()))
        else: raise ValueError('Keeper explicitly sets local observer IDs with .ob set id1 id2')
        return {'observers':state['observers'],'warning':'Future hidden rolls include these authorized local recipients'}
    if command.startswith('.group '):
        require_gm(state,actor); text=command[7:].strip()
        if text=='info': return {'config':state['config'],'keeper':state['gm'],'members':list(state['players'])}
        name,value=text.split(' ',1)
        if name not in ('simple','secret','jrrp','deck','ob') or value not in ('0','1'): raise ValueError('Local group switches: simple/secret/jrrp/deck/ob0|1')
        setting={'jrrp':'DisabledJrrp','deck':'DisabledDraw'}.get(name,name)
        state['config'][setting]=1-int(value) if name in ('jrrp','deck') else int(value)
        return {'name':name,'value':int(value),'scope':'local table'}
    if command.startswith('.welcome'):
        require_gm(state,actor); text=command[8:].strip()
        if text in ('open','close'): state['config']['welcome_enabled']=text=='open'
        elif text:
            if len(text)>5000: raise ValueError('Welcome template exceeds5000 characters')
            if any(x not in ('name','actor') for x in re.findall(r'\{([^{}]+)\}',text)):
                raise ValueError('Welcome variables: {name}, {actor}')
            state['config']['welcome']=text
        return {'template':state['config'].get('welcome',''),'enabled':state['config'].get('welcome_enabled',False),'trigger':'local .join event','automatic_delivery':False}
    if command.startswith('.notice '):
        require_gm(state,actor); text=command[8:]; store=state.setdefault('notices',{})
        if text=='show': return copy.deepcopy(store)
        if text.startswith('input '):
            title,body=text[6:].split('|',1)
            if title in store: raise ValueError('Notice title already exists')
            store[title]={'body':body,'status':'pending','author':actor}
            return {'title':title,**store[title],'published':False}
        action,title=text.split(' ',1)
        if action not in ('agree','refuse') or title not in store: raise ValueError('Unknown notice/action')
        store[title]['status']='approved' if action=='agree' else 'rejected'
        return {'title':title,**store[title],'published':False,'note':'Local Keeper review only; no multi-admin approval or QQ publication'}
    if command.startswith('.admin '):
        require_gm(state,actor); text=command[7:].strip()
        if '=' not in text: return {'name':text,'value':state['config'].get(text),'scope':'local table'}
        name,value=text.split('=',1)
        if name not in ('DisabledDraw','DisabledJrrp','DisabledSend','simple'): raise ValueError('Only documented local switches are supported')
        if value not in ('0','1'): raise ValueError('Use0 or1')
        state['config'][name]=int(value); return {'name':name,'value':int(value)}
    if command.startswith('.str'):
        require_gm(state,actor); name,_,value=command[1:].partition(' ')
        strings=state.setdefault('strings',{})
        if not value: return {'name':name,'value':strings.get(name)}
        if value=='reset': strings.pop(name,None)
        else:
            variables=re.findall(r'\{([^{}]+)\}',value)
            if any(x not in ('nick','pc','res') for x in variables): raise ValueError('Allowed local placeholders: nick/pc/res')
            value.format(nick='',pc='',res='')
            strings[name]='' if value=='NULL' else value
        return {'saved':name,'note':'Presentation templates are applied to result.rendered; canonical numeric JSON remains unchanged'}
    if command=='.rf': return roll('4df')
    m=re.fullmatch(r'\.(?:w|ww|ws)(\d+)?(?:a(\d+))?(?:k(\d+))?(?:m(\d+))?([+-]\d+)?',command)
    if m:
        n,a,k,s,b=m.groups(); return pool(int(n or 10),int(a or 10),int(k or 8),int(s or 10),int(b or 0))
    if command.startswith('.r') and not command.startswith(('.rh','.rav','.rcv','.ral','.rcl')):
        return roll(command[2:].strip(),state['default_die'])
    if command.startswith('.'):
        raise ValueError('Unsupported local command; consult manual coverage. No implicit network or historical-service fallback.')
    result = {'recorded_message':command}
    if state.get('reply_rules', {}).get(actor, {}).get(command) and command in state['replies'].get(actor, {}):
        result.update(reply=state['replies'][actor][command], reply_visibility='actor', reply_match='exact')
    elif command in state.get('table_replies', {}):
        result.update(reply=state['table_replies'][command]['text'], reply_visibility='table', reply_match='exact')
    return result


def execute(path, scope, actor, command, operation, expected):
    if not all(isinstance(x,str) and x.strip() for x in (scope,actor,command,operation)) or len(command)>20000:
        raise ValueError('Explicit bounded scope/actor/command/operation required')
    if type(expected) is not int or expected<0: raise ValueError('Expected revision required')
    db=sqlite3.connect(path,timeout=30)
    try:
        db.executescript('CREATE TABLE IF NOT EXISTS tables(scope TEXT PRIMARY KEY,state TEXT); CREATE TABLE IF NOT EXISTS requests(scope TEXT,operation TEXT,request TEXT,response TEXT,PRIMARY KEY(scope,operation));')
        db.execute('BEGIN IMMEDIATE')
        request=json.dumps([actor,command,expected],ensure_ascii=False)
        prior=db.execute('SELECT request,response FROM requests WHERE scope=? AND operation=?',(scope,operation)).fetchone()
        if prior:
            if prior[0]!=request: raise ValueError('Operation ID reused with changed input')
            return json.loads(prior[1])
        row=db.execute('SELECT state FROM tables WHERE scope=?',(scope,)).fetchone(); state=json.loads(row[0]) if row else fresh()
        if expected!=state['revision']: raise ValueError('Stale revision')
        audience='table'; actual=command.strip()
        if actual and actual[0] in '。!！': actual='.'+actual[1:]
        disabled={'DisabledDraw':('.draw','.deck '),'DisabledJrrp':('.jrrp',),'DisabledSend':('.send',)}
        for setting,prefixes in disabled.items():
            if state['config'].get(setting) and actual.startswith(prefixes): raise ValueError('Local command disabled by '+setting)
        if actual.startswith('.rh') or (state['config'].get('secret') and re.match(r'\.(r|sc |en |w|coc|dnd)',actual)):
            observers=state['observers'] if state['config'].get('ob',1) else []
            audience=list(dict.fromkeys([actor,*([state['gm']] if state['gm'] else []),*observers]))
            if actual.startswith('.rh'): actual='.r'+actual[3:]
        elif actual.startswith(('.team desc','.npc','.monster','.des','.custom','.reply','.clock','.log get','.log group','.notice ','.st','.card ','.nn','.hiy','.lookup import ','.mark ')):
            audience=[actor]
        if actual.startswith('.log group '):
            text=actual[len('.log group '):]
            if text.startswith('list '):
                name=text[5:]; scopes=[]
                for other_scope,raw in db.execute('SELECT scope,state FROM tables'):
                    other=state if other_scope==scope else json.loads(raw)
                    if actor in other['players'] and name in other['logs']: scopes.append(other_scope)
                result={'scopes':scopes,'name':name}
            elif text.startswith('get '):
                requested,name=text[4:].split(' ',1); scopes=list(dict.fromkeys(requested.split(',')))
                if not 1<=len(scopes)<=20: raise ValueError('Explicit1..20 local table scopes required')
                entries=[]
                for other_scope in scopes:
                    row=db.execute('SELECT state FROM tables WHERE scope=?',(other_scope,)).fetchone()
                    if row is None: raise ValueError('Table unavailable')
                    other=state if other_scope==scope else json.loads(row[0])
                    if actor not in other['players']: raise ValueError('Actor has no membership in requested local table')
                    entries.extend(dict(scope=other_scope,**x) for x in visible_log(other,actor,name))
                result={'name':name,'entries':sorted(entries,key=lambda x:x['utc'])}
            else: raise ValueError('Use .log group list name or .log group get scope1,scope2 name')
        else: result=dispatch(state,actor,actual)
        if isinstance(result, dict) and result.get('reply_visibility') == 'actor': audience = [actor]
        if isinstance(result,dict) and actual.startswith('.r') and not state['config'].get('simple') and 'strRoll' in state.get('strings',{}):
            result['rendered']=state['strings']['strRoll'].format(nick=actor,pc=player(state,actor)['active'] or actor,res=json.dumps(result,ensure_ascii=False))
        state['revision']+=1
        response=dict(revision=state['revision'],operation=operation,audience=audience,result=result)
        if state['active_log'] and not actual.startswith('.log'):
            state['logs'][state['active_log']].append(dict(actor=actor,command=command,utc=datetime.now(timezone.utc).isoformat(),**response))
        db.execute('INSERT OR REPLACE INTO tables VALUES(?,?)',(scope,json.dumps(state,ensure_ascii=False)))
        db.execute('INSERT INTO requests VALUES(?,?,?,?)',(scope,operation,request,json.dumps(response,ensure_ascii=False)))
        db.commit(); return response
    finally: db.rollback(); db.close()


def strip_ooc(text):
    result=[]; stack=[]
    for c in text:
        if c in '(（': stack.append(c)
        elif c in ')）':
            if not stack or (stack[-1],c) not in (('(',')'),('（','）')): raise ValueError('Unbalanced OOC parentheses; raw log retained')
            stack.pop()
        elif not stack: result.append(c)
    if stack: raise ValueError('Unbalanced OOC parentheses; raw log retained')
    return ''.join(result)


def export_log(path,scope,actor,name,destination,kind='txt'):
    entries=visible_log(read(path,scope),actor,name)
    lines=[x['utc']+' '+x['actor']+': '+x['command']+'\n'+json.dumps(x['result'],ensure_ascii=False) for x in entries]
    if kind=='html':
        body='<!doctype html><meta charset="utf-8"><title>Table log</title>'+''.join('<pre>'+html.escape(line)+'</pre>' for line in lines)
    elif kind=='txt': body='\n\n'.join(lines)
    elif kind=='clean-txt':
        # Human message echoes would reintroduce removed OOC text; export cleaned messages only, dice records verbatim.
        body='\n\n'.join(x['utc']+' '+x['actor']+': '+(x['command']+'\n'+json.dumps(x['result'],ensure_ascii=False) if x['command'].startswith('.') else strip_ooc(x['command'])) for x in entries if x['command'].startswith('.') or strip_ooc(x['command']).strip())
    elif kind=='json': body=json.dumps(entries,ensure_ascii=False,indent=2)
    elif kind=='docx':
        from xml.sax.saxutils import escape
        colors=['005A9C','7A3E00','4F6B20','713D7C']; actors=list(dict.fromkeys(x['actor'] for x in entries))
        paragraphs=''.join('<w:p><w:r><w:rPr><w:color w:val="'+colors[actors.index(x['actor'])%len(colors)]+'"/></w:rPr><w:t xml:space="preserve">'+escape(line)+'</w:t></w:r></w:p>' for x in entries for line in (x['utc']+' '+x['actor']+': '+x['command']+'\n'+json.dumps(x['result'],ensure_ascii=False)).splitlines())
        document='<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+paragraphs+'<w:sectPr/></w:body></w:document>'
        with zipfile.ZipFile(destination,'x',zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
            archive.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
            archive.writestr('word/document.xml',document.encode('utf-8'))
        with zipfile.ZipFile(destination) as archive: assert archive.read('word/document.xml').decode('utf-8')==document
        return {'exported':str(destination),'format':kind,'entries':len(entries)}
    else: raise ValueError('Export format must be txt/clean-txt/html/json/docx')
    with Path(destination).open('x',encoding='utf-8',newline='\n') as out: out.write(body+'\n')
    assert Path(destination).read_text(encoding='utf-8')==body+'\n'
    return {'exported':str(destination),'format':kind,'entries':len(entries)}


def wait_for_timers(path, scope, actor, timeout):
    """Bounded foreground wait; pending timers survive timeout and process exit."""
    if not 1 <= timeout <= 60: raise ValueError('Wait timeout must be1..60 seconds')
    until = time.monotonic() + timeout
    while True:
        if actor_timers(read(path, scope), actor, time.time(), due_only=True): return True
        remaining = until - time.monotonic()
        if remaining <= 0: return False
        time.sleep(min(.25, remaining))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--db',type=Path,required=True); ap.add_argument('--scope',required=True); ap.add_argument('--actor',required=True)
    ap.add_argument('--command'); ap.add_argument('--operation'); ap.add_argument('--expected',type=int)
    ap.add_argument('--wait-timers',type=int,metavar='SECONDS',help='Wait1..60 seconds for own timers, then run .clock poll; explicit operation/revision/private-output required')
    ap.add_argument('--private-output',type=Path,help='Local private response file; never displayed in public CLI output')
    ap.add_argument('--export-log'); ap.add_argument('--output',type=Path); ap.add_argument('--format',choices=['txt','clean-txt','html','json','docx'],default='txt')
    a=ap.parse_args()
    try:
        if a.wait_timers is not None:
            if a.command or a.export_log or not a.operation or a.expected is None or not a.private_output:
                raise ValueError('Timer wait requires operation, expected and private-output; no command/export')
            if read(a.db,a.scope)['revision'] != a.expected: raise ValueError('Stale revision')
            if not wait_for_timers(a.db,a.scope,a.actor,a.wait_timers):
                print(json.dumps({'timed_out':True,'pending_timers_preserved':True})); return
            a.command='.clock poll'
        if a.export_log:
            if a.output is None: raise ValueError('--output required')
            result=export_log(a.db,a.scope,a.actor,a.export_log,a.output,a.format)
        elif a.command:
            result=execute(a.db,a.scope,a.actor,a.command,a.operation,a.expected)
            if isinstance(result.get('audience'),list):
                if a.private_output:
                    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
                    if a.private_output.exists():
                        if a.private_output.read_text(encoding='utf-8')!=text: raise ValueError('Private output exists with different contents')
                    else:
                        with a.private_output.open('x',encoding='utf-8',newline='\n') as out: out.write(text)
                result={k:result[k] for k in ('revision','operation')}
                result['private_result_saved']=bool(a.private_output)
                result['note']='Retry identical operation with --private-output to retrieve privately; file access control belongs to the local operator'
        else:
            state=read(a.db,a.scope)
            result={'revision':state['revision'],'keeper':state['gm'],'player':state['players'].get(a.actor,{}),'active_log':state['active_log']}
    except (ValueError,KeyError,sqlite3.Error,OSError) as exc: ap.error(str(exc))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
