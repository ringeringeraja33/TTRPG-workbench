import json
from pathlib import Path
import tempfile
import unittest
from session import init, apply, view
from session_review import recap


class SessionReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / '中文.sqlite'
        self.profile = {'system': 'fixture', 'edition': '1', 'options': {}}
        init(self.path, {'profile': self.profile, 'actors': {}, 'facts': [], 'private': {}, 'pending': [], 'clock': 0})

    def event(self, changes, eid=None):
        rev = view(self.path, gm=True)['revision']
        apply(self.path, {'id': eid or f'GM-secret-{rev}', 'revision': rev, 'profile': self.profile,
                          'input': 'secret input', 'resolution': 'secret resolution',
                          'sources': ['fixture GM ruling'], 'changes': changes})

    def fact(self, name, audience):
        return {'kind': 'fact', 'value': {'id': name, 'text': name, 'audience': audience}}

    def test_public_and_individual_projection(self):
        self.event([self.fact('public', ['all']), self.fact('only-pc1', ['pc1']), self.fact('GM', []),
                    {'kind': 'private', 'value': {'review': {'gm_plans': ['unrealized trap']}}}])
        public = json.dumps(recap(self.path))
        self.assertNotIn('secret', public)
        self.assertNotIn('GM', public)
        self.assertNotIn('trap', public)
        self.assertEqual([f['text'] for f in recap(self.path, player='pc1')['recorded_facts']], ['public', 'only-pc1'])
        self.assertEqual(recap(self.path, gm=True)['next_prep']['evaluate_unrealized_plans'], ['unrealized trap'])

    def test_restore_removes_abandoned_events_and_facts(self):
        self.event([self.fact('kept', ['all'])])
        self.event([self.fact('abandoned', ['all'])])
        self.event([{'kind': 'restore', 'revision': 1}])
        self.event([self.fact('new', ['all'])])
        result = recap(self.path, gm=True)
        self.assertEqual(result['superseded_revisions'], [2])
        self.assertEqual([f['source_revision'] for f in result['recorded_facts']], [1, 4])
        self.assertNotIn('abandoned', json.dumps(result))

    def test_restore_to_abandoned_branch(self):
        self.event([self.fact('first', ['all'])])
        self.event([self.fact('second', ['all'])])
        self.event([{'kind': 'restore', 'revision': 0}])
        self.event([{'kind': 'restore', 'revision': 2}])
        self.assertEqual([f['text'] for f in recap(self.path)['recorded_facts']], ['first', 'second'])

    def test_since_and_read_only(self):
        self.event([self.fact('old', ['all'])])
        self.event([self.fact('new', ['all'])])
        before = self.path.read_bytes()
        self.assertEqual([f['text'] for f in recap(self.path, since=2)['recorded_facts']], ['new'])
        self.assertEqual(before, self.path.read_bytes())
        with self.assertRaises(ValueError):
            recap(self.path, since=3)
        missing = self.path.with_name('missing.sqlite')
        with self.assertRaises(FileNotFoundError):
            recap(missing)
        self.assertFalse(missing.exists())


if __name__ == '__main__':
    unittest.main()
