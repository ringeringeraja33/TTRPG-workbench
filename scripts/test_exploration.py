import unittest, json, subprocess, sys, copy
from pathlib import Path
import test_actions
import session, session_review, exploration

class ExplorationTests(unittest.TestCase):
    setUp=test_actions.ActionTests.setUp
    revision=test_actions.ActionTests.revision
    event=test_actions.ActionTests.event
    send=test_actions.ActionTests.send
    declaration=test_actions.ActionTests.declaration

    def saved(self):return session.view(self.path,gm=True)['state']
    def exevent(self,step,data):return self.event(step,data,changes=[{'kind':'exploration','step':step,'data':data}])
    def ex(self,step,data):return session.apply(self.path,self.exevent(step,data))
    def setup(self):self.ex('setup',{'audience':['all']})
    def advance(self,minutes=5,cost=-1):
        return {'minutes':minutes,'participants':['pc1'],'summary':'搜索','audience':['all'],
                'costs':[{'kind':'resource','actor':'pc1','resource':'mp','delta':cost}]}
    def schedule(self,due=5,every=0,blocking=True,audience=None):
        self.ex('schedule',{'id':'lamp','label':'SECRET lamp','due':due,'every':every,'blocking':blocking,'audience':audience or ['pc1']})
    def reminder(self):return self.saved()['private']['exploration']['reminders']['lamp']
    def test_retry(self):
        self.setup(); e=self.exevent('advance',self.advance());session.apply(self.path,e)
        self.assertTrue(session.apply(self.path,e)['duplicate'])
        self.assertEqual(self.saved()['clock'],5)
        self.assertEqual(self.saved()['actors']['pc1']['resources']['mp']['value'],11)
    def test_insufficient_cost_rollback(self):
        self.setup();self.schedule();before=self.saved()
        with self.assertRaises(ValueError):self.ex('advance',self.advance(cost=-99))
        self.assertEqual(self.saved(),before)
    def test_deadline_boundary(self):
        self.setup();self.schedule();before=self.saved()
        with self.assertRaises(ValueError):self.ex('advance',self.advance(6))
        self.assertEqual(self.saved(),before);self.ex('advance',self.advance())
        self.assertEqual(self.reminder()['status'],'due')
        with self.assertRaises(ValueError):self.ex('advance',self.advance())
        self.ex('ack',{'id':'lamp','resolution':'replaced'});self.ex('advance',self.advance())
        self.assertEqual(self.saved()['clock'],10)
    def test_clock_cannot_bypass(self):
        self.setup();self.schedule()
        with self.assertRaises(ValueError):session.apply(self.path,self.event('',{},changes=[{'kind':'clock','minutes':6}]))
    def test_recurring_anchor(self):
        self.setup();self.schedule(every=5);self.ex('advance',self.advance())
        self.ex('ack',{'id':'lamp','resolution':'done'})
        self.assertEqual(self.reminder()['due'],10);self.assertEqual(self.reminder()['status'],'pending')
    def test_overdue_catchup(self):
        self.setup();self.schedule(every=5,blocking=False);self.ex('advance',self.advance(16))
        for expected in (10,15,20):
            self.ex('ack',{'id':'lamp','resolution':'explicit consequence'})
            self.assertEqual(self.reminder()['due'],expected)
        self.assertEqual(self.reminder()['status'],'pending')
    def test_cancel(self):
        self.setup();self.schedule();self.ex('cancel',{'id':'lamp','reason':'extinguished'})
        self.ex('advance',self.advance(10));self.assertEqual(self.reminder()['status'],'cancelled')
    def test_action_settlement_time(self):
        self.setup();self.send('declare',self.declaration())
        with self.assertRaises(ValueError):self.ex('advance',self.advance())
        self.send('roll',{});data=self.advance();data['costs']=[]
        self.send('settle',{'outcome':'no-check','effects':[{'kind':'exploration_effect','step':'advance','data':data}]})
        self.assertEqual(self.saved()['clock'],5)
        self.assertEqual(self.saved()['actors']['pc1']['resources']['mp']['value'],11)
    def test_ack_consequence_rollback(self):
        self.setup();self.schedule(due=0);self.send('declare',self.declaration());self.send('roll',{});before=self.saved()
        with self.assertRaises(ValueError):self.send('settle',{'outcome':'no-check','effects':[
            {'kind':'exploration_effect','step':'ack','data':{'id':'lamp','resolution':'done'}},
            {'kind':'resource','actor':'pc1','resource':'hp','delta':-99}]})
        self.assertEqual(self.saved(),before)
    def test_private_and_cold_recovery(self):
        self.setup();self.schedule();data=self.advance();data['summary']='SECRET search';data['audience']=[]
        self.ex('advance',data)
        self.assertNotIn('SECRET',json.dumps(session.view(self.path,player='pc2')))
        out=self.root/'gm.json'
        run=subprocess.run([sys.executable,str(Path(exploration.__file__)),str(self.path),'view','--private-output',str(out)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr);self.assertNotIn('SECRET',run.stdout)
        self.assertEqual(json.loads(out.read_text(encoding='utf-8'))['exploration'],self.saved()['private']['exploration'])
    def test_recap(self):
        self.setup();self.schedule(due=0)
        self.assertIn('lamp',session_review.recap(self.path,gm=True)['next_prep']['exploration']['due'])
    def test_restore(self):
        self.setup();self.schedule();before=self.saved();rev=self.revision()
        self.ex('advance',self.advance());self.ex('ack',{'id':'lamp','resolution':'done'})
        session.apply(self.path,self.event('',{},changes=[{'kind':'restore','revision':rev}]))
        self.assertEqual(self.saved(),before)
    def test_bad_activity_inputs(self):
        self.setup();before=self.saved()
        for field,value in [('minutes',True),('minutes',-1),('minutes',10081),('participants',['missing']),('participants',['pc1','pc1'])]:
            data=self.advance();data[field]=value
            with self.assertRaises(ValueError):self.ex('advance',data)
        self.assertEqual(self.saved(),before)
    def test_duplicate_schedule(self):
        self.setup();self.schedule()
        with self.assertRaises(ValueError):self.schedule()
    def test_legacy_clock(self):
        session.apply(self.path,self.event('',{},changes=[{'kind':'clock','minutes':5}]))
        self.assertEqual(self.saved()['clock'],5)
    def test_combat_blocks_time(self):
        self.setup()
        session.apply(self.path,self.event('',{},changes=[{'kind':'combat','step':'start','data':{
            'id':'fight','audience':['all'],'order':['pc1','pc2'],'refresh':[]}}]))
        before=self.saved()
        with self.assertRaises(ValueError):self.ex('advance',self.advance())
        self.assertEqual(self.saved(),before)
    def test_reserved_supplies_not_spendable(self):
        self.setup();data=self.declaration();data['costs'][0]['delta']=-12
        self.send('declare',data);before=self.saved()
        with self.assertRaisesRegex(ValueError,'(?i)(resource|cost|available|reserv)'):self.ex('advance',self.advance())
        self.assertEqual(self.saved(),before)
    def test_protected_store(self):
        self.setup()
        with self.assertRaises(ValueError):session.apply(self.path,self.event('',{},changes=[{'kind':'private','value':{}}]))
        with self.assertRaises(ValueError):session.apply(self.path,self.event('',{},changes=[{'kind':'exploration_effect','step':'schedule','data':{}}]))

    def test_saved_receipts_reject_corruption(self):
        self.setup();self.schedule();self.ex('advance',self.advance());self.ex('ack',{'id':'lamp','resolution':'done'})
        baseline=self.saved()
        mutations=[
            lambda x:x['activities'][0].update(costs='invalid'),
            lambda x:x['activities'][0].update(participants=[]),
            lambda x:x['activities'][0].update(end=99),
            lambda x:x['activities'][0]['costs'][0].update(delta=1),
            lambda x:x['reminders']['lamp']['acknowledgements'][0].update(at=99),
            lambda x:x['reminders']['lamp'].update(status='pending'),
            lambda x:x['history'][0].update(revision=True)]
        for mutation in mutations:
            state=copy.deepcopy(baseline);mutation(state['private']['exploration'])
            with self.assertRaises(ValueError):session.validate(state)
    def test_old_costs_do_not_require_current_balance(self):
        self.setup();self.ex('advance',self.advance(cost=-12))
        self.ex('advance',{**self.advance(),'costs':[]})
        self.assertEqual(self.saved()['actors']['pc1']['resources']['mp']['value'],0)
    def test_preview_does_not_mutate_source(self):
        self.setup();before=self.saved();rev=self.revision();event=self.exevent('advance',self.advance())
        result=exploration.preview(self.path,event)
        self.assertEqual(self.saved(),before);self.assertEqual(self.revision(),rev)
        self.assertEqual(result['minutes'],{'before':0,'after':5})
        self.assertEqual(result['resources'],[{'actor':'pc1','resource':'mp','before':12,'after':11}])
        session.apply(self.path,result['event'])
        self.assertEqual(self.saved()['clock'],result['minutes']['after'])
    def test_preview_invalid_does_not_mutate(self):
        self.setup();self.schedule();before=self.saved()
        with self.assertRaises(ValueError):exploration.preview(self.path,self.exevent('advance',self.advance(6)))
        self.assertEqual(self.saved(),before)
    def test_preview_stale_rejected(self):
        self.setup();event=self.exevent('advance',self.advance());exploration.preview(self.path,event)
        self.schedule()
        with self.assertRaises(ValueError):session.apply(self.path,event)
    def test_preview_duplicate_no_additional_cost(self):
        self.setup();event=self.exevent('advance',self.advance());session.apply(self.path,event)
        result=exploration.preview(self.path,event)
        self.assertTrue(result['receipt']['duplicate']);self.assertEqual(result['resources'],[])
        self.assertEqual(result['minutes'],{'before':5,'after':5})
    def test_preview_only_exploration(self):
        with self.assertRaises(ValueError):exploration.preview(self.path,self.event('declare',self.declaration()))
    def test_preview_cli_keeps_gm_output_private(self):
        self.setup();self.schedule(due=0)
        event=self.exevent('ack',{'id':'lamp','resolution':'SECRET resolution'})
        eventfile=self.root/'event.json';eventfile.write_text(json.dumps(event),encoding='utf-8')
        out=self.root/'preview.json'
        run=subprocess.run([sys.executable,str(Path(exploration.__file__)),str(self.path),'preview','--event',str(eventfile),'--private-output',str(out)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr);self.assertNotIn('SECRET',run.stdout)
        self.assertTrue(json.loads(out.read_text(encoding='utf-8'))['preview'])
        self.assertEqual(self.reminder()['status'],'due')
    def test_reschedule_pending(self):
        self.setup();self.schedule();event=self.exevent('reschedule',{'id':'lamp','due':10,'every':5,'reason':'new fuel'})
        session.apply(self.path,event);self.assertTrue(session.apply(self.path,event)['duplicate'])
        self.ex('advance',self.advance(10));self.ex('ack',{'id':'lamp','resolution':'done'})
        self.assertEqual(self.reminder()['due'],15)
    def test_reschedule_due_cannot_skip_consequence(self):
        self.setup();self.schedule(due=0);before=self.saved()
        with self.assertRaises(ValueError):self.ex('reschedule',{'id':'lamp','due':10,'every':0,'reason':'skip'})
        self.assertEqual(self.saved(),before)
    def test_reschedule_now_becomes_due(self):
        self.setup();self.schedule();self.ex('reschedule',{'id':'lamp','due':0,'every':0,'reason':'updated deadline'})
        self.assertEqual(self.reminder()['status'],'due')
    def test_reschedule_restore(self):
        self.setup();self.schedule();rev=self.revision()
        self.ex('reschedule',{'id':'lamp','due':10,'every':0,'reason':'new estimate'})
        session.apply(self.path,self.event('',{},changes=[{'kind':'restore','revision':rev}]))
        self.assertEqual(self.reminder()['due'],5)

if __name__=='__main__':unittest.main()
