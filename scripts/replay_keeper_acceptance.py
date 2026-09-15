"""Run original synthetic Keeper situations through existing persistence interfaces.

No model-generated decisions, live players, dice, external delivery or source PDF.
The case responses are worked examples, not proof of autonomous hosting quality.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import handout_manifest
import investigation

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    path.write_text(text, encoding='utf-8')
    if json.loads(path.read_text(encoding='utf-8')) != value:
        raise AssertionError('UTF-8 roundtrip failed')


def cli(db, *args, success=True):
    run = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/session.py'),
                          str(db), *map(str, args)], capture_output=True,
                         encoding='utf-8')
    if (run.returncode == 0) != success:
        raise AssertionError(run.stderr or run.stdout)
    return json.loads(run.stdout) if success else run.stderr


def run_case(case, folder):
    folder.mkdir()
    actors = {p: {'name': name, 'audience': [p],
                  'resources': {'hp': {'value': 10, 'max': 12},
                                'san': {'value': 48, 'max': 99}},
                  'conditions': ['indefinite insanity'] if p == 'pc1' else []}
              for p, name in [('pc1', '林蔚'), ('pc2', '沈青')]}
    initial = {'profile': {'system': 'CoC', 'edition': '7e', 'options': {}},
               'actors': actors, 'facts': [
                   {'id': 'destroyed', 'text': 'The original register was destroyed.', 'audience': ['all']},
                   {'id': 'culprit', 'text': 'GM truth: the station owner is responsible.', 'audience': []}],
               'clock': 90, 'pending': ['Earlier unresolved vehicle question.'],
               'private': {'san_day_start': 60, 'san_day_loss': 12,
                           'inventory': {'pc2': ['pencil', 'dictionary']},
                           'next_actor': 'pc1',
                           'review': {'gm_plans': ['Untriggered storm.'],
                                      'character_hooks': ['Return borrowed dictionary.'],
                                      'player_hypotheses': []},
                           'keeper': {'agreement': {'pause': 'pause', 'absence': 'safe fade'}}}}
    write(folder / 'initial.json', initial)
    db = folder / 'campaign.sqlite'
    cli(db, 'init', '--config', folder / 'initial.json')
    # Read real state before replacement; retain unrelated pending and private fields.
    saved = cli(db, 'view', '--gm')
    private = copy.deepcopy(saved['state']['private'])
    private['keeper'].update(copy.deepcopy(case['keeper']))
    private['keeper']['last_case'] = {'id': case['id'], 'diagnosis': case['diagnosis'],
                                    'next_choice': case['next_choice']}
    private['next_actor'] = 'pc2' if case['id'] == 'split-party' else 'pc1'
    private['review']['player_hypotheses'].extend(case.get('hypotheses', []))
    event = {'id': 'keeper-' + case['id'], 'revision': saved['revision'],
             'profile': initial['profile'], 'input': 'Synthetic situation: ' + case['situation'],
             'resolution': case['response'],
             'sources': ['Original worked case; Keeper Tips translated PDF pp. ' +
                         ', '.join(map(str, case['source_pages'])) + '; guidance, not RAW'],
             'changes': [{'kind': 'private', 'value': private},
                         {'kind': 'pending', 'value': initial['pending'] + case['pending']}]
                        + [{'kind': 'fact', 'value': f} for f in case['facts']]}
    write(folder / 'event.json', event)
    applied = cli(db, 'apply', '--event', folder / 'event.json')
    restored = cli(db, 'view', '--gm')  # separate process for every read
    assert restored['revision'] == applied['revision'] == 1
    state = restored['state']
    assert state['actors'] == initial['actors']
    assert state['clock'] == initial['clock']
    assert state['facts'][:2] == initial['facts']
    assert state['private'] == private
    assert state['pending'] == initial['pending'] + case['pending']
    again = cli(db, 'apply', '--event', folder / 'event.json')
    assert again['duplicate'] and again['state_sha256'] == applied['state_sha256']
    assert cli(db, 'view', '--gm') == restored
    for player in ['pc1', 'pc2']:
        public = cli(db, 'view', '--player', player)
        assert 'private' not in public and 'pending' not in public
        assert all(f['id'] != 'culprit' for f in public['facts'])
        assert public['facts'] == [f for f in state['facts']
                                   if 'all' in f['audience'] or player in f['audience']]
        write(folder / (player + '.json'), public)

    if case['id'] == 'missed-clue':
        plan = {'schema': 1, 'evidence': [
            {'id': 'original', 'text': 'Original schedule', 'available': False, 'audience': []},
            {'id': 'duplicate', 'text': 'Customs schedule', 'available': True, 'audience': []}],
            'conclusions': [{'id': 'time', 'text': 'Departure time', 'essential': True,
                             'audience': [], 'routes': [['original'], ['duplicate']]}]}
        assert investigation.audit(plan)['ok']
        assert not investigation.audit(plan, player='pc1')['ok']
        assert not investigation.audit(plan, unavailable=['duplicate'])['ok']
        write(folder / 'evidence-audit.json', investigation.audit(plan))

    if case['id'] == 'rule-dispute':
        conflict = copy.deepcopy(event)
        conflict.update(id='changed-edition', revision=1)
        conflict['profile']['edition'] = '6e'
        write(folder / 'conflict.json', conflict)
        error = cli(db, 'apply', '--event', folder / 'conflict.json', success=False)
        assert 'profile conflict' in error
        assert cli(db, 'view', '--gm') == restored
        write(folder / 'expected-rejection.json', {'reason': 'profile conflict', 'state_unchanged': True})

    if case['id'] == 'unreadable-handout':
        text = '夜班钥匙在长椅下。'
        for name, body in [('plain.txt', text), ('styled.txt', text),
                           ('gm.txt', 'GM truth: station owner is responsible.')]:
            (folder / name).write_text(body, encoding='utf-8')
        variants = {n: {'path': n + '.txt',
                        'sha256': hashlib.sha256((folder / (n + '.txt')).read_bytes()).hexdigest(),
                        'review': 'gm-only' if n == 'gm' else 'player-safe'}
                    for n in ['plain', 'styled', 'gm']}
        manifest = {'revealed_facts': ['letter-opened'], 'handouts': [{
            'id': 'letter', 'audience': 'individual', 'recipients': ['pc1'],
            'released': True, 'requires': ['letter-opened'], 'player_title': '夜班信件',
            'player_text': text, 'selected_variant': 'plain', 'variants': variants}]}
        assert not handout_manifest.validate(manifest, folder)
        assert handout_manifest.project(manifest, 'pc1', folder)['handouts'][0]['text'] == text
        assert not handout_manifest.project(manifest, 'pc2', folder)['handouts']
        assert (folder / 'plain.txt').read_bytes() == (folder / 'styled.txt').read_bytes()
        unsafe = copy.deepcopy(manifest)
        unsafe['handouts'][0]['selected_variant'] = 'gm'
        assert handout_manifest.validate(unsafe, folder)
        write(folder / 'manifest.json', manifest)
        write(folder / 'readable-player-handout.json', handout_manifest.project(manifest, 'pc1', folder))
        # Simulates a readability decision; typography itself is not tested here.

    return {'id': case['id'], 'passed': True, 'revision': 1,
            'fresh_process_recovery': True, 'identical_retry': True,
            'resources_unchanged': True, 'audience_filter': True,
            'worked_response': case['response'], 'next_choice': case['next_choice'],
            'reviewed_boundary': case['must_preserve']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New private output directory')
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT.resolve()):
        parser.error('Acceptance artifacts must remain outside the distributed skill')
    args.output.mkdir(parents=True, exist_ok=False)
    cases = json.loads((ROOT / 'assets/examples/keeper-practice-cases.json').read_text(encoding='utf-8'))['cases']
    results = []
    try:
        for case in cases:
            results.append(run_case(case, args.output / case['id']))
    except Exception as error:
        write(args.output / 'report.json', {'passed': False, 'completed': results,
                                           'failed_case': case['id'], 'error': str(error)})
        raise
    report = {'passed': True, 'cases': results, 'scope': 'Eight prewritten synthetic responses with executable persistence checks; no autonomous GM or live-player certification.',
              'utf8_readback': 'OK', 'dice_used': False}
    write(args.output / 'report.json', report)
    print(json.dumps({'passed': True, 'cases': len(results), 'utf8_readback': 'OK'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
