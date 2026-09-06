import copy
import json
from pathlib import Path
import unittest
from background_chargen import audit,player_view,budget

ROOT=Path(__file__).resolve().parents[1]/'assets/examples/background-chargen'


class BackgroundCreation(unittest.TestCase):
    def setUp(self):
        self.spec=json.loads((ROOT/'monastery/spec.json').read_text(encoding='utf-8'))

    def test_six_complete_cards_and_budgets(self):
        for case in ['monastery','railway','harbor']:
            spec=json.loads((ROOT/case/'spec.json').read_text(encoding='utf-8'))
            result=audit(spec)
            self.assertEqual(result['status'],'passed configured arithmetic')
            self.assertEqual(len(result['cards']),2)
            self.assertFalse(result['coverage_gaps'])
            self.assertEqual([c['interest_spent'] for c in result['cards']],[150,150])
            self.assertEqual(result['cards'][0]['derived']['hp'],12)
        self.assertEqual([c['occupation_budget'] for c in audit(self.spec)['cards']],[280,240])

    def test_budget_overrun_and_base_override(self):
        self.spec['characters'][0]['allocations'][0]['occupation']+=1
        self.assertEqual(audit(self.spec)['status'],'invalid')
        self.spec['characters'][0]['allocations'][0]['base']=50
        with self.assertRaises(ValueError):audit(self.spec)

    def test_unknown_specialty_and_cap(self):
        self.spec['characters'][0]['allocations'][0]['skill']='Unsupported Ancient Science'
        self.assertTrue(any('unknown' in e for e in audit(self.spec)['errors']))
        self.spec['skill_cap']=30
        self.assertTrue(any('skill cap' in e for e in audit(self.spec)['errors']))

    def test_edition_conflict(self):
        self.spec['characters'][0]['profile']=dict(self.spec['profile'],edition='6e')
        self.assertTrue(any('profile conflict' in e for e in audit(self.spec)['errors']))
        self.spec['profile']['system']='D&D'
        with self.assertRaises(ValueError):audit(self.spec)

    def test_missing_source_and_unapproved_house_rule_are_drafts(self):
        del self.spec['sources']['core']
        self.assertEqual(audit(self.spec)['status'],'draft')
        self.spec['house_rules_approved']=False
        self.assertIn('House rules not approved',audit(self.spec)['pending'])

    def test_anachronistic_equipment_and_overspending(self):
        self.spec['characters'][0]['equipment'].append('smartphone')
        self.assertTrue(any('unavailable equipment' in e for e in audit(self.spec)['errors']))
        self.spec['characters'][0]['wealth']['equipment_cost']=100
        self.assertTrue(any('wealth accounting' in e for e in audit(self.spec)['errors']))

    def test_secret_projection_and_duplicate_id(self):
        self.spec['characters'][0]['gm_secret']='GM_CARD_ONLY'
        public=json.dumps(player_view(audit(self.spec)))
        self.assertNotIn('GM_ONLY_FIXTURE_SECRET',public)
        self.assertNotIn('GM_CARD_ONLY',public)
        self.spec['characters'][1]['id']=self.spec['characters'][0]['id']
        self.assertEqual(audit(self.spec)['status'],'invalid')

    def test_booleans_and_formula_injection(self):
        with self.assertRaises(ValueError):budget({'EDU':True},{'EDU':70})
        with self.assertRaises(ValueError):budget('__import__("os")',{'EDU':70})

    def test_points_cannot_enter_wrong_occupation_or_mythos(self):
        row=self.spec['characters'][0]['allocations'][0]
        row['skill']='Cthulhu Mythos'
        errors=audit(self.spec)['errors']
        self.assertTrue(any('not eligible' in e for e in errors))
        self.assertTrue(any('interest prohibited' in e for e in errors))
