"""Read-only, branch-aware ledger recap and next-session preparation. JSON output."""
import argparse
import json
from pathlib import Path
import sqlite3
from session import validate


def read_history(path):
    path = Path(path).resolve(strict=True)
    db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    try:
        rows = db.execute('SELECT revision,id,request,state FROM events ORDER BY revision').fetchall()
    finally:
        db.close()
    if not rows or [r[0] for r in rows] != list(range(len(rows))):
        raise ValueError('Missing or non-contiguous ledger history')
    history = []
    for rev, eid, request, state in rows:
        state = json.loads(state)
        validate(state)
        history.append({'revision': rev, 'event_id': eid, 'request': json.loads(request), 'state': state})
    return history


def active_history(history):
    branches = {0: [history[0]]}
    for row in history[1:]:
        changes = row['request']['changes']
        restore = [c for c in changes if c['kind'] == 'restore']
        if restore:
            target = restore[0]['revision']
            if len(changes) != 1 or target not in branches:
                raise ValueError('Invalid restore ancestry')
            branches[row['revision']] = branches[target] + [row]
        else:
            branches[row['revision']] = branches[row['revision'] - 1] + [row]
    return branches[history[-1]['revision']]


def recap(path, since=0, player=None, gm=False):
    history = read_history(path)
    if type(since) is not int or since < 0 or since > history[-1]['revision']:
        raise ValueError('since must be an existing revision')
    active = active_history(history)
    current = history[-1]['state']
    visible = lambda r: gm or 'all' in r['audience'] or (player is not None and player in r['audience'])
    facts = []
    for f in current['facts']:
        if not visible(f):
            continue
        # Match full fact, including audience: later disclosure has its own provenance.
        origin = next(r for r in active if f in r['state']['facts'])
        if origin['revision'] < since:
            continue
        entry = {'text': f['text'], 'source_revision': origin['revision']}
        if gm:
            entry.update(fact_id=f['id'], event_id=origin['event_id'], audience=f['audience'])
        facts.append(entry)
    result = {'revision': history[-1]['revision'], 'since_inclusive': since,
              'recorded_facts': facts,
              'actors': [{'name': a['name'], 'resources': a['resources'], 'conditions': a['conditions']}
                         for a in current['actors'].values() if visible(a)]}
    if gm:
        result['events'] = [{'revision': r['revision'], 'event_id': r['event_id'],
                             'input': r['request']['input'], 'resolution': r['request']['resolution'],
                             'sources': r['request']['sources']}
                            for r in active if r['revision'] and r['revision'] >= since]
        result['pending'] = current['pending']
        # Optional, explicit categories; never infer player beliefs from GM truth.
        review = current['private'].get('review', {})
        if not isinstance(review, dict):
            raise ValueError('private.review must be an object')
        for key in ('player_hypotheses', 'gm_plans', 'character_hooks'):
            items = review.get(key, [])
            if not isinstance(items, list) or any(not isinstance(i, str) for i in items):
                raise ValueError('Review categories must be lists of strings')
            result[key] = items
        result['next_prep'] = {
            'resolve_pending': current['pending'],
            'revisit_character_hooks': result['character_hooks'],
            'evaluate_unrealized_plans': result['gm_plans'],
            'verify_player_hypotheses': result['player_hypotheses']}
        result['state_source_revision'] = history[-1]['revision']
        result['superseded_revisions'] = sorted(set(r['revision'] for r in history) - set(r['revision'] for r in active))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('database', type=Path)
    p.add_argument('--since', type=int, default=0, help='Inclusive revision filter; actors always show current state')
    g = p.add_mutually_exclusive_group()
    g.add_argument('--gm', action='store_true')
    g.add_argument('--player')
    a = p.parse_args()
    try:
        print(json.dumps(recap(a.database, a.since, a.player, a.gm), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as e:
        p.exit(2, str(e) + '\n')


if __name__ == '__main__':
    main()
