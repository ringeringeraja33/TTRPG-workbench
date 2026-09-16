import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
import investigation_runtime as runtime
import session
import session_review
import test_actions


class InvestigationRuntimeTests(unittest.TestCase):
    setUp=test_actions.ActionTests.setUp
    revision=test_actions.ActionTests.revision
    event=test_actions.ActionTests.event
    send=test_actions.ActionTests.send
    declaration=test_actions.ActionTests.declaration
    action=test_actions.ActionTests.action

    def plan(self):
        return {'schema':1,'evidence':[{'id':'letter','text':'Letter observation','available':True,'audience':['all']},
            {'id':'key','text':'Key observation','available':False,'audience':['pc1']}],
            'conclusions':[{'id':'secret','text':'GM_SECRET culprit','audience':[],'essential':True,'routes':[['letter','key']]}]}

    def apply(self,step,data):
        event=self.event('unused',{});event['changes']=[{'kind':'investigation','step':step,'data':data}]
        return session.apply(self.path,event)

    def setup(self):self.apply('setup',{'plan':self.plan()})
    def stored(self):return session.view(self.path,gm=True)['state']['private']['investigation']
    def discover(self,eid='letter',who=None):self.apply('discover',{'evidence':eid,'recipients':who or ['pc1'],'method':'explicit inspection'})

    def test_setup_does_not_discover_or_publish_available_clues(self):
        self.setup()
        self.assertEqual(session.view(self.path,player='pc1')['investigation']['evidence'],[])
        self.assertEqual(session.view(self.path)['investigation']['evidence'],[])
        self.assertNotIn('GM_SECRET',json.dumps(session.view(self.path,player='pc1')))

    def test_split_party_share_requires_sender_knowledge(self):
        self.setup();self.discover()
        self.assertEqual(session.view(self.path,player='pc2')['investigation']['evidence'],[])
        with self.assertRaises(ValueError):self.apply('share',{'evidence':'letter','sender':'pc2','recipients':['pc1'],'method':'unknown'})
        self.apply('share',{'evidence':'letter','sender':'pc1','recipients':['pc2'],'method':'read the letter together'})
        self.assertEqual(session.view(self.path,player='pc2')['investigation']['evidence'][0]['text'],'Letter observation')

    def test_unavailable_clue_rejected_but_learned_observation_survives_loss(self):
        self.setup()
        with self.assertRaises(ValueError):self.discover('key')
        self.discover();self.apply('available',{'evidence':'letter','available':False,'reason':'destroyed'})
        self.apply('share',{'evidence':'letter','sender':'pc1','recipients':['pc2'],'method':'remembered observation'})
        self.assertEqual(len(session.view(self.path,player='pc2')['investigation']['evidence']),1)

    def test_knowledge_analysis_does_not_auto_publish_deduction(self):
        self.setup();self.discover();self.apply('available',{'evidence':'key','available':True,'reason':'found location'});self.discover('key')
        state=session.view(self.path,gm=True)['state'];analysis=runtime.analysis(self.stored(),state)
        self.assertIn('secret',analysis['actual_knowledge']['pc1']['derivable_conclusions'])
        self.assertEqual(analysis['actual_knowledge']['pc2']['derivable_conclusions'],[])
        self.assertNotIn('GM_SECRET',json.dumps(session.view(self.path,player='pc1')))
        self.assertEqual(state['facts'],[])

    def test_hypothesis_support_must_be_known(self):
        self.setup()
        with self.assertRaises(ValueError):self.apply('hypothesize',{'id':'h','actor':'pc1','text':'Theory','evidence':['letter']})
        self.discover();self.apply('hypothesize',{'id':'h','actor':'pc1','text':'Theory','evidence':['letter']})
        self.assertEqual(self.stored()['hypotheses']['h']['status'],'open')
        self.assertEqual(session.view(self.path,player='pc2')['investigation']['hypotheses'],[])

    def test_resolution_is_explicit_and_does_not_change_world_facts(self):
        self.setup();self.apply('hypothesize',{'id':'h','actor':'pc1','text':'Speculation without evidence','evidence':[]})
        self.apply('resolve',{'id':'h','status':'refuted','public_resolution':'The witness contradicts it','gm_reason':'GM_SECRET reason'})
        own=session.view(self.path,player='pc1')['investigation']
        self.assertEqual(own['hypotheses'][0]['status'],'refuted')
        self.assertNotIn('GM_SECRET',json.dumps(own));self.assertEqual(session.view(self.path,gm=True)['state']['facts'],[])

    def test_discovery_costs_and_receipt_commit_together(self):
        self.setup();data=self.declaration();data['roll']=None;self.send('declare',data)
        event=self.event('settle',{'outcome':'success','effects':[{'kind':'investigation_effect','step':'discover','data':
            {'evidence':'letter','recipients':['pc1'],'method':'successful original test procedure'}}]})
        session.apply(self.path,event);self.assertTrue(session.apply(self.path,event)['duplicate'])
        self.assertEqual(len(self.stored()['knowledge']['pc1']['letter']['events']),1)
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['value'],11)

    def test_invalid_discovery_rolls_back_cost_and_action_completion(self):
        self.setup();data=self.declaration();data['roll']=None;self.send('declare',data)
        with self.assertRaises(ValueError):self.send('settle',{'outcome':'success','effects':[{'kind':'investigation_effect','step':'discover',
            'data':{'evidence':'key','recipients':['pc1'],'method':'unavailable'}}]})
        self.assertEqual(self.action()['status'],'declared')
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['value'],12)

    def test_bad_types_unknown_fields_and_public_recipient_rejected(self):
        plan=self.plan();plan['evidence'][0]['gm_secret']='hidden'
        with self.assertRaises(ValueError):self.apply('setup',{'plan':plan})
        self.setup()
        for recipients in ('pc1',['all'],['absent'],['pc1','pc1']):
            with self.assertRaises(ValueError):self.apply('discover',{'evidence':'letter','recipients':recipients,'method':'test'})
        with self.assertRaises(ValueError):self.apply('available',{'evidence':'key','available':'false','reason':'bad'})

    def test_default_cli_private_export_and_cold_recovery(self):
        self.setup();self.discover();out=self.root/'private.json'
        run=subprocess.run([sys.executable,'-X','utf8',str(Path(runtime.__file__)),str(self.path),'view',
                            '--private-output',str(out)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr);self.assertNotIn('GM_SECRET',run.stdout)
        self.assertEqual(json.loads(out.read_text(encoding='utf-8'))['investigation'],self.stored())

    def test_recap_includes_actual_knowledge_without_spoilers(self):
        self.setup();self.discover()
        self.assertIn('investigation',session_review.recap(self.path,gm=True)['next_prep'])
        player=session_review.recap(self.path,player='pc1')
        self.assertEqual(len(player['investigation']['evidence']),1)
        self.assertNotIn('GM_SECRET',json.dumps(player))

    def test_restore_undoes_delivery_and_preserves_other_pending(self):
        self.setup();revision=self.revision();self.discover()
        event=self.event('unused',{});event['changes']=[{'kind':'restore','revision':revision}];session.apply(self.path,event)
        self.assertEqual(self.stored()['knowledge'],{})
        self.assertEqual(session.view(self.path,gm=True)['state']['pending'],self.state['pending'])

    def test_private_overwrite_and_inline_setup_are_rejected(self):
        self.setup();event=self.event('unused',{});event['changes']=[{'kind':'private','value':{}}]
        with self.assertRaises(ValueError):session.apply(self.path,event)
        event['changes']=[{'kind':'investigation_effect','step':'setup','data':{'plan':self.plan()}}]
        with self.assertRaises(ValueError):session.apply(self.path,event)


if __name__=='__main__':unittest.main()
