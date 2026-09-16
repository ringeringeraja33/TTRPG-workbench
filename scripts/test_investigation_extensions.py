import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
import investigation_runtime as runtime
import session
import test_investigation_runtime as fixtures


class InvestigationExtensionTests(unittest.TestCase):
    setUp=fixtures.InvestigationRuntimeTests.setUp
    revision=fixtures.InvestigationRuntimeTests.revision
    event=fixtures.InvestigationRuntimeTests.event
    send=fixtures.InvestigationRuntimeTests.send
    declaration=fixtures.InvestigationRuntimeTests.declaration
    plan=fixtures.InvestigationRuntimeTests.plan
    apply=fixtures.InvestigationRuntimeTests.apply
    setup=fixtures.InvestigationRuntimeTests.setup
    stored=fixtures.InvestigationRuntimeTests.stored
    discover=fixtures.InvestigationRuntimeTests.discover

    def extension(self):
        return {'evidence':[{'id':'witness','text':'New witness account','available':True,'audience':['all']}],
                'conclusions':[{'id':'location','text':'GM_SECRET location','audience':[],'essential':False,'routes':[['witness']]}],
                'routes':[{'conclusion':'secret','route':['location']}],'reason':'Players interviewed a new witness'}
    def saved(self):return session.view(self.path,gm=True)
    def test_extend_does_not_publish_or_rewrite_knowledge(self):
        self.setup();self.discover();before=copy.deepcopy(self.stored()['knowledge'])
        self.apply('extend',self.extension())
        self.assertEqual(self.stored()['knowledge'],before)
        own=session.view(self.path,player='pc1')['investigation']
        self.assertEqual(own['evidence'],[{'id':'letter','text':'Letter observation'}])
        self.assertNotIn('GM_SECRET',json.dumps(own))
    def test_new_route_changes_analysis_only_after_discovery(self):
        self.setup();self.apply('extend',self.extension())
        state=self.saved()['state'];audit=runtime.analysis(self.stored(),state)
        self.assertIn('secret',audit['preparation']['derivable_conclusions'])
        self.assertNotIn('secret',audit['actual_knowledge']['pc1']['derivable_conclusions'])
        self.discover('witness');audit=runtime.analysis(self.stored(),self.saved()['state'])
        self.assertIn('secret',audit['actual_knowledge']['pc1']['derivable_conclusions'])
        self.assertEqual(self.saved()['state']['facts'],[])
    def test_bad_extension_rolls_back_all_records(self):
        self.setup();before=self.saved();data=self.extension();data['routes'][0]['route']=['missing']
        with self.assertRaises(ValueError):self.apply('extend',data)
        self.assertEqual(self.saved(),before)
    def test_duplicate_ids_rejected(self):
        self.setup();before=self.saved()
        for existing in ('letter','secret'):
            data=self.extension();data['evidence'][0]['id']=existing
            with self.assertRaises(ValueError):self.apply('extend',data)
            self.assertEqual(self.saved(),before)
    def test_duplicate_routes_rejected(self):
        self.setup()
        with self.assertRaises(ValueError):self.apply('extend',{'evidence':[],'conclusions':[],
            'routes':[{'conclusion':'secret','route':['key','letter']}],'reason':'duplicate reordered AND group'})
    def test_invalid_lists_and_empty_extensions(self):
        self.setup();before=self.saved()
        for data in ({'evidence':[],'conclusions':[],'routes':[],'reason':'empty'},
                     {**self.extension(),'routes':{}}, {**self.extension(),'reason':''}):
            with self.assertRaises(ValueError):self.apply('extend',data)
        self.assertEqual(self.saved(),before)
    def test_record_bound_applies_to_total_plan(self):
        self.setup();data={'evidence':[{'id':f'new-{i}','text':'text','audience':[],'available':False} for i in range(1998)],
                          'conclusions':[],'routes':[],'reason':'too many'}
        with self.assertRaises(ValueError):self.apply('extend',data)
        self.assertEqual(len(self.stored()['plan']['evidence']),2)
    def test_exact_retry_and_stale_extension(self):
        self.setup();event=self.event('',{},changes=[{'kind':'investigation','step':'extend','data':self.extension()}])
        session.apply(self.path,event);self.assertTrue(session.apply(self.path,event)['duplicate'])
        self.assertEqual(len(self.stored()['plan']['evidence']),3)
        event['id']='different'
        with self.assertRaises(ValueError):session.apply(self.path,event)
    def test_edit_unseen_then_discover(self):
        self.setup();self.apply('edit_unseen',{'evidence':'letter','text':'Corrected unseen observation','reason':'Preparation typo'})
        self.discover();self.assertEqual(self.stored()['knowledge']['pc1']['letter']['text'],'Corrected unseen observation')
    def test_any_recipient_prevents_rewrite_even_after_loss(self):
        self.setup();self.discover(who=['pc2']);self.apply('available',{'evidence':'letter','available':False,'reason':'Destroyed'})
        before=self.saved()
        with self.assertRaises(ValueError):self.apply('edit_unseen',{'evidence':'letter','text':'Changed truth','reason':'Rewrite'})
        self.assertEqual(self.saved(),before)
        self.apply('share',{'evidence':'letter','sender':'pc2','recipients':['pc1'],'method':'Recall'})
        self.assertEqual(self.stored()['knowledge']['pc1']['letter']['text'],'Letter observation')
    def test_new_observation_keeps_old_hypothesis(self):
        self.setup();self.discover();self.apply('hypothesize',{'id':'h','actor':'pc1','text':'Original theory','evidence':['letter']})
        before=copy.deepcopy(self.stored()['hypotheses']);self.apply('extend',self.extension());self.discover('witness')
        self.assertEqual(self.stored()['hypotheses'],before)
    def test_extension_cannot_be_inline_effect(self):
        self.setup();data=self.declaration();data['roll']=None;self.send('declare',data);before=self.saved()
        with self.assertRaises(ValueError):self.send('settle',{'outcome':'success','effects':[
            {'kind':'investigation_effect','step':'extend','data':self.extension()}]})
        self.assertEqual(self.saved(),before)
    def test_new_evidence_action_acquisition(self):
        self.setup();self.apply('extend',self.extension());data=self.declaration();data['roll']=None;self.send('declare',data)
        self.send('settle',{'outcome':'success','effects':[{'kind':'investigation_effect','step':'discover','data':{
            'evidence':'witness','recipients':['pc1'],'method':'Interview completed'}}]})
        self.assertIn('witness',self.stored()['knowledge']['pc1'])
        self.assertEqual(self.saved()['state']['actors']['pc1']['resources']['mp']['value'],11)
    def test_cold_recovery_and_restore(self):
        self.setup();self.discover();before=self.stored();rev=self.revision();self.apply('extend',self.extension());self.discover('witness')
        out=self.root/'gm-expanded.json'
        run=subprocess.run([sys.executable,'-X','utf8',str(Path(runtime.__file__)),str(self.path),'view','--private-output',str(out)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr);self.assertNotIn('GM_SECRET',run.stdout)
        self.assertEqual(json.loads(out.read_text(encoding='utf-8'))['investigation'],self.stored())
        session.apply(self.path,self.event('',{},changes=[{'kind':'restore','revision':rev}]))
        self.assertEqual(self.stored(),before)


if __name__=='__main__':unittest.main()
