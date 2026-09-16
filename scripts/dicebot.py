"""Legacy local character-card storage and numeric checks."""
import argparse
import copy
import json
import re
import secrets
import sqlite3
import sys
from pathlib import Path
from dice import roll
from rules_math import coc_result

ALIASES = {}
for canonical, aliases in {
    'STR': ['力量'], 'CON': ['体质'], 'SIZ': ['体型'], 'DEX': ['敏捷'],
    'APP': ['外貌'], 'INT': ['智力', '灵感', '智力灵感'], 'POW': ['意志'],
    'EDU': ['教育'], 'LUCK': ['幸运', '运气'], 'SAN': ['理智', '理智值'],
    'HP': ['生命', '生命值', '耐久'], 'MP': ['魔法值'],
}.items():
    for alias in [canonical, *aliases]: ALIASES[alias.casefold()] = canonical
NAME = r'[A-Za-z\u4e00-\u9fff][A-Za-z\u4e00-\u9fff()（）·]*'


def key(name):
    if not re.fullmatch(NAME, name): raise ValueError('Invalid stat name')
    return ALIASES.get(name.casefold(), name.casefold())


def assignments(text, stats):
    result, seen, pos = dict(stats), set(), 0
    while pos < len(text):
        if text[pos] in ' ,，;；\t': pos += 1; continue
        match = re.match(r'(' + NAME + r')\s*([=+-]?)\s*(\d+)', text[pos:])
        if not match: raise ValueError('Use stat60 / stat=60 or stat+5 / stat-5; expressions are not accepted')
        name, op, number = match.groups(); name = key(name); number = int(number)
        if name in seen: raise ValueError('Duplicate stat or alias in one update')
        seen.add(name)
        if op in ('+', '-'):
            if name not in result: raise ValueError('Cannot adjust an unrecorded stat')
            number = result[name] + (number if op == '+' else -number)
        if not 0 <= number <= 999: raise ValueError('Stored values must be integers 0..999; no silent clamping')
        result[name] = number; pos += match.end()
    if not seen: raise ValueError('No stat assignments supplied')
    return result


def percentile(mode, extra=1):
    units = secrets.randbelow(10)
    tens = [secrets.randbelow(10) for _ in range(1 + (extra if mode else 0))]
    candidates = [(10 * t + units) or 100 for t in tens]
    value = max(candidates) if mode == 'penalty' else min(candidates)
    return {'units': units, 'tens': tens, 'candidates': candidates, 'total': value,
            'mode': mode or 'normal', 'randomness': 'OS secrets; actual roll'}


def connect(path):
    db = sqlite3.connect(path, timeout=30)
    db.execute('CREATE TABLE IF NOT EXISTS accounts(scope TEXT, owner TEXT, state TEXT, PRIMARY KEY(scope,owner))')
    db.execute('CREATE TABLE IF NOT EXISTS requests(scope TEXT, owner TEXT, operation TEXT, request TEXT, response TEXT, PRIMARY KEY(scope,owner,operation))')
    db.commit()
    return db


