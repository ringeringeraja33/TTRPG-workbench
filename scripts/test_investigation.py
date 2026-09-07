import copy
import unittest
from investigation import audit, projection


class InvestigationTests(unittest.TestCase):
    def setUp(self):
        self.plan = {'schema': 1, 'evidence': [
            {'id': 'letter', 'text': '信提到北门。', 'available': True, 'audience': ['pc1']},
            {'id': 'witness', 'text': 'Witness saw the cart.', 'available': True, 'audience': ['pc2']},
            {'id': 'map', 'text': 'Map', 'available': True, 'audience': ['all']}],
            'conclusions': [
                {'id': 'route', 'text': 'Secret destination', 'audience': [], 'essential': True,
                 'routes': [['letter'], ['witness', 'map']]},
                {'id': 'culprit', 'text': 'Hidden culprit', 'audience': [], 'essential': True,
                 'routes': [['route', 'map']]}]}

    def test_alternatives_and_and_groups(self):
        self.assertTrue(audit(self.plan, ['letter'])['ok'])
        self.assertFalse(audit(self.plan, ['letter', 'map'])['ok'])
        self.assertEqual(audit(self.plan)['single_evidence_bottlenecks'], {'map': ['culprit']})

    def test_cycle_needs_external_seed(self):
        self.plan['conclusions'][0]['routes'] = [['culprit']]
        self.assertEqual(audit(self.plan)['blocked_essential'], ['culprit', 'route'])
        self.plan['conclusions'][0]['routes'].append(['letter'])
        self.assertTrue(audit(self.plan)['ok'])

    def test_split_knowledge_does_not_merge(self):
        self.plan['conclusions'][0]['routes'] = [['letter', 'witness']]
        self.assertTrue(audit(self.plan)['ok'])
        self.assertFalse(audit(self.plan, player='pc1')['ok'])

    def test_projection_does_not_reveal_routes_or_extra_fields(self):
        self.plan['evidence'][0]['gm_secret'] = 'culprit'
        self.assertEqual(projection(self.plan, 'pc1'), {'evidence': [{'text': '信提到北门。'}, {'text': 'Map'}]})

    def test_invalid_and_unavailable(self):
        with self.assertRaises(ValueError):
            audit(self.plan, ['typo'])
        self.plan['conclusions'][0]['routes'] = [['typo']]
        with self.assertRaises(ValueError):
            audit(self.plan)
        self.plan['conclusions'][0]['routes'] = []
        self.assertFalse(audit(self.plan)['ok'])

    def test_missing_evidence_not_given_to_players(self):
        self.plan['evidence'][0]['available'] = False
        self.assertEqual(projection(self.plan, 'pc1'), {'evidence': [{'text': 'Map'}]})


if __name__ == '__main__':
    unittest.main()
