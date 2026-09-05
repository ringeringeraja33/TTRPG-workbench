import copy
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

import session
import rules_math as rules


def initial():
    return json.loads((Path(__file__).resolve().parents[1] / 'assets/templates/session-initial.json').read_text(encoding='utf-8'))


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / '中文战役.sqlite'
        self.state = initial()
        session.init(self.path, self.state)

    def event(self, **overrides):
        event = {'id': 'e1', 'revision': 0, 'profile': self.state['profile'], 'input': '我检查门闩。',
                 'resolution': '预设测试输入；受到2点擦伤。', 'sources': ['GM原创风险'],
                 'changes': [{'kind': 'resource', 'actor': 'pc1', 'resource': 'hp', 'delta': -2}]}
        event.update(overrides)
        return event

    def test_upgrade_retains_spent_capacity_and_restore(self):
        session.apply(self.path, self.event())
        e = self.event(id='upgrade', revision=1, changes=[
            {'kind': 'resize', 'actor': 'pc1', 'resource': 'hp', 'maximum': 20}])
        session.apply(self.path, e)
        hp = session.view(self.path, gm=True)['state']['actors']['pc1']['resources']['hp']
        self.assertEqual(hp, {'value': 18, 'max': 20})
        self.assertTrue(session.apply(self.path, e)['duplicate'])
        session.apply(self.path, self.event(id='undo-upgrade', revision=2,
                      changes=[{'kind': 'restore', 'revision': 1}]))
        self.assertEqual(session.view(self.path, gm=True)['state']['actors']['pc1']['resources']['hp']['max'], 12)

    def test_invalid_resize_rolls_back_prior_spend(self):
        with self.assertRaises(ValueError):
            session.apply(self.path, self.event(changes=[
                {'kind': 'resource', 'actor': 'pc1', 'resource': 'hp', 'delta': -2},
                {'kind': 'resize', 'actor': 'pc1', 'resource': 'hp', 'maximum': True}]))
        self.assertEqual(session.view(self.path, gm=True)['revision'], 0)

    def test_duplicate_does_not_spend_twice(self):
        e = self.event()
        session.apply(self.path, e)
        self.assertTrue(session.apply(self.path, e)['duplicate'])
        self.assertEqual(session.view(self.path, gm=True)['state']['actors']['pc1']['resources']['hp']['value'], 10)

    def test_reused_id_with_changed_dice_rejected(self):
        session.apply(self.path, self.event())
        with self.assertRaises(ValueError):
            session.apply(self.path, self.event(resolution='不同骰子'))

    def test_stale_revision_rejected(self):
        session.apply(self.path, self.event())
        with self.assertRaises(ValueError):
            session.apply(self.path, self.event(id='e2'))

    def test_profile_conflict_no_mutation(self):
        p = copy.deepcopy(self.state['profile'])
        p['edition'] = '6e'
        with self.assertRaises(ValueError):
            session.apply(self.path, self.event(profile=p))
        self.assertEqual(session.view(self.path, gm=True)['revision'], 0)

    def test_missing_source_rejected(self):
        with self.assertRaises(ValueError):
            session.apply(self.path, self.event(sources=[]))

    def test_missing_rule_stays_pending_without_spending(self):
        event = self.event(sources=['GM: rule not found; defer resolution'], changes=[{'kind': 'pending', 'value': [{'rule': '未知法术', 'needed': '当前版本正文', 'status': 'unresolved'}]}])
        session.apply(self.path, event)
        state = session.view(self.path, gm=True)['state']
        self.assertEqual(state['actors'], self.state['actors'])
        self.assertEqual(state['pending'][0]['status'], 'unresolved')

    def test_dnd_edition_mismatch_is_not_migrated(self):
        path = Path(self.temp.name) / 'dnd.sqlite'
        state = initial()
        state['profile'] = {'system': 'D&D', 'edition': 'SRD5.2.1', 'options': {}}
        session.init(path, state)
        with self.assertRaises(ValueError):
            session.apply(path, self.event(profile={'system': 'D&D', 'edition': '2014', 'options': {}}))
        self.assertEqual(session.view(path, gm=True)['revision'], 0)

    def test_all_changes_atomic(self):
        changes = self.event()['changes'] + [{'kind': 'resource', 'actor': 'pc1', 'resource': 'mp', 'delta': -99}]
        with self.assertRaises(ValueError):
            session.apply(self.path, self.event(changes=changes))
        self.assertEqual(session.view(self.path, gm=True)['state'], self.state)
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM events').fetchone()[0], 1)

    def test_restore_appends_history(self):
        session.apply(self.path, self.event())
        session.apply(self.path, self.event(id='restore', revision=1, changes=[{'kind': 'restore', 'revision': 0}]))
        self.assertEqual(session.view(self.path, gm=True), {'revision': 2, 'state': self.state})

    def test_secret_projection_and_split_party(self):
        changes = [{'kind': 'fact', 'value': {'id': str(i), 'text': text, 'audience': who}} for i, (text, who) in enumerate([
            ('公开入口', ['all']), ('甲队看见的账本', ['pc1']), ('乙队听见的口令', ['pc2']), ('幕后秘密', [])])]
        changes += [{'kind': 'pending', 'value': ['秘密事件等待触发']}, {'kind': 'private', 'value': {'hidden': '真凶周衡'}}]
        session.apply(self.path, self.event(changes=changes))
        public = session.encode(session.view(self.path))
        player = session.encode(session.view(self.path, player='pc1'))
        self.assertNotIn('甲队', public)
        self.assertIn('甲队', player)
        for secret in ['乙队', '幕后', '真凶', '等待触发']:
            self.assertNotIn(secret, player)

    def test_parallel_writers_cannot_overwrite(self):
        def write(i):
            try:
                session.apply(self.path, self.event(id=f'race{i}'))
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(write, [1, 2])), 1)
        self.assertEqual(session.view(self.path, gm=True)['revision'], 1)

    def test_init_does_not_overwrite(self):
        with self.assertRaises(FileExistsError):
            session.init(self.path, self.state)

    def test_boolean_and_overhealing_rejected(self):
        for delta in [True, 1]:
            with self.assertRaises(ValueError):
                session.apply(self.path, self.event(changes=[{'kind': 'resource', 'actor': 'pc1', 'resource': 'hp', 'delta': delta}]))

    def test_invalid_container_rejected_before_write(self):
        with self.assertRaises(ValueError):
            session.apply(self.path, self.event(changes={}))
        self.assertEqual(session.view(self.path, gm=True)['revision'], 0)


