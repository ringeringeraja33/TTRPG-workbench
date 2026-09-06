from copy import deepcopy
import json
from pathlib import Path
import unittest
import background_design as design

BASE=Path(__file__).resolve().parents[1]/'assets/examples'

def inputs(case='harbor'):
    return (json.loads((BASE/'background-design'/case/'pack.json').read_text(encoding='utf-8')),
            json.loads((BASE/'background-chargen'/case/'spec.json').read_text(encoding='utf-8')))

class BackgroundDesignTests(unittest.TestCase):
    def test_three_packs_six_characters_and_nine_scenes(self):
        for case in ('monastery','railway','harbor'):
            pack,spec=inputs(case);result=design.audit(pack,spec)
            self.assertEqual(result['status'],'passed explicit checks',result)
            self.assertEqual(len(result['characters']),2)
            self.assertEqual(len(pack['scenes']),3)
            for c in result['characters']:
                self.assertEqual(c['occupation_spent'],c['occupation_budget'])
                self.assertEqual(c['interest_spent'],150)

    def test_no_special_skill_or_item_failure_walk(self):
        for case in ('monastery','railway','harbor'):
            pack,spec=inputs(case)
            self.assertEqual(design.walk(pack,True),[s['id'] for s in pack['scenes']]+['END'])
            # Remove specialist routes, representing unavailable tools/failed access.
            for s in pack['scenes']:
                s['routes']=[x for x in s['routes'] if not x['items'] and not x['skills']]
            self.assertEqual(len(design.walk(pack,True)),4)

    def test_wrong_edition_and_setting(self):
        p,s=inputs();p['profile']['edition']='2014'
        self.assertEqual(design.audit(p,s)['status'],'invalid')
        p,s=inputs();p['profile']['setting_id']='monastery'
        self.assertIn('profile conflict',design.audit(p,s)['errors'])

    def test_budget_overrun_and_base_override(self):
        p,s=inputs();s['characters'][0]['allocations'][0]['interest']+=1
        self.assertEqual(design.audit(p,s)['status'],'invalid')
        p,s=inputs();p['skills'][0]['base']=99
        self.assertTrue(any('base conflict' in x for x in design.audit(p,s)['errors']))

    def test_missing_history_and_unread_rule_source(self):
        p,s=inputs();p['sources']['history']['status']='unread'
        self.assertEqual(design.audit(p,s)['status'],'draft')
        p,s=inputs();p['sources'].pop('history')
        self.assertEqual(design.audit(p,s)['status'],'draft')
        p,s=inputs();p['sources'].pop('core')
        self.assertEqual(design.audit(p,s)['status'],'draft')

    def test_invalid_item_access_and_quantity(self):
        p,s=inputs();p['items'][0]['availability']='unverified modern radio'
        self.assertEqual(design.audit(p,s)['status'],'invalid')
        p,s=inputs();p['items'][0]['quantity']=True
        self.assertEqual(design.audit(p,s)['status'],'invalid')
        p,s=inputs();p['items'][0]['price_basis']=''
        self.assertEqual(design.audit(p,s)['status'],'invalid')

    def test_broken_destination_and_required_unique_item(self):
        p,s=inputs();p['scenes'][0]['routes'][0]['success']='absent'
        self.assertTrue(any('destination' in x for x in design.audit(p,s)['errors']))
        p,s=inputs();p['scenes'][0]['routes'][-1]['items']=['ledger-copy']
        self.assertTrue(any('no ordinary' in x for x in design.audit(p,s)['errors']))

    def test_cycle_without_exit_and_unknown_skill(self):
        p,s=inputs();last=p['scenes'][-1];last['exit']=False
        for route in last['routes']:route['success']=route['failure']=last['id']
        self.assertEqual(design.audit(p,s)['status'],'invalid')
        p,s=inputs();p['scenes'][0]['routes'][0]['skills']=['Invented Plot Solution']
        self.assertEqual(design.audit(p,s)['status'],'invalid')

    def test_public_projection_excludes_internal_fields(self):
        p,s=inputs();p['items'][0]['gm_note']='SECRET_NESTED';p['skills'][0]['hidden_answer']='SECRET_NESTED'
        out=design.player_view(p,design.audit(p,s));text=json.dumps(out)
        self.assertNotIn('SECRET',text);self.assertNotIn('scenes',out);self.assertNotIn('sources',out)
        self.assertEqual(out,json.loads((BASE/'background-design/harbor/player.json').read_text(encoding='utf-8')))
        p['profile']['edition']='bad'
        self.assertEqual(design.player_view(p,design.audit(p,s)),{'status':'invalid'})

    def test_duplicate_and_unused_records(self):
        p,s=inputs();p['items'].append(deepcopy(p['items'][0]))
        self.assertEqual(design.audit(p,s)['status'],'invalid')
        p,s=inputs();item=deepcopy(p['items'][0]);item['id']='unused';p['items'].append(item)
        self.assertTrue(any('unused item' in x for x in design.audit(p,s)['errors']))

if __name__=='__main__':unittest.main()
