from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from rulebook_check import audit
from rulebook_demo import initial, apply, grow, run, events, resolve, validate, probabilities

BASE = Path(__file__).resolve().parents[1] / 'assets/examples/rulebook'

class RulebookManifestTests(unittest.TestCase):
    def fixture(self):
        return json.loads((BASE/'dream/project.json').read_text(encoding='utf-8'))

    def test_complete_project_and_transitive_impact(self):
        result = audit(self.fixture(), BASE/'dream', 'R-memory')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['affected'], ['book','cards','playthrough','quickstart','scenario'])

    def test_conflict_and_repair(self):
        before = json.loads((BASE/'conflict/before.json').read_text(encoding='utf-8'))
        after = json.loads((BASE/'conflict/after.json').read_text(encoding='utf-8'))
        errors = audit(before, BASE/'conflict')['errors']
        for fragment in ('conflicting claim','stale binding','open material'):
            self.assertTrue(any(fragment in x for x in errors))
        result = audit(after, BASE/'conflict', 'battery')
        self.assertEqual(result['errors'], [])
        self.assertEqual(len(result['affected']), 5)

    def test_missing_rule_contract_and_file(self):
        p = self.fixture()
        p['rules'][0]['contract'].pop('outcomes')
        p['rules'][1]['file'] = 'absent.md'
        errors = audit(p, BASE/'dream')['errors']
        self.assertTrue(any('outcomes' in x for x in errors))
        self.assertTrue(any('absent.md' in x for x in errors))

    def test_duplicate_cycles_unknown_and_stale(self):
        p = self.fixture()
        p['rules'].append(deepcopy(p['rules'][0]))
        p['rules'][0]['depends_on'] = ['R-grow', 'missing']
        p['rules'][-1]['depends_on'] = ['R-grow', 'missing']
        p['artifacts'][0]['bindings']['R-create'] = 1
        errors = audit(p, BASE/'dream')['errors']
        for fragment in ('duplicate', 'cycle', 'unknown dependency', 'stale'):
            self.assertTrue(any(fragment in x for x in errors))

    def test_private_transitive_dependency(self):
        p = self.fixture()
        p['rules'][0]['file'] = 'scenario.md'
        self.assertTrue(any('GM rule' in x for x in audit(p, BASE/'dream')['errors']))

    def test_path_escape_and_bad_types(self):
        p = self.fixture()
        p['rules'][0]['file'] = '../courier.md'
        p['version'] = True
        p['issues'][0]['material'] = 'false'
        errors = audit(p, BASE/'dream')['errors']
        self.assertTrue(any('unsafe' in x for x in errors))
        self.assertTrue(any('version' in x for x in errors))
        self.assertTrue(any('material flag' in x for x in errors))
        self.assertEqual(audit([], BASE)['status'], 'invalid')

    def test_new_rule_revision_invalidates_bound_cards(self):
        p = self.fixture()
        p['rules'][0]['revision'] = 3
        result = audit(p, BASE/'dream', 'R-create')
        self.assertEqual(len([x for x in result['errors'] if 'stale' in x]), 5)

class DreamPrototypeTests(unittest.TestCase):
    def test_creation_and_twenty_turn_outcomes(self):
        state, trace = run(initial(), events())
        self.assertEqual(len(trace), 20)
        self.assertEqual(state['archives'], 2)
        self.assertTrue(state['ended'])
        self.assertEqual([t['calculation']['scene_end'].startswith('complete') for t in trace if t['turn']%5==0], [True,False,False,True])
        self.assertEqual([state['actors'][x]['strain'] for x in ('A','B')], [4,2])
        self.assertEqual(sum(sum(a['memories'].values()) for a in state['actors'].values()), 0)
        self.assertEqual(trace[14]['after']['actors']['A']['strain'],6)

    def test_known_probability_boundaries(self):
        self.assertEqual(resolve(0,1), {'total':1,'progress_gain':0,'strain_gain':2})
        self.assertEqual(resolve(2,1)['progress_gain'],1)
        self.assertEqual(resolve(2,3)['progress_gain'],2)
        self.assertEqual(resolve(2,1,2)['progress_gain'],2)
        self.assertEqual(probabilities()[0]['full'], '1/3')
        for bad in (True,0,7):
            with self.assertRaises(ValueError): resolve(1,bad)

    def test_faded_trade_cannot_refresh_and_illegal_payment_atomic(self):
        s,_ = apply(initial(), dict(actor='A',kind='delve',skill='trace',die=2,spend=['A-0']))
        s,_ = apply(s, dict(actor='A',kind='trade',give='A-0',take='B-0',consent=True))
        s,_ = apply(s, dict(actor='B',kind='trade',give='A-0',take='B-0',consent=True))
        self.assertFalse(s['actors']['A']['memories']['A-0'])
        before=deepcopy(s)
        with self.assertRaises(ValueError): apply(s, dict(actor='A',kind='delve',skill='trace',die=6,spend=['A-0']))
        self.assertEqual(s,before)

    def test_help_expiry_stacking_and_zero_memory_action(self):
        s,_=apply(initial(),dict(actor='A',kind='help',spend=['A-0']))
        with self.assertRaises(ValueError): apply(s,dict(actor='A',kind='help',spend=['A-1']))
        for _ in range(4): s,_=apply(s,dict(actor='A',kind='wait'))
        self.assertEqual(s['actors']['B']['help'],0)
        s['actors']['A']['memories']={k:False for k in s['actors']['A']['memories']}
        s,_=apply(s,dict(actor='A',kind='delve',skill='trace',die=3,spend=[]))
        self.assertEqual(s['progress'],2)

    def test_fracture_recovery_once_and_deadlock_escape(self):
        s=initial();s['actors']['A']['strain']=6
        with self.assertRaises(ValueError): apply(s,dict(actor='A',kind='help',spend=['A-0']))
        s,_=apply(s,dict(actor='A',kind='recover'))
        self.assertEqual(s['actors']['A']['strain'],4)
        with self.assertRaises(ValueError): apply(s,dict(actor='A',kind='recover'))
        s['actors']['A']['strain']=6
        for _ in range(4): s,_=apply(s,dict(actor='A',kind='wait'))
        self.assertEqual(s['turn'],5)
        self.assertFalse(s['actors']['A']['recovered'])

    def test_snapshot_version_and_memory_integrity(self):
        s,_=run(initial(),events()[:10])
        resumed,_=run(json.loads(json.dumps(s)),events()[10:])
        direct,_=run(initial(),events())
        self.assertEqual(resumed,direct)
        s['version']='old'
        with self.assertRaises(ValueError): validate(s)
        s=initial();s['actors']['B']['memories']['A-0']=True
        with self.assertRaises(ValueError): validate(s)

    def test_growth_once_no_resource_refill_and_invalid_action(self):
        s,_=run(initial(),events())
        after=grow(s,'A','listen')
        self.assertEqual(after['actors']['A']['skills']['listen'],2)
        self.assertEqual(after['actors']['A']['memories'],s['actors']['A']['memories'])
        self.assertEqual(after['actors']['A']['strain'],4)
        with self.assertRaises(ValueError): grow(after,'A','weave')
        with self.assertRaises(ValueError): grow(initial(),'A','listen')
        with self.assertRaises(ValueError): apply(s,dict(actor='A',kind='wait'))
        with self.assertRaises(ValueError): apply(initial(),dict(actor='A',kind='invent'))
        with self.assertRaises(ValueError): apply(initial(),dict(actor='A',kind='delve',skill='trace',die=5,spend=['A-0','A-0']))

if __name__ == '__main__':
    unittest.main()
