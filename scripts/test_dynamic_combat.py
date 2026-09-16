import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
import combat
import session
import test_combat


class DynamicCombatTests(unittest.TestCase):
    setUp=test_combat.CombatAndReservationTests.setUp
    revision=test_combat.CombatAndReservationTests.revision
    event=test_combat.CombatAndReservationTests.event
    send=test_combat.CombatAndReservationTests.send
    declaration=test_combat.CombatAndReservationTests.declaration
    combat_event=test_combat.CombatAndReservationTests.combat_event
    advance=test_combat.CombatAndReservationTests.advance
    start=test_combat.CombatAndReservationTests.start
    stored=test_combat.CombatAndReservationTests.stored
    timed=test_combat.CombatAndReservationTests.timed
    add_effect=test_combat.CombatAndReservationTests.add_effect

    def prepare(self):
        # Existing campaign actors, not implicit character creation by join.
        self.path=self.root/'dynamic.sqlite'
        initial=copy.deepcopy(self.state)
        initial['actors']['pc3']=copy.deepcopy(initial['actors']['pc2'])
        initial['actors']['pc3']['name']='Secret reinforcement'
        initial['actors']['pc3']['audience']=[]
        session.init(self.path,initial)
        self.start()

    def join(self,actor='pc3',participation='this-round',position=0):
        self.advance('join',{'actor':actor,'position':position,'participation':participation,'refresh':[],'reason':'reinforcements'})

    def next(self):self.advance('end_turn');self.advance('next_turn')

    def test_join_preserves_current_turn_and_this_round_eligibility(self):
        self.prepare();self.join()
        self.assertEqual((combat.current_actor(self.stored()),self.stored()['turn']),('pc1',1))
        self.assertEqual(self.stored()['counts']['pc3'],{'start':0,'end':0})
        self.next()
        self.assertEqual(combat.current_actor(self.stored()),'pc3')
        self.assertEqual(self.stored()['round'],1)
        self.next();self.assertEqual(combat.current_actor(self.stored()),'pc2')
        self.next();self.assertEqual(self.stored()['round'],2)

    def test_next_round_join_is_skipped_until_round_rollover(self):
        self.prepare();self.join(participation='next-round')
        self.next();self.assertEqual(combat.current_actor(self.stored()),'pc2')
        self.next();self.assertEqual((combat.current_actor(self.stored()),self.stored()['round']),('pc3',2))

    def test_reorder_never_repeats_already_started_actor(self):
        self.prepare();self.join(position=2)
        self.next()
        self.advance('reorder',{'order':['pc2','pc1','pc3'],'reason':'new initiative ruling'})
        self.assertEqual(combat.current_actor(self.stored()),'pc2')
        self.next();self.assertEqual(combat.current_actor(self.stored()),'pc3')
        self.next();self.assertEqual((combat.current_actor(self.stored()),self.stored()['round']),('pc2',2))
        self.assertEqual(self.stored()['counts']['pc1']['start'],1)

    def test_leave_current_requires_end_and_preserves_departed_counters(self):
        self.prepare()
        with self.assertRaises(ValueError):self.advance('leave',{'actor':'pc1','reason':'retreat'})
        self.advance('end_turn');self.advance('leave',{'actor':'pc1','reason':'retreat'})
        self.assertEqual(self.stored()['index'],-1)
        self.assertEqual(self.stored()['counts']['pc1'],{'start':1,'end':1})
        self.advance('next_turn');self.assertEqual(combat.current_actor(self.stored()),'pc2')
        self.assertEqual(self.stored()['round'],1)

    def test_returning_actor_keeps_counts_and_no_extra_turn(self):
        self.prepare();self.advance('end_turn');self.advance('leave',{'actor':'pc1','reason':'retreat'})
        self.advance('next_turn');self.join(actor='pc1')
        self.assertEqual(self.stored()['counts']['pc1']['start'],1)
        self.next()
        self.assertEqual((combat.current_actor(self.stored()),self.stored()['round']),('pc1',2))
        self.assertEqual(self.stored()['counts']['pc1']['start'],2)

    def test_leave_blocks_pending_actor_cost_or_decision(self):
        self.prepare();data=self.declaration();data['actor']='pc2';data['roll']=None
        self.send('declare',data)
        with self.assertRaises(ValueError):self.advance('leave',{'actor':'pc2','reason':'retreat'})
        self.send('cancel',{'reason':'withdraw action'})
        self.advance('leave',{'actor':'pc2','reason':'retreat'})
        self.assertEqual(self.stored()['order'],['pc1'])

    def test_dependent_expiry_requires_explicit_retime_before_leave(self):
        self.prepare();self.advance('add_effect',self.add_effect(actor='pc2',at='end',occurrence=1))
        with self.assertRaises(ValueError):self.advance('leave',{'actor':'pc2','reason':'retreat'})
        self.advance('retime_effect',{'id':'shield','expires':{'actor':'pc1','at':'end','occurrence':1},'reason':'explicit revised expiry'})
        self.advance('leave',{'actor':'pc2','reason':'retreat'})
        self.advance('end_turn')
        self.assertEqual(self.stored()['effects']['shield']['status'],'expired')

    def test_targeted_effect_must_be_removed_before_target_leaves(self):
        self.prepare();effect=self.add_effect();effect['targets']=['pc2']
        self.advance('add_effect',effect)
        with self.assertRaises(ValueError):self.advance('leave',{'actor':'pc2','reason':'retreat'})
        self.advance('remove_effect',{'id':'shield','reason':'effect ends on retreat'})
        self.advance('leave',{'actor':'pc2','reason':'retreat'})
        self.assertIn('pc2',self.stored()['counts'])
        self.assertEqual(self.stored()['effects']['shield']['targets'],['pc2'])

    def test_invalid_retime_rolls_back(self):
        self.prepare();self.advance('add_effect',self.add_effect());before=self.stored()
        with self.assertRaises(ValueError):self.advance('retime_effect',{'id':'shield','expires':{'actor':'pc1','at':'start','occurrence':1},'reason':'bad'})
        self.assertEqual(self.stored(),before)

    def test_join_invalid_refresh_rolls_back_membership(self):
        self.prepare();before=self.stored()
        with self.assertRaises(ValueError):self.advance('join',{'actor':'pc3','position':0,'participation':'this-round',
            'refresh':[{'actor':'pc3','resource':'mp','at':'start','value':999}],'reason':'bad'})
        self.assertEqual(self.stored(),before)

    def test_duplicate_join_retry_does_not_duplicate_actor(self):
        self.prepare();event=self.combat_event('join',{'actor':'pc3','position':1,'participation':'this-round','refresh':[],'reason':'join'})
        session.apply(self.path,event);self.assertTrue(session.apply(self.path,event)['duplicate'])
        self.assertEqual(self.stored()['order'].count('pc3'),1)

    def test_invalid_order_duplicate_join_and_last_leave_rejected(self):
        self.prepare()
        with self.assertRaises(ValueError):self.advance('reorder',{'order':['pc1','pc1'],'reason':'bad'})
        with self.assertRaises(ValueError):self.join(actor='pc1')
        self.advance('leave',{'actor':'pc2','reason':'retreat'})
        self.advance('end_turn')
        with self.assertRaises(ValueError):self.advance('leave',{'actor':'pc1','reason':'retreat'})

    def test_hidden_join_and_cold_read_do_not_publish_private_participant(self):
        self.prepare();self.join()
        self.assertNotIn('pc3',json.dumps(session.view(self.path,player='pc1')['combat']))
        output=self.root/'cold.json'
        run=subprocess.run([sys.executable,'-X','utf8',str(Path(combat.__file__)),str(self.path),'view',
                            '--private-output',str(output)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(json.loads(output.read_text(encoding='utf-8'))['combat'],self.stored())

    def test_schema_one_reads_unchanged_then_migrates_on_mutation(self):
        self.prepare();self.next()
        old=session.view(self.path,gm=True)['state'];store=old['private']['combat']
        store['schema']=1;store.pop('current');store.pop('round_used')
        self.path=self.root/'legacy.sqlite';session.init(self.path,old)
        self.assertEqual(self.stored()['schema'],1)
        self.advance('reorder',{'order':['pc2','pc1'],'reason':'upgrade and reorder'})
        self.assertEqual(self.stored()['schema'],2)
        self.assertEqual(set(self.stored()['round_used']),{'pc1','pc2'})
        self.next();self.assertEqual(self.stored()['round'],2)

    def test_restore_recovers_original_membership_and_eligibility(self):
        self.prepare();revision=self.revision();self.join();self.next()
        event=self.event('unused',{});event['changes']=[{'kind':'restore','revision':revision}]
        session.apply(self.path,event)
        self.assertEqual(self.stored()['order'],['pc1','pc2'])
        self.assertEqual(self.stored()['round_used'],['pc1'])
        self.assertEqual(combat.current_actor(self.stored()),'pc1')


if __name__=='__main__':unittest.main()