def dispatch(state, command):
    cards = state['cards']; active = state['active']
    m = re.fullmatch(r'\.coc(\d*)', command)
    if m:
        count = int(m[1] or 1)
        if not 1 <= count <= 10: raise ValueError('Candidate count must be 1..10 (tool limit, not a rule)')
        candidates = []
        for _ in range(count):
            stats, rolls = {}, {}
            for name in ('STR', 'CON', 'SIZ', 'DEX', 'APP', 'INT', 'POW', 'EDU', 'LUCK'):
                event = roll('2d6+6' if name in ('SIZ', 'INT', 'EDU') else '3d6')
                rolls[name] = event
                stats[name] = event['total'] * 5
            candidates.append({'stats': stats, 'rolls': rolls,
                               'total_without_luck': sum(stats.values()) - stats['LUCK'],
                               'total_with_luck': sum(stats.values())})
        batch = 'b' + str(state['revision'] + 1)
        record = {'batch': batch, 'profile': 'coc7-core', 'stage': 'base_attributes_age_pending',
                  'candidates': candidates}
        state.setdefault('chargen_batches', {})[batch] = record
        return record
    m = re.fullmatch(r'\.coc show (b\d+)', command)
    if m:
        record = state.get('chargen_batches', {}).get(m[1])
        if record is None: raise ValueError('Unknown attribute batch in this scope/owner')
        return record
    m = re.fullmatch(r'\.coc take (b\d+) (\d+) ([a-zA-Z0-9_-]{1,64}) (.+)', command)
    if m:
        batch, number, cid, name = m.groups()
        record = state.get('chargen_batches', {}).get(batch)
        if record is None: raise ValueError('Unknown attribute batch in this scope/owner')
        index = int(number) - 1
        if not 0 <= index < len(record['candidates']): raise ValueError('Candidate index is one-based and must exist')
        if cid in cards: raise ValueError('Card already exists; selection must not overwrite it')
        candidate = record['candidates'][index]
        cards[cid] = {'name': name, 'profile': record['profile'], 'stats': dict(candidate['stats']),
                      'creation': {'stage': 'base_attributes_age_pending', 'batch': batch,
                                   'candidate': index + 1, 'original': copy.deepcopy(candidate)}}
        state['active'] = cid
        return {'created': cid, **copy.deepcopy(cards[cid]), 'legality': 'Age, derived values and skill allocation pending'}
    if command == '.card list':
        return {'active': active, 'cards': [{'id': k, 'name': v['name']} for k, v in cards.items()]}
    if command.startswith('.card new '):
        parts = command[len('.card new '):].split(maxsplit=1)
        if len(parts) != 2 or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', parts[0]): raise ValueError('Use .card new <id> <display name>')
        cid, name = parts
        if cid in cards: raise ValueError('Card already exists; import must not overwrite it')
        cards[cid] = {'name': name, 'profile': 'coc7-core', 'stats': {}}
        state['active'] = cid
        return {'created': cid, 'name': name, 'legality': 'not audited'}
    if command.startswith('.card use '):
        cid = command[len('.card use '):].strip()
        if cid not in cards: raise ValueError('Unknown card in this scope/owner')
        state['active'] = cid
        return {'active': cid}
    if command.startswith('.r ') or re.fullmatch(r'\.r\d.*', command):
        expression = command[2:].strip()
        # Explicit bounded product supports the tutorial's .r3d6*5 without eval.
        m = re.fullmatch(r'(\d+d(?:\d+|F)(?:[+-]\d+)?)(?:\*(\d+))?', expression)
        if not m: raise ValueError('Use NdS[+/-integer][*integer]')
        multiplier = int(m[2] or 1)
        if not 1 <= multiplier <= 1000: raise ValueError('Multiplier must be 1..1000')
        result = roll(m[1]); result['multiplier'] = multiplier
        result['total'] *= multiplier; result['expression'] = expression
        return result
    if active not in cards: raise ValueError('Create or select a card first')
    card = cards[active]; stats = card['stats']
    if command in ('.st', '.st show'):
        return {'card_id': active, **card, 'legality': 'recorded values; not an audited character'}
    if command.startswith('.st show'):
        name = key(command[len('.st show'):].strip())
        if name not in stats: raise ValueError('Stat not recorded; no default or inferred value')
        return {'card_id': active, 'stat': name, 'value': stats[name]}
    if command == '.st export':
        if not stats: raise ValueError('No recorded stats to export')
        return {'dialect': 'workbench-local-v1', 'command': '.st ' + ' '.join(k + '=' + str(v) for k, v in sorted(stats.items())),
                'note': 'Import recorded numeric fields into another local card.'}
    if command.startswith('.st'):
        card['stats'] = assignments(command[3:].strip(), stats)
        return {'card_id': active, 'stats': card['stats'], 'legality': 'not audited'}
    if command.startswith('.nn'):
        name = command[3:].strip()
        if not name: raise ValueError('Empty name')
        card['name'] = name
        return {'card_id': active, 'name': name}
    m = re.fullmatch(r'\.ra([bp]?)([12]?)\s*(' + NAME + r')(?:\s+(\d+))?', command)
    if m:
        mode, count, name, explicit = m.groups(); name = key(name)
        if count and not mode: raise ValueError('Extra dice require rab or rap')
        if explicit is None and name not in stats: raise ValueError('Stat not recorded')
        target = int(explicit) if explicit is not None else stats[name]
        if not 0 <= target <= 999: raise ValueError('This check adapter supports target 0..999 only')
        result = percentile({'b': 'bonus', 'p': 'penalty'}.get(mode), int(count or 1))
        result.update(card_id=active, stat=name, target=target, profile=card['profile'],
                      outcome=coc_result(target, result['total']), effects_applied=False)
        return result
    raise ValueError('Unsupported local command; consult local card reference. No state changed.')


def execute(path, scope, owner, command, operation, expected):
    if not all(isinstance(x, str) and x.strip() for x in (scope, owner, command, operation)):
        raise ValueError('Explicit scope, owner, command and operation ID required')
    if len(command) > 10000 or '\n' in command or '\r' in command: raise ValueError('One bounded command per request')
    if type(expected) is not int or expected < 0: raise ValueError('Expected revision must be nonnegative')
    request = json.dumps([command, expected], ensure_ascii=False)
    db = connect(path)
    try:
        db.execute('BEGIN IMMEDIATE')
        previous = db.execute('SELECT request,response FROM requests WHERE scope=? AND owner=? AND operation=?', (scope, owner, operation)).fetchone()
        if previous:
            if previous[0] != request: raise ValueError('Operation ID reused with different input')
            return json.loads(previous[1])
        row = db.execute('SELECT state FROM accounts WHERE scope=? AND owner=?', (scope, owner)).fetchone()
        state = json.loads(row[0]) if row else {'revision': 0, 'active': None, 'cards': {}}
        if expected != state['revision']: raise ValueError('Stale revision; read current state before retrying')
        result = dispatch(state, command.strip())
        state['revision'] += 1
        response = {'revision': state['revision'], 'operation': operation, 'result': result}
        db.execute('INSERT OR REPLACE INTO accounts VALUES(?,?,?)', (scope, owner, json.dumps(state, ensure_ascii=False)))
        db.execute('INSERT INTO requests VALUES(?,?,?,?,?)', (scope, owner, operation, request, json.dumps(response, ensure_ascii=False)))
        db.commit()
        return response
    finally:
        db.rollback(); db.close()


def inspect(path, scope, owner):
    # Local trusted operator only. Scope/owner isolate data; they are not authentication.
    if not Path(path).is_file(): return {'revision': 0, 'active': None, 'cards': {}}
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        row = db.execute('SELECT state FROM accounts WHERE scope=? AND owner=?', (scope, owner)).fetchone()
        return json.loads(row[0]) if row else {'revision': 0, 'active': None, 'cards': {}}
    finally: db.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--db', required=True, type=Path); ap.add_argument('--scope', required=True); ap.add_argument('--owner', required=True)
    ap.add_argument('--command'); ap.add_argument('--operation'); ap.add_argument('--expected', type=int)
    a = ap.parse_args()
    try:
        result = execute(a.db, a.scope, a.owner, a.command, a.operation, a.expected) if a.command else inspect(a.db, a.scope, a.owner)
    except (ValueError, sqlite3.Error) as exc: ap.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
