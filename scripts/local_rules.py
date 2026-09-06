"""Bounded calculations for verified local passages; unresolved outcomes stay pending."""
import argparse
import copy
import json


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum: raise ValueError(f'{name} must be an integer >= {minimum}')


def jiangshan_parry(hp, stance, action_points, damage):
    """After a successful parry only; Jiangshanxue 3.1, paragraphs 133-134."""
    for name, value in [('stance', stance), ('action_points', action_points), ('damage', damage)]: integer(value, name)
    integer(hp, 'hp', -100000)
    if stance == 0: raise ValueError('Resolve parry permission at zero stance before applying this helper')
    overflow = max(0, damage - stance)
    remaining = max(0, stance - damage)
    return {'hp': hp - overflow, 'stance': remaining, 'action_points': 0 if remaining == 0 else action_points,
            'unbalanced': remaining == 0, 'hp_damage': overflow}


def jiangshan_death(hp, maximum, roll):
    """Local 3.1 paragraph 122 leaves roll 5 and odd-half rounding unspecified."""
    integer(hp, 'hp', -100000); integer(maximum, 'maximum', 1); integer(roll, 'roll', 1)
    if roll > 20: raise ValueError('Use a d20 result')
    if hp >= 0: return {'status': 'not-triggered', 'note': 'Passage says below zero, not zero or below.'}
    if roll == 5: return {'status': 'pending', 'question': 'Source omits exactly 5; obtain a table ruling.'}
    if roll < 5: return {'status': 'dead'}
    if roll == 20:
        if maximum % 2: return {'status': 'pending', 'question': 'Source does not specify rounding for half of odd maximum HP.'}
        return {'status': 'recovered', 'hp': maximum // 2}
    return {'status': 'dying', 'deadline_minutes': 30, 'further_damage': 'death'}


def toc_safe_rest(pools, chosen, *, safe_minutes, interrupted=False, already_used=False):
    """TOC local player handbook PDF64. Preview only; commit once after the full hour."""
    integer(safe_minutes, 'safe_minutes')
    if already_used: raise ValueError('Safe-haven refresh already used this session')
    if not 1 <= len(chosen) <= 3 or len(chosen) != len(set(chosen)): raise ValueError('Choose 1-3 distinct general pools')
    result = copy.deepcopy(pools)
    for key in chosen:
        if key not in pools or pools[key].get('kind') != 'general': raise ValueError('Only eligible general pools; never investigation, Health, Sanity or Stability')
        integer(pools[key]['current'], 'current'); integer(pools[key]['rating'], 'rating')
        if pools[key]['current'] > pools[key]['rating']: raise ValueError('Pool exceeds rating')
    if safe_minutes < 60 or interrupted:
        return {'pools': result, 'refreshed': [], 'used': False, 'note': 'No provisional gains are committed.'}
    for key in chosen: result[key]['current'] = result[key]['rating']
    return {'pools': result, 'refreshed': chosen, 'used': True}


def toc_psychotherapy(pool, test_spend, recovery_spend, roll, stability, rating, *, specialist=False):
    """TOC PDF63: successful test cost and subsequent 2:1 recovery cost are separate."""
    for name, value in [('pool', pool), ('test_spend', test_spend), ('recovery_spend', recovery_spend), ('rating', rating)]: integer(value, name)
    integer(stability, 'stability', -100000); integer(roll, 'roll', 1)
    if roll > 6 or test_spend > pool or stability > rating: raise ValueError('Invalid die, spend or Stability')
    difficulty = 3 if specialist else 4
    remaining = pool - test_spend
    if roll + test_spend < difficulty:
        return {'success': False, 'pool': remaining, 'stability': stability, 'retry': 'same analyst waits until patient loses more Stability'}
    if recovery_spend > remaining: raise ValueError('Recovery purchase exceeds remaining pool')
    return {'success': True, 'pool': remaining - recovery_spend, 'stability': min(rating, stability + 2 * recovery_spend)}


OPERATIONS = {name: globals()[name] for name in ('jiangshan_parry', 'jiangshan_death', 'toc_safe_rest', 'toc_psychotherapy')}
if __name__ == '__main__':
    from pathlib import Path
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('operation', choices=OPERATIONS); ap.add_argument('input', type=Path)
    a = ap.parse_args()
    print(json.dumps(OPERATIONS[a.operation](**json.loads(a.input.read_text(encoding='utf-8'))), ensure_ascii=False, indent=2))
