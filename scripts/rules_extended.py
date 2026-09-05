"""Explicit-input helpers; never roll dice or decide fictional permission.

Sources and unresolved cases: references/systems/advanced-mechanics.md.
"""


def bounded(value, low=0, high=None):
    if type(value) is not int or value < low or (high is not None and value > high):
        raise ValueError('Integer outside permitted range')
    return value


def coc_volley_plan(skill, volleys, ammunition, waste=0):
    """Full-auto plan, normal starting difficulty, no situational dice modifiers."""
    bounded(skill, 1, 100)
    bounded(ammunition)
    bounded(waste)
    if not isinstance(volleys, list) or not volleys:
        raise ValueError('Declare volleys before rolling')
    capacity = max(3, skill // 10)
    for size in volleys:
        bounded(size, 3, capacity)
    if sum(volleys) + waste > ammunition:
        raise ValueError('Insufficient ammunition including target transitions')
    difficulties = ['regular', 'hard', 'extreme', 'critical', 'impossible']
    return {'spent': sum(volleys) + waste, 'remaining': ammunition-sum(volleys)-waste,
            'volleys': [{'shots': n, 'penalty_dice': min(i, 2),
                         'difficulty': difficulties[min(max(i-2, 0), 4)]}
                        for i, n in enumerate(volleys)]}


def coc_volley_hits(shots, outcome, required='regular'):
    bounded(shots, 1)
    if required not in {'regular', 'hard', 'extreme'}:
        raise ValueError('Critical-only firing requires source adjudication')
    ranks = {'failure': 0, 'regular': 1, 'hard': 2, 'extreme': 3}
    if outcome not in ranks:
        raise ValueError('Critical/fumble needs separate adjudication')
    if ranks[outcome] < ranks[required]:
        return {'normal': 0, 'impaling': 0}
    if outcome == 'extreme' and required != 'extreme':
        impaling = max(1, shots // 2)
        return {'normal': shots-impaling, 'impaling': impaling}
    return {'normal': max(1, shots // 2), 'impaling': 0}


def dnd_slot_cast(turn_id, spent_turns, uses_slot):
    """SRD 5.2.1 turn restriction only; NOT full spell/action legality."""
    if not isinstance(turn_id, str) or not turn_id or type(uses_slot) is not bool:
        raise ValueError('Explicit turn ID and slot use required')
    if not isinstance(spent_turns, list) or not all(isinstance(x, str) and x for x in spent_turns):
        raise ValueError('Expected recorded turn IDs')
    if uses_slot and turn_id in spent_turns:
        raise ValueError('Spell slot already expended to cast a spell this turn')
    return spent_turns + ([turn_id] if uses_slot else [])


def fate_absorb(shifts, stress_boxes, consequences):
    bounded(shifts)
    bounded(stress_boxes)
    if not isinstance(consequences, list) or len(set(consequences)) != len(consequences):
        raise ValueError('Distinct available consequence slots required')
    if any(type(x) is not int or x not in {2, 4, 6} for x in consequences):
        raise ValueError('Condensed standard consequences are 2, 4, 6')
    absorbed = stress_boxes + sum(consequences)
    return {'absorbed': absorbed, 'taken_out': absorbed < shifts}


def fate_recovery(severity, self_treatment=False):
    if type(severity) is not int or severity not in {2, 4, 6} or type(self_treatment) is not bool:
        raise ValueError('Expected consequence severity and treatment flag')
    return {'difficulty': severity + (2 if self_treatment else 0),
            'wait_after_treatment': {2: 'one full scene', 4: 'one full session', 6: 'breakthrough'}[severity]}


def blades_vice(stress, highest):
    bounded(stress)
    bounded(highest, 1, 6)
    return {'stress': max(0, stress-highest), 'overindulgence': highest > stress}


def blades_downtime_cost(activities, at_war=False):
    bounded(activities)
    if type(at_war) is not bool:
        raise ValueError('Explicit war flag required')
    return max(0, activities-(1 if at_war else 2))
