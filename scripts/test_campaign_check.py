import copy
import unittest
from campaign_check import audit, projection


class CampaignAudit(unittest.TestCase):
    def setUp(self):
        self.plan = {'start': 'gate', 'nodes': [
            {'id': 'gate', 'leads_to': ['office', 'exit']},
            {'id': 'office', 'leads_to': ['gate']},
            {'id': 'exit', 'leads_to': [], 'exit': True}],
            'clues': [{'id': 'secret', 'node': 'office', 'reveals': 'exit', 'audience': []},
                      {'id': 'letter', 'node': 'gate', 'reveals': 'office', 'audience': ['pc1']}]}

    def test_cycle_with_exit(self):
        self.assertTrue(audit(self.plan)['ok'])

    def test_broken_reference_and_unreachable(self):
        p = copy.deepcopy(self.plan)
        p['nodes'][0]['leads_to'] = ['typo']
        errors = audit(p)['errors']
        self.assertTrue(any('unknown destination' in e for e in errors))
        self.assertIn('no reachable exit', errors)
        self.assertIn('unreachable node: office', errors)

    def test_duplicate_and_private_projection(self):
        self.plan['clues'].append(copy.deepcopy(self.plan['clues'][0]))
        self.assertFalse(audit(self.plan)['ok'])
        self.assertEqual(projection(self.plan, 'pc2'), {'clues': []})
        self.assertEqual([c['id'] for c in projection(self.plan, 'pc1')['clues']], ['letter'])