class RulesBoundaryTests(unittest.TestCase):
    def test_outnumbered_bonus_does_not_accumulate(self):
        self.assertEqual([rules.coc_outnumbered_bonus(n) for n in [0, 1, 2, 3]], [0, 1, 1, 1])
        self.assertEqual([rules.coc_outnumbered_bonus(n, 3) for n in [0, 2, 3, 4]], [0, 0, 1, 1])

    def test_melee_equal_success_defense_changes_winner(self):
        self.assertEqual(rules.coc_melee(60, 45, 60, 40, 'dodge'), 'dodged')
        self.assertEqual(rules.coc_melee(60, 45, 60, 40, 'fight_back'), 'attacker_hits')
        self.assertEqual(rules.coc_melee(60, 99, 60, 98, 'fight_back'), 'no_hit')

    def test_fumble_and_high_skill(self):
        self.assertEqual(rules.coc_result(49, 96), 'fumble')
        self.assertEqual(rules.coc_result(50, 96), 'failure')
        self.assertEqual(rules.coc_result(110, 100), 'fumble')
        self.assertEqual(rules.coc_result(0, 1), 'critical')

    def test_sanity_daily_and_temporary_separate(self):
        a = rules.coc_sanity(60, 60, 0, 5)
        self.assertTrue(a['int_required'])
        self.assertFalse(a['indefinite'])
        b = rules.coc_sanity(49, 60, 11, 1)
        self.assertTrue(b['indefinite'])
        self.assertFalse(b['temporary'])
        self.assertEqual(rules.coc_sanity(60, 60, 0, 5, in_bout=True)['san'], 60)

    def test_development_above_95_and_above_100(self):
        self.assertEqual(rules.coc_development(100, 96, 4), 104)
        self.assertEqual(rules.coc_development(80, 80, 4), 80)
        self.assertEqual(rules.coc_development(80, 81, 4), 84)

    def test_concentration_cap_and_rounding(self):
        self.assertEqual([rules.dnd_concentration_dc(d) for d in [1, 21, 23, 100]], [10, 10, 11, 30])

    def test_chase_slowest_participant_not_slowest_pursuer(self):
        # First runner is the fleeing PC; second and third are pursuers.
        self.assertEqual(rules.coc_chase_points([5, 7, 8]), [1, 3, 4])
        with self.assertRaises(ValueError):
            rules.coc_chase_points([])

    def test_death_save_nat_one_twenty_and_stability(self):
        self.assertEqual(rules.dnd_death_save(1, failures=1)['state'], 'dead')
        self.assertEqual(rules.dnd_death_save(20, failures=2)['hp'], 1)
        self.assertEqual(rules.dnd_death_save(10, successes=2), {'hp': 0, 'successes': 0, 'failures': 0, 'state': 'stable'})


if __name__ == '__main__':
    unittest.main()
