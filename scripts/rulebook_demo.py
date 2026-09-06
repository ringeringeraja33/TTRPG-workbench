"""Original Dream Archaeology 0.2 fixture; not a generic TTRPG engine."""
import argparse
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys

VERSION = 'Dream Archaeology 0.2'

def number(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('integer outside declared bounds')
    return value


def initial():
    return {'version': VERSION, 'turn': 0, 'progress': 0, 'archives': 0, 'ended': False,
            'actors': {name: {'skills': skills, 'strain': 0, 'help': 0, 'recovered': False,
                             'grown': False, 'memories': {name+'-'+str(i): True for i in range(3)}}
                       for name, skills in [('A', {'trace': 2, 'listen': 1, 'weave': 0}),
                                            ('B', {'trace': 1, 'listen': 0, 'weave': 2})]}}


def validate(state):
    if state.get('version') != VERSION:
        raise ValueError('rule version mismatch')
    number(state['turn'], 0, 20)
    number(state['progress'], 0, 5)
    number(state['archives'], 0, 4)
    if type(state['ended']) is not bool or set(state['actors']) != {'A', 'B'}:
        raise ValueError('invalid expedition state')
    ids = []
    for actor in state['actors'].values():
        number(actor['strain'], 0, 6)
        number(actor['help'], 0, 1)
        if any(type(actor[k]) is not bool for k in ('recovered', 'grown')):
            raise ValueError('invalid flags')
        if set(actor['skills']) != {'trace', 'weave', 'listen'}:
            raise ValueError('invalid approaches')
        for value in actor['skills'].values():
            number(value, 0, 2)
        if sum(actor['skills'].values()) not in ((3, 4) if actor['grown'] else (3,)):
            raise ValueError('invalid creation/growth allocation')
        ids.extend(actor['memories'])
        if any(type(fresh) is not bool for fresh in actor['memories'].values()):
            raise ValueError('invalid memory status')
    if len(ids) != 6 or set(ids) != {a+'-'+str(i) for a in ('A', 'B') for i in range(3)}:
        raise ValueError('lost or duplicated memory')


def resolve(skill, die, spend=0, help_bonus=0):
    total = number(skill, 0, 2) + number(die, 1, 6) + number(spend, 0, 2) + number(help_bonus, 0, 1)
    progress, strain = (2, 0) if total >= 5 else (1, 1) if total >= 3 else (0, 2)
    return {'total': total, 'progress_gain': progress, 'strain_gain': strain}


def apply(state, event):
    """Return new state and calculation. Illegal actions leave the input untouched."""
    validate(state)
    if state['ended']:
        raise ValueError('expedition ended')
    current = deepcopy(state)
    who = event.get('actor')
    if who not in current['actors']:
        raise ValueError('unknown actor')
    actor = current['actors'][who]
    other = current['actors']['B' if who == 'A' else 'A']
    kind = event.get('kind')
    fields = {'delve': {'actor', 'kind', 'skill', 'die', 'spend'},
              'help': {'actor', 'kind', 'spend'}, 'recover': {'actor', 'kind'},
              'wait': {'actor', 'kind'}, 'trade': {'actor', 'kind', 'give', 'take', 'consent'}}
    if kind not in fields or set(event) != fields[kind]:
        raise ValueError('unknown action or unexpected fields')
    result = {'kind': kind, 'rule_version': VERSION}
    if kind in ('delve', 'help'):
        if actor['strain'] == 6:
            raise ValueError('fractured actor')
        spend = event['spend']
        if not isinstance(spend, list) or any(not isinstance(x, str) for x in spend):
            raise ValueError('invalid memory list')
        if len(spend) != len(set(spend)) or len(spend) > 2 or (kind == 'help' and len(spend) != 1):
            raise ValueError('invalid memory count')
        if any(actor['memories'].get(x) is not True for x in spend):
            raise ValueError('memory not owned and fresh')
        if kind == 'help' and (other['help'] or other['strain'] == 6):
            raise ValueError('help cannot stack or target fractured actor')
        for mid in spend:
            actor['memories'][mid] = False
        if kind == 'delve':
            if event['skill'] not in actor['skills']:
                raise ValueError('unknown approach')
            result.update(resolve(actor['skills'][event['skill']], event['die'], len(spend), actor['help']))
            actor['help'] = 0
            current['progress'] = min(5, current['progress'] + result['progress_gain'])
            actor['strain'] = min(6, actor['strain'] + result['strain_gain'])
        else:
            other['help'] = 1
    elif kind == 'recover':
        if actor['recovered']:
            raise ValueError('recovery already used this scene')
        actor['strain'] = max(0, actor['strain'] - 2)
        actor['recovered'] = True
    elif kind == 'trade':
        give, take = event['give'], event['take']
        if event['consent'] is not True or give not in actor['memories'] or take not in other['memories']:
            raise ValueError('invalid trade')
        fresh_give, fresh_take = actor['memories'].pop(give), other['memories'].pop(take)
        actor['memories'][take], other['memories'][give] = fresh_take, fresh_give
    current['turn'] += 1
    if current['turn'] % 5 == 0:
        complete = current['progress'] == 5
        current['archives'] += int(complete)
        result['scene_end'] = 'complete' if complete else 'damaged; onward route remains'
        for pc in current['actors'].values():
            pc['help'] = 0
        if current['turn'] == 20:
            current['ended'] = True
        else:
            current['progress'] = 0
            for pc in current['actors'].values():
                pc['help'], pc['recovered'] = 0, False
    validate(current)
    return current, result


def grow(state, who, skill):
    validate(state)
    if not state['ended'] or state['archives'] < 2 or who not in state['actors']:
        raise ValueError('growth unavailable')
    new = deepcopy(state)
    pc = new['actors'][who]
    if pc['grown'] or (skill is not None and (skill not in pc['skills'] or pc['skills'][skill] >= 2)):
        raise ValueError('illegal growth')
    if skill is not None:
        pc['skills'][skill] += 1
    pc['grown'] = True
    validate(new)
    return new


def events():
    def delve(a, skill, die, *spend):
        return dict(actor=a, kind='delve', skill=skill, die=die, spend=list(spend))
    def rest(a):
        return dict(actor=a, kind='recover')
    return [delve('A', 'trace', 1), dict(actor='B', kind='help', spend=['B-0']),
            delve('A', 'trace', 2, 'A-0'), delve('B', 'weave', 6), rest('A'),
            delve('B', 'listen', 1), dict(actor='A', kind='trade', give='A-1', take='B-1', consent=True),
            delve('B', 'weave', 2, 'A-1'), delve('A', 'trace', 1, 'B-1'), rest('B'),
            delve('A', 'listen', 1), delve('B', 'trace', 1), delve('A', 'listen', 1),
            delve('B', 'trace', 1), delve('A', 'listen', 1), rest('A'), rest('B'),
            delve('A', 'trace', 4), delve('B', 'weave', 3, 'B-2'), delve('A', 'trace', 2, 'A-2')]


def run(state, inputs):
    trace = []
    for event in inputs:
        before = deepcopy(state)
        state, result = apply(state, event)
        trace.append(dict(turn=state['turn'], before=before, event=event, calculation=result, after=deepcopy(state)))
    return state, trace


def probabilities():
    rows = []
    for skill in range(3):
        for spend in range(3):
            counts = {0: 0, 1: 0, 2: 0}
            for die in range(1, 7):
                counts[resolve(skill, die, spend)['progress_gain']] += 1
            rows.append({'skill': skill, 'spend': spend, 'help': 0,
                         'none': str(Fraction(counts[0], 6)), 'partial': str(Fraction(counts[1], 6)),
                         'full': str(Fraction(counts[2], 6)),
                         'expected_progress': str(Fraction(counts[1]+2*counts[2], 6))})
    return rows


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    assert json.loads(path.read_text(encoding='utf-8')) == data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--output', type=Path)
    group.add_argument('--resume', type=Path)
    args = parser.parse_args()
    if args.resume:
        snapshot = json.loads(args.resume.read_text(encoding='utf-8'))
        state, trace = run(snapshot, events()[10:])
        print(json.dumps({'state': state, 'trace': trace}, ensure_ascii=False))
        return
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    state, first = run(initial(), events()[:10])
    save(out/'turn-10.json', state)
    resumed = json.loads(subprocess.check_output([sys.executable, '-X', 'utf8', __file__, '--resume',
                                                  str(out/'turn-10.json')], encoding='utf-8'))
    continuous, _ = run(initial(), events())
    assert resumed['state'] == continuous
    trace = first + resumed['trace']
    grown = grow(grow(continuous, 'A', 'listen'), 'B', 'trace')
    save(out/'trace.json', trace)
    save(out/'final.json', grown)
    save(out/'probabilities.json', probabilities())
    lines = ['# Twenty simulated player turns — Dream Archaeology 0.2', '',
             'All dice and player choices are declared fixture inputs, not random play or live players.', '',
             '| Turn | Actor / action | Calculation | Progress | A / B strain | Scene end |',
             '|---|---|---|---|---|---|']
    for t in trace:
        s, c, e = t['after'], t['calculation'], t['event']
        calc = ('total '+str(c['total'])+'; +'+str(c['progress_gain'])+' progress, +'+str(c['strain_gain'])+' strain') if 'total' in c else e['kind']
        lines.append(f"| {t['turn']} | {e['actor']} / {e['kind']} | {calc} | {s['progress']} | {s['actors']['A']['strain']} / {s['actors']['B']['strain']} | {c.get('scene_end', '')} |")
    lines += ['', 'Scene boundary progress displays the reset state; full pre/post states and chosen memory IDs are in trace.json.',
              'Fresh-process recovery after turn 10 matches continuous execution. Two archives: contested reconstruction.',
              'Growth: A Listen 1 to 2; B Trace 1 to 2. Memories stay faded; strain stays A=4, B=2.',
              'Probability model: fair independent d6, one action, no help, no exhaustion or deadline policy. It does not establish strategic balance.']
    (out/'trace.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'turns': len(trace), 'archives': continuous['archives'], 'cold_recovery': True,
                      'output': str(out)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
