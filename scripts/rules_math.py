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
