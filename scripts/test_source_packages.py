import unittest
import json
import subprocess
import sys
import session
from pathlib import Path
from tempfile import TemporaryDirectory
from srd_catalog import parse_spells, select, load
from class_magic import multiclass_slots, fixed_hp, settle_slot_cast
from coc_vehicle_magic import vehicle_damage, collision, magic_payment, casting_outcome


class SourcePackages(unittest.TestCase):
    def test_ritual_costs_survive_cold_recovery(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'ritual.sqlite'
            profile={'system':'CoC','edition':'7e','options':{}}
            state={'profile':profile,'actors':{'caster':{'name':'Test caster','audience':[],
                   'resources':{'mp':{'value':13,'max':13},'hp':{'value':13,'max':13}},'conditions':[]}},
                   'facts':[],'private':{},'pending':[],'clock':0}
            session.init(path,state)
            for n,changes in enumerate([
                [{'kind':'resource','actor':'caster','resource':'mp','delta':-4}],
                [{'kind':'resource','actor':'caster','resource':'mp','delta':-4}],
                [{'kind':'resource','actor':'caster','resource':'mp','delta':-5},
                 {'kind':'resource','actor':'caster','resource':'hp','delta':-11},
                 {'kind':'conditions','actor':'caster','value':['major wound']},
                 {'kind':'pending','value':['Resolve separately rolled SAN and manifestation']}]]):
                event={'id':str(n),'revision':n,'profile':profile,'input':'Deterministic ritual fixture',
                       'resolution':'Attempt, push, then additional backlash; MP4 fixture cost',
                       'sources':['CoC7 local PDF156; fixture dice, not a player roll'], 'changes':changes}
                session.apply(path,event)
            cold=json.loads(subprocess.check_output([sys.executable,'-X','utf8',str(Path(session.__file__)),str(path),'view','--gm'],encoding='utf-8'))
            self.assertEqual(cold['state']['actors']['caster']['resources']['hp']['value'],2)
            self.assertTrue(session.apply(path,event)['duplicate'])
            self.assertEqual(cold['revision'],3)
            self.assertTrue(cold['state']['pending'])

    def test_counterspell_refund_is_not_free_action(self):
        self.assertEqual(settle_slot_cast('r1.pc', [], True),
                         {'spent_turns': [], 'slot_delta': 0, 'casting_action_consumed': True})
        with self.assertRaises(ValueError):
            settle_slot_cast('r1.pc', ['r1.pc'], True)

    def test_spell_across_page_and_case(self):
        spells = parse_spells([(107, 'Acid  SplASh\nEvocation Cantrip (Wizard)\nCasting Time: Action\nDuration: Instantaneous\nOpening'),
                               (108, 'System Reference Document 5.2.1\n108\ncontinuation\nAid\nLevel 2 Abjuration (Cleric)\nCasting Time: Action\nDuration: 8 hours\nEnd')])
        self.assertEqual(len(spells), 2)
        self.assertEqual(select(spells, 'acid splash')['pdf_pages'], [107, 108])
        self.assertTrue(select(spells, 'ACID SPLASH')['text'].endswith('continuation'))
        with self.assertRaises(ValueError):
            select(spells, 'unknown expansion spell')

    def test_wrong_book_rejected(self):
        with TemporaryDirectory() as folder:
            p = Path(folder)/'wrong.pdf'; p.write_bytes(b'2014 is not 2024')
            with self.assertRaisesRegex(ValueError, 'Unverified PDF'):
                load(p)

    def test_multiclass_source_example(self):
        self.assertEqual(multiclass_slots({'Ranger': 4, 'Sorcerer': 3})['slots'], [4,3,2,0,0,0,0,0,0])
        self.assertEqual(multiclass_slots({'Paladin': 3, 'Ranger': 3})['caster_level'], 4)
        self.assertEqual(multiclass_slots({'Wizard': 3, 'Cleric': 2, 'Warlock': 2})['caster_level'], 5)
        with self.assertRaises(ValueError):
            multiclass_slots({'Paladin': 5, 'Fighter': 2})
        with self.assertRaises(ValueError):
            multiclass_slots({'Wizard': 20, 'Cleric': 1})

    def test_starting_class_and_retroactive_con(self):
        self.assertEqual(fixed_hp(['Fighter', 'Wizard', 'Wizard'], 2)['maximum'], 24)
        self.assertEqual(fixed_hp(['Wizard', 'Fighter', 'Wizard'], 2)['maximum'], 22)
        self.assertEqual(fixed_hp(['Fighter']*5, 2)['maximum'], 44)
        self.assertEqual(fixed_hp(['Fighter']*5, 3)['maximum'], 49)

    def test_collision_units_and_single_wreck(self):
        self.assertEqual(vehicle_damage(5,5,9,'ordinary_damage')['remaining_build'], 5)
        self.assertEqual(vehicle_damage(5,5,10,'ordinary_damage')['remaining_build'], 4)
        self.assertEqual(vehicle_damage(5,5,3,'build')['drive_penalty'], 1)
        self.assertFalse(vehicle_damage(5,1,1,'build')['catastrophic_single_collision'])
        self.assertTrue(vehicle_damage(5,5,5,'build')['catastrophic_single_collision'])

    def test_occupants_are_separate(self):
        r=collision('moderate',3,[1,6],2)
        self.assertEqual(r['occupant_hp_damage'], [1,6])
        self.assertEqual(r['vehicle_build_damage'],3)
        self.assertFalse(r['occupant_armor_applies'])
        with self.assertRaises(ValueError):
            collision('minor',3,[1],1)

    def test_failed_push_still_casts_and_pays(self):
        self.assertFalse(casting_outcome(True,False,False)['works'])
        self.assertTrue(casting_outcome(True,True,False)['works'])
        self.assertIsNotNone(casting_outcome(True,True,False)['backlash'])
        self.assertTrue(casting_outcome(False,False,True,True)['pay_costs'])
        self.assertFalse(casting_outcome(False,False,True,True)['works'])

    def test_magic_backlash_spills_to_hp(self):
        self.assertEqual(magic_payment(5,13,16), {'mp':0,'hp':2,'hp_damage':11,'injury_check_required':True})
        with self.assertRaises(ValueError):
            magic_payment(True,13,4)
