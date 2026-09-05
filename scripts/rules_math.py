"""Narrow arithmetic helpers, not a universal rules or character validator.

Sources: references/systems/{coc7,dnd2024}-procedures.md.
No dice are rolled here. Examples and tests use explicit inputs.
"""
from fractions import Fraction
from itertools import product


def dnd_modifier(score):
    if type(score) is not int or not 1 <= score <= 30:
        raise ValueError('Ability score must be an integer from 1 to 30')
    return (score - 10) // 2


def dnd_point_cost(scores):
    costs = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    if len(scores) != 6 or any(type(s) is not int or s not in costs for s in scores):
        raise ValueError('Supply six pre-background scores from 8 to 15')
    return sum(costs[s] for s in scores)


def dnd_attack_probability(bonus, ac, *, advantage=False, disadvantage=False):
    def hit(d):
        return d == 20 or (d != 1 and d + bonus >= ac)
    if advantage == disadvantage:
        return Fraction(sum(hit(d) for d in range(1, 21)), 20)
    choose = max if advantage else min
    return Fraction(sum(hit(choose(ds)) for ds in product(range(1, 21), repeat=2)), 400)


def dnd_damage(raw, reduction=0, *, resistance=False, vulnerability=False):
    if any(type(x) is not int or x < 0 for x in (raw, reduction)):
        raise ValueError('Use nonnegative integer damage and fixed reduction')
    value = max(0, raw - reduction)
    if resistance:
        value //= 2
    if vulnerability:
        value *= 2
    return value


def coc_thresholds(skill):
    if type(skill) is not int or skill < 0:
        raise ValueError('Skill must be a nonnegative integer')
    return skill, skill // 2, skill // 5


def coc_injury(max_hp, hp, damage, *, major=False):
    """Single post-armor blow; official Wiki fatal threshold >= max HP.

    Excludes drowning, poison, attacks on helpless people and other exceptions.
    Does not roll CON or decide consciousness after a major wound.
    """
    if any(type(x) is not int for x in (max_hp, hp, damage)) or max_hp < 1 or not 0 <= hp <= max_hp or damage < 0:
        raise ValueError('Invalid HP or damage')
    new_hp = max(0, hp - damage)
    major = major or damage * 2 >= max_hp
    if damage >= max_hp:
        state = 'dead'
    elif new_hp == 0:
        state = 'dying' if major else 'unconscious'
    else:
        state = 'major_wound_requires_CON' if damage * 2 >= max_hp else 'injured'
    return new_hp, major, state


def gumshoe_probability(difficulty, spend):
    if type(spend) is not int or spend < 0:
        raise ValueError('Spend must be a nonnegative integer declared before roll')
    return Fraction(sum(d + spend >= difficulty for d in range(1, 7)), 6)


def coc_result(skill, roll):
    """Core percentile outcome, independent of task difficulty. No luck spent."""
    coc_thresholds(skill)
    if type(roll) is not int or not 1 <= roll <= 100:
        raise ValueError('Percentile must be 1..100')
    if roll == 1:
        return 'critical'
    if roll == 100 or (skill < 50 and roll >= 96):
        return 'fumble'
    if roll > skill:
        return 'failure'
    if roll <= skill // 5:
        return 'extreme'
    if roll <= skill // 2:
        return 'hard'
    return 'regular'


def coc_melee(attacker_skill, attacker_roll, defender_skill, defender_roll, defense):
    if defense not in {'dodge', 'fight_back'}:
        raise ValueError('Choose dodge or fight_back')
    ranks = {'fumble': -1, 'failure': 0, 'regular': 1, 'hard': 2, 'extreme': 3, 'critical': 4}
    attack = ranks[coc_result(attacker_skill, attacker_roll)]
    defend = ranks[coc_result(defender_skill, defender_roll)]
    if attack <= 0 and defend <= 0:
        return 'no_hit'
    if attack > 0 and (attack > defend or (attack == defend and defense == 'fight_back')):
        return 'attacker_hits'
    return 'dodged' if defense == 'dodge' else 'defender_hits'


def coc_outnumbered_bonus(prior_defenses, attacks_per_round=1):
    """Attacker's bonus dice after the defender exhausts its normal defenses."""
    if type(prior_defenses) is not int or prior_defenses < 0 or type(attacks_per_round) is not int or attacks_per_round < 1:
        raise ValueError('Invalid defense count/capacity')
    return int(prior_defenses >= attacks_per_round)


def coc_sanity(san, day_start, day_loss, loss, *, int_roll=None, in_bout=False):
    """Return SAN ledger and threshold flags; INT success supplied as boolean.

    Bout handling and duration require the Keeper's rule lookup and separate timers.
    """
    if any(type(x) is not int or x < 0 for x in (san, day_start, day_loss, loss)) or day_start == 0:
        raise ValueError('Invalid SAN ledger')
    if int_roll is not None and type(int_roll) is not bool:
        raise ValueError('INT outcome must be bool or omitted')
    actual = 0 if in_bout else min(san, loss)
    return {'san': san - actual, 'day_loss': day_loss + actual,
            'int_required': actual >= 5 and int_roll is None,
            'temporary': actual >= 5 and int_roll is True,
            'indefinite': (day_loss + actual) * 5 >= day_start,
            'zero_san': san - actual == 0}


def coc_development(skill, roll, gain):
    coc_thresholds(skill)
    if type(roll) is not int or not 1 <= roll <= 100 or type(gain) is not int or not 1 <= gain <= 10:
        raise ValueError('Invalid development dice')
    return skill + gain if roll > skill or roll > 95 else skill


def coc_chase_points(adjusted_moves):
    """Participants only, after speed rolls and initial escape exclusion."""
    if not adjusted_moves or any(type(x) is not int or x < 1 for x in adjusted_moves):
        raise ValueError('Supply positive adjusted MOV for actual participants')
    slowest = min(adjusted_moves)
    return [1 + move - slowest for move in adjusted_moves]


def dnd_concentration_dc(damage):
    if type(damage) is not int or damage <= 0:
        raise ValueError('Concentration damage must be positive')
    return min(30, max(10, damage // 2))


def dnd_death_save(roll, successes=0, failures=0):
    if type(roll) is not int or not 1 <= roll <= 20 or any(type(x) is not int or not 0 <= x < 3 for x in (successes, failures)):
        raise ValueError('Invalid unresolved death save')
    if roll == 20:
        return {'hp': 1, 'successes': 0, 'failures': 0, 'state': 'conscious'}
    if roll == 1:
        failures += 2
    elif roll >= 10:
        successes += 1
    else:
        failures += 1
    state = 'dead' if failures >= 3 else 'stable' if successes >= 3 else 'unconscious'
    if state == 'stable':
        successes = failures = 0
    return {'hp': 0, 'successes': successes, 'failures': failures, 'state': state}
