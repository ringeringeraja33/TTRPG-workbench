"""CoC7 proposed results; callers supply actual dice and commit once.

Local core PDF126-129,155-157. Costs and spell exceptions require the spell entry.
"""
from rules_extended import bounded


def vehicle_damage(initial_build, current_build, amount, unit):
    bounded(initial_build, 1)
    bounded(current_build, 0, initial_build)
    bounded(amount)
    if unit not in {'build', 'ordinary_damage'}:
        raise ValueError('Declare collision Build or ordinary damage units')
    loss = amount if unit == 'build' else amount//10
    remaining = max(0, current_build-loss)
    return {'remaining_build': remaining, 'build_loss': loss,
            'drive_penalty': int(0 < remaining <= initial_build//2),
            'inoperable': remaining == 0,
            'catastrophic_single_collision': unit == 'build' and loss >= initial_build}


def collision(severity, vehicle_roll, occupant_rolls, delay_roll):
    limits = {'minor': (0,2), 'moderate': (1,6), 'serious': (1,10),
              'severe': (2,20), 'extreme': (5,50)}
    if severity not in limits or not isinstance(occupant_rolls, list):
        raise ValueError('Explicit severity and individual occupant rolls required')
    low, high = limits[severity]
    bounded(vehicle_roll, low, high)
    bounded(delay_roll, 1, 3)
    for roll in occupant_rolls:
        bounded(roll, low, high)
    return {'vehicle_build_damage': vehicle_roll, 'occupant_hp_damage': occupant_rolls[:],
            'delay_ap': delay_roll, 'occupant_armor_applies': False}


def magic_payment(mp, hp, mp_cost):
    bounded(mp); bounded(hp); bounded(mp_cost)
    spill = max(0, mp_cost-mp)
    return {'mp': max(0, mp-mp_cost), 'hp': max(0, hp-spill), 'hp_damage': spill,
            'injury_check_required': spill > 0}


def casting_outcome(first_cast, pushed, succeeded, interrupted=False):
    if any(type(x) is not bool for x in [first_cast, pushed, succeeded, interrupted]):
        raise ValueError('Explicit boolean casting flags required')
    if pushed and not first_cast:
        raise ValueError('Established spell has no routine casting roll to push')
    if interrupted:
        return {'works': False, 'pay_costs': True, 'backlash': 'Keeper adjudicates interruption'}
    return {'works': not first_cast or succeeded or pushed, 'pay_costs': True,
            'backlash': 'additional 1d6 multiples of costs plus consequences' if pushed and not succeeded else None}
