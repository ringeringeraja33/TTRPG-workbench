"""Audit a declared scenario graph; cannot prove fictional clue sufficiency.

JSON: {start: node_id, nodes: [{id, leads_to: [node_id], exit: bool}],
       clues: [{id, node, reveals, audience: [player_id or all]}]}.
An empty audience is GM-only. Run with --player to emit only visible clues.
"""
import argparse
import json
from pathlib import Path


def audit(plan):
    errors = []
    nodes = plan['nodes']
    ids = [n['id'] for n in nodes]
    if len(set(ids)) != len(ids):
        errors.append('duplicate node ID')
    graph = {n['id']: n['leads_to'] for n in nodes}
    if plan['start'] not in graph:
        errors.append('missing start node')
    for source, targets in graph.items():
        for target in targets:
            if target not in graph:
                errors.append(f'unknown destination: {source} -> {target}')
    clue_ids = set()
    for clue in plan['clues']:
        if clue['id'] in clue_ids:
            errors.append('duplicate clue ID: '+clue['id'])
        clue_ids.add(clue['id'])
        if clue['node'] not in graph or clue['reveals'] not in graph:
            errors.append('unknown clue node: '+clue['id'])
        if not isinstance(clue['audience'], list) or not all(isinstance(x, str) and x for x in clue['audience']):
            errors.append('invalid audience: '+clue['id'])
    reached, todo = set(), [plan['start']]
    while todo:
        current = todo.pop()
        if current in reached or current not in graph:
            continue
        reached.add(current)
        todo.extend(graph[current])
    for node in sorted(set(graph)-reached):
        errors.append('unreachable node: '+node)
    if not any(n.get('exit') is True and n['id'] in reached for n in nodes):
        errors.append('no reachable exit')
    return {'ok': not errors, 'errors': errors, 'reachable_nodes': sorted(reached)}


def projection(plan, player):
    return {'clues': [c for c in plan['clues'] if 'all' in c['audience'] or player in c['audience']]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--player')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8-sig'))
    result = projection(plan, args.player) if args.player else audit(plan)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.player and not result['ok']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
