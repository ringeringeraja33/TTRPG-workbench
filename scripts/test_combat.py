import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import unittest
import actions
import combat
import session
import session_review
import test_actions


class CombatAndReservationTests(unittest.TestCase):
    setUp=test_actions.ActionTests.setUp
    revision=test_actions.ActionTests.revision
    event=test_actions.ActionTests.event
    send=test_actions.ActionTests.send
    declaration=test_actions.ActionTests.declaration
    action=test_actions.ActionTests.action
    settlement=test_actions.ActionTests.settlement

    def combat_event(self,step,data):
        event=self.event('unused',{})
        event['changes']=[{'kind':'combat','step':step,'data':data}]
        return event

    def advance(self,step,data=None):
        return session.apply(self.path,self.combat_event(step,data or {}))

    def start(self,refresh=None,identity='fight'):
        return self.advance('start',{'id':identity,'audience':['all'],'order':['pc1','pc2'],'refresh':refresh or []})

    def stored(self):return session.view(self.path,gm=True)['state']['private']['combat']

    def add_effect(self,eid='shield',actor='pc1',at='start',occurrence=2):
        return {'id':eid,'label':'护盾','targets':['pc1'],'audience':['pc1'],
                'expires':{'actor':actor,'at':at,'occurrence':occurrence}}

    def timed(self):
        data=self.declaration();data['roll']=None
        data['timing']={'encounter':'fight','turn':1}
        return data

    def test_reservations_block_second_action_until_cancelled(self):
        data=self.declaration();data['costs'][0]['delta']=-12
        self.send('declare',data)
        with self.assertRaises(ValueError):self.send('declare',data,'b')
        own=actions.view(self.path,player='pc1')['resource_availability']
        mp=next(x for x in own if x['resource']=='mp')
        self.assertEqual((mp['current'],mp['reserved'],mp['available']),(12,12,0))
        self.send('cancel',{'reason':'withdraw'})
        self.send('declare',data,'b')
        self.assertTrue(self.action('b')['reserved'])

    def test_reserve_release_retries_do_not_double_hold(self):
        self.send('declare',self.declaration())
        event=self.event('release',{'reason':'changed plan'})
        session.apply(self.path,event);session.apply(self.path,event)
        self.assertEqual(actions.reservations(session.view(self.path,gm=True)['state']),{})
        self.send('reserve',{'reason':'resume plan'})
        self.assertEqual(actions.reservations(session.view(self.path,gm=True)['state']),{('pc1','mp'):1})

    def test_concurrent_declarations_cannot_overbook_resource(self):
        data=self.declaration();data['costs'][0]['delta']=-12
        first=self.event('declare',data,'a',id='a')
        second=self.event('declare',data,'b',id='b')
        def apply(event):
            try:return session.apply(self.path,event)
            except ValueError:return None
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(apply,[first,second]))
        self.assertEqual(sum(r is not None for r in results),1)
        self.assertEqual(self.revision(),1)

    def test_resize_cannot_destroy_reserved_capacity(self):
        data=self.declaration();data['costs'][0]['delta']=-12
        self.send('declare',data)
        event=self.event('unused',{});event['changes']=[{'kind':'resize','actor':'pc1','resource':'mp','maximum':3}]
        with self.assertRaises(ValueError):session.apply(self.path,event)
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['max'],12)

    def test_legacy_actions_do_not_acquire_silent_reservations(self):
        self.send('declare',self.declaration())
        old=session.view(self.path,gm=True)['state'];old['private']['action_workflow']['actions']['a'].pop('reserved')
        self.path=self.root/'legacy.sqlite';session.init(self.path,old)
        self.assertEqual(actions.reservations(old),{})
        self.send('reserve',{'reason':'explicit migration for pending action'})
        self.assertTrue(self.action()['reserved'])

    def test_reservation_projection_hides_other_actor_and_internal_action(self):
        self.send('declare',self.declaration())
        self.assertEqual(actions.view(self.path)['resource_availability'],[])
        other=actions.view(self.path,player='pc2')
        self.assertTrue(all(x['actor']=='pc2' and x['reserved']==0 for x in other['resource_availability']))
        self.assertEqual(other['actions'],{})

    def test_turn_boundaries_increment_and_retries_are_idempotent(self):
        self.start();self.assertEqual(self.stored()['counts']['pc1'],{'start':1,'end':0})
        event=self.combat_event('end_turn',{})
        session.apply(self.path,event);session.apply(self.path,event)
        self.assertEqual(self.stored()['counts']['pc1']['end'],1)
        with self.assertRaises(ValueError):self.advance('end_turn')
        self.advance('next_turn');self.assertEqual(self.stored()['turn'],2)
        self.advance('end_turn');self.advance('next_turn')
        self.assertEqual((self.stored()['round'],self.stored()['index']),(2,0))

    def test_start_and_target_end_expiries_are_distinct(self):
        self.start()
        self.advance('add_effect',self.add_effect())
        self.advance('add_effect',self.add_effect('target-end','pc2','end',1))
        self.advance('end_turn');self.advance('next_turn')
        self.assertTrue(all(e['status']=='active' for e in self.stored()['effects'].values()))
        self.advance('end_turn')
        self.assertEqual(self.stored()['effects']['target-end']['status'],'expired')
        self.assertEqual(self.stored()['effects']['shield']['status'],'active')
        self.advance('next_turn')
        self.assertEqual(self.stored()['effects']['shield']['status'],'expired')

    def test_timed_action_blocks_turn_end_and_finish_until_settled(self):
        self.start();self.send('declare',self.timed())
        with self.assertRaises(ValueError):self.advance('end_turn')
        with self.assertRaises(ValueError):self.advance('finish',{'reason':'done'})
        self.send('settle',{'outcome':'no-check','effects':[]})
        self.advance('end_turn');self.advance('next_turn')
        self.assertEqual(self.stored()['turn'],2)

    def test_stale_timing_or_nonparticipant_is_rejected(self):
        self.start();data=self.timed();data['timing']['turn']=2
        with self.assertRaises(ValueError):self.send('declare',data)
        self.advance('end_turn');data['timing']['turn']=1
        with self.assertRaises(ValueError):self.send('declare',data)

    def test_effect_and_cost_commit_atomically(self):
        self.start();self.send('declare',self.timed())
        effects=[{'kind':'combat_effect','step':'add_effect','data':self.add_effect()}]
        event=self.event('settle',{'outcome':'success','effects':effects})
        session.apply(self.path,event);session.apply(self.path,event)
        self.assertEqual(self.stored()['effects']['shield']['status'],'active')
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['value'],11)

    def test_invalid_effect_rolls_back_settlement_and_cost(self):
        self.start();self.send('declare',self.timed())
        effects=[{'kind':'combat_effect','step':'add_effect','data':self.add_effect(occurrence=1)}]
        with self.assertRaises(ValueError):self.send('settle',{'outcome':'success','effects':effects})
        self.assertEqual(self.action()['status'],'declared')
        self.assertEqual(self.stored()['effects'],{})
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['value'],12)

    def test_inline_effect_cannot_advance_turn(self):
        self.start();self.send('declare',self.timed())
        with self.assertRaises(ValueError):self.send('settle',{'outcome':'success','effects':[{'kind':'combat_effect','step':'end_turn','data':{}}]})
        self.assertEqual(self.stored()['phase'],'active')

    def test_configured_refresh_occurs_only_at_own_boundary(self):
        self.start([{'actor':'pc1','resource':'mp','at':'start','value':12}])
        self.send('declare',self.timed());self.send('settle',{'outcome':'success','effects':[]})
        self.advance('end_turn');self.advance('next_turn')
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['value'],11)
        self.advance('end_turn');self.advance('next_turn')
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['value'],12)

    def test_refresh_conflicting_with_reservation_rolls_back_boundary(self):
        self.start([{'actor':'pc1','resource':'mp','at':'end','value':0}])
        self.send('declare',self.declaration())
        with self.assertRaises(ValueError):self.advance('end_turn')
        self.assertEqual(self.stored()['counts']['pc1']['end'],0)
        self.assertEqual(self.stored()['phase'],'active')

    def test_hidden_combat_details_and_cold_read(self):
        self.start();self.advance('add_effect',self.add_effect())
        view=session.view(self.path,player='pc2')['combat']
        self.assertEqual(view['order'],['pc2']);self.assertIsNone(view['current_actor'])
        self.assertEqual(view['effects'],{})
        self.assertNotIn('turn',view);self.assertNotIn('counts',view)
        destination=self.root/'combat-private.json'
        run=subprocess.run([sys.executable,'-X','utf8',str(Path(combat.__file__)),str(self.path),'view',
                            '--private-output',str(destination)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(set(json.loads(run.stdout)),{'revision','private_result_saved'})
        self.assertEqual(json.loads(destination.read_text(encoding='utf-8'))['combat'],self.stored())

    def test_restore_rewinds_timing_and_effects(self):
        self.start();self.advance('add_effect',self.add_effect());revision=self.revision()
        self.advance('end_turn');self.advance('next_turn')
        event=self.event('unused',{});event['changes']=[{'kind':'restore','revision':revision}]
        session.apply(self.path,event)
        self.assertEqual(self.stored()['turn'],1)
        self.assertEqual(self.stored()['effects']['shield']['status'],'active')
        recap=session_review.recap(self.path,gm=True)['next_prep']['combat']
        self.assertEqual(recap['turn'],1)
        self.assertIn('shield',recap['active_effects'])

    def test_finish_cleans_encounter_effects_and_forbids_reused_id(self):
        self.start();self.advance('add_effect',self.add_effect())
        self.advance('finish',{'reason':'all participants withdraw'})
        self.assertEqual(self.stored()['effects']['shield']['status'],'expired')
        self.start(identity='fight2');self.advance('finish',{'reason':'done'})
        with self.assertRaises(ValueError):self.start(identity='fight')

    def test_private_overwrite_cannot_bypass_turns(self):
        self.start();event=self.event('unused',{});event['changes']=[{'kind':'private','value':{}}]
        with self.assertRaises(ValueError):session.apply(self.path,event)
        self.assertEqual(self.stored()['phase'],'active')

    def test_duplicate_refresh_and_invalid_order_fail_without_state(self):
        refresh={'actor':'pc1','resource':'mp','at':'start','value':12}
        with self.assertRaises(ValueError):self.start([refresh,refresh])
        with self.assertRaises(ValueError):self.advance('start',{'id':'bad','audience':['all'],'order':['pc1','pc1'],'refresh':[]})
        self.assertEqual(self.revision(),0)


if __name__=='__main__':unittest.main()
