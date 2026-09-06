"""SRD 5.2.1 class arithmetic. Prepared spells remain class-specific."""
from rules_extended import bounded
from rules_extended import dnd_slot_cast

FULL = {'Bard', 'Cleric', 'Druid', 'Sorcerer', 'Wizard'}
HALF = {'Paladin', 'Ranger'}
HIT_DIE = {'Barbarian': 12, 'Bard': 8, 'Cleric': 8, 'Druid': 8, 'Fighter': 10,
           'Monk': 8, 'Paladin': 10, 'Ranger': 10, 'Rogue': 8, 'Sorcerer': 6,
           'Warlock': 8, 'Wizard': 6}
# SRD PDF26. Pact Magic is a distinct pool and is deliberately not added here.
SLOTS = [[], [2], [3], [4,2], [4,3], [4,3,2], [4,3,3], [4,3,3,1],
         [4,3,3,2], [4,3,3,3,1], [4,3,3,3,2], [4,3,3,3,2,1],
         [4,3,3,3,2,1], [4,3,3,3,2,1,1], [4,3,3,3,2,1,1],
         [4,3,3,3,2,1,1,1], [4,3,3,3,2,1,1,1],
         [4,3,3,3,2,1,1,1,1], [4,3,3,3,3,1,1,1,1],
         [4,3,3,3,3,2,1,1,1], [4,3,3,3,3,2,2,1,1]]


def multiclass_slots(levels):
    if not isinstance(levels, dict) or not levels or any(c not in HIT_DIE for c in levels):
        raise ValueError('Use the twelve SRD classes')
    for level in levels.values():
        bounded(level, 1, 20)
    bounded(sum(levels.values()), 1, 20)
    casters = set(levels) & (FULL | HALF)
    if len(casters) < 2:
        raise ValueError('Only one Spellcasting class: use its own class table')
    effective = sum(levels[c] for c in casters & FULL) + sum((levels[c]+1)//2 for c in casters & HALF)
    return {'caster_level': effective, 'slots': SLOTS[effective] + [0]*(9-len(SLOTS[effective])),
            'pact_magic_separate': levels.get('Warlock', 0), 'prepared_spells': 'determine for each class separately'}


def fixed_hp(class_order, constitution_mod):
    """One class name per total level; use current CON modifier retroactively."""
    if not isinstance(class_order, list) or not 1 <= len(class_order) <= 20 or any(c not in HIT_DIE for c in class_order):
        raise ValueError('Expected one valid class for each gained level')
    if type(constitution_mod) is not int:
        raise ValueError('Integer CON modifier required')
    gains = [max(1, (HIT_DIE[c] if i == 0 else HIT_DIE[c]//2+1)+constitution_mod)
             for i, c in enumerate(class_order)]
    return {'maximum': sum(gains), 'per_level': gains, 'proficiency_bonus': 2+(len(class_order)-1)//4}


def settle_slot_cast(turn_id, spent_turns, countered):
    """SRD Counterspell: action wasted, interrupted spell slot not expended."""
    if type(countered) is not bool:
        raise ValueError('Explicit Counterspell result required')
    proposed = dnd_slot_cast(turn_id, spent_turns, True)
    return {'spent_turns': spent_turns[:] if countered else proposed,
            'slot_delta': 0 if countered else -1, 'casting_action_consumed': True}
