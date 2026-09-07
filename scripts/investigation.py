"""Declared evidence dependencies, not a semantic proof or automatic revelation."""
import argparse
import json
from pathlib import Path


def validate(plan):
    if plan.get('schema') != 1:
        raise ValueError('Expected investigation schema 1')
    records = plan['evidence'] + plan['conclusions']
    ids = [r['id'] for r in records]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('Evidence and conclusion IDs must be unique nonempty strings')
    for r in records:
        if not isinstance(r['text'], str):
            raise ValueError('Text required')
        if not isinstance(r['audience'], list) or any(not isinstance(a, str) or not a for a in r['audience']):
            raise ValueError('Explicit audience required')
    evidence_ids = {r['id'] for r in plan['evidence']}
    for r in plan['evidence']:
        if type(r.get('available')) is not bool:
            raise ValueError('Evidence availability must be explicit')
    for r in plan['conclusions']:
        routes = r['routes']
        if type(r.get('essential')) is not bool or not isinstance(routes, list):
            raise ValueError('Conclusion requires essential flag and routes')
        for route in routes:
            if not isinstance(route, list) or not route or any(not isinstance(i, str) or i not in ids for i in route):
                raise ValueError('Routes must be nonempty AND groups of known IDs')
    return evidence_ids


def closure(plan, seeds):
    known = set(seeds)
    while True:
        added = {r['id'] for r in plan['conclusions']
                 if any(set(route) <= known for route in r['routes'])} - known
        if not added:
            return known
        known.update(added)


def audit(plan, unavailable=(), player=None):
    evidence_ids = validate(plan)
    unavailable = set(unavailable)
    if not unavailable <= evidence_ids:
        raise ValueError('Unknown unavailable evidence')
    seeds = {r['id'] for r in plan['evidence'] if r['available'] and r['id'] not in unavailable
             and (player is None or 'all' in r['audience'] or player in r['audience'])}
    reached = closure(plan, seeds)
    missing = sorted(r['id'] for r in plan['conclusions'] if r['id'] not in reached)
    essential = {r['id'] for r in plan['conclusions'] if r['essential']}
    bottlenecks = {}
    for eid in sorted(seeds):
        lost = sorted((essential & reached) - closure(plan, seeds - {eid}))
        if lost:
            bottlenecks[eid] = lost
    return {'ok': not (essential - reached), 'available_evidence': sorted(seeds),
            'derivable_conclusions': sorted(reached - evidence_ids),
            'unresolved_conclusions': missing, 'blocked_essential': sorted(essential - reached),
            'single_evidence_bottlenecks': bottlenecks,
            'scope': 'GM-only declared dependency analysis; derivable does not mean discovered or true.'}


def projection(plan, player):
    validate(plan)
    # Do not expose conclusion IDs, routes, acquisition sites, truth or unused fields.
    return {'evidence': [{'text': r['text']} for r in plan['evidence']
                         if r['available'] and ('all' in r['audience'] or player in r['audience'])]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan', type=Path)
    p.add_argument('--unavailable', action='append', default=[])
    group = p.add_mutually_exclusive_group()
    group.add_argument('--knowledge-of', help='GM-only analysis of one player knowledge set')
    group.add_argument('--player', help='Safe evidence-only export')
    a = p.parse_args()
    try:
        plan = json.loads(a.plan.read_text(encoding='utf-8-sig'))
        if a.player and a.unavailable:
            raise ValueError('Scenario perturbations are GM analysis only')
        result = projection(plan, a.player) if a.player else audit(plan, a.unavailable, a.knowledge_of)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result.get('ok') is False:
            raise SystemExit(1)
    except (ValueError, KeyError, TypeError, OSError) as e:
        p.exit(2, str(e) + '\n')


if __name__ == '__main__':
    main()
