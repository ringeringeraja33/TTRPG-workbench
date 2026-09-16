import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import actions
import dice_local
import session
import session_review
from test_session import initial


class ActionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root/'战役.sqlite'
        self.state = initial()
        self.state['actors']['pc2'] = copy.deepcopy(self.state['actors']['pc1'])
        self.state['actors']['pc2']['audience'] = ['pc2']
        self.state['pending'] = [{'rule':'unrelated pending ruling'}]
        session.init(self.path, self.state)

    def revision(self): return session.view(self.path, gm=True)['revision']

    def declaration(self, mode='tool'):
        return {'actor':'pc1', 'summary':'检查门闩', 'intent':'GM_SECRET intent',
                'method':'use tools', 'stakes':'GM_SECRET stakes', 'audience':['pc1'],
                'roll':{'mode':mode, 'expression':'1d6'},
                'costs':[{'kind':'resource','actor':'pc1','resource':'mp','delta':-1}]}

    def event(self, step, data, aid='a', **extra):
        rev = self.revision()
        result = {'id':'event-'+str(rev), 'revision':rev, 'profile':self.state['profile'],
                  'input':'synthetic action fixture', 'resolution':'explicit GM adjudication',
                  'sources':['GM original test procedure'],
                  'changes':[{'kind':'action','action':aid,'step':step,'data':data}]}
        result.update(extra)
        return result

    def send(self, step, data, aid='a'):
        return session.apply(self.path, self.event(step,data,aid))

    def action(self, aid='a'): return actions.view(self.path, gm=True)['actions'][aid]

    def roll_action(self):
        self.send('declare', self.declaration())
        self.send('roll', {})

    def settlement(self):
        return {'outcome':'failure', 'effects':[{'kind':'resource','actor':'pc1','resource':'hp','delta':-2}]}

    def test_roll_retry_does_not_reroll_and_spend_only_at_settlement(self):
        self.send('declare', self.declaration())
        event = self.event('roll', {})
        with patch('vendor.dice_rd.secrets.randbelow', return_value=3) as rng:
            session.apply(self.path, event)
            evidence = self.action()['evidence']
            self.assertTrue(session.apply(self.path,event)['duplicate'])
            self.assertEqual(rng.call_count, 1)
        self.assertEqual(evidence, self.action()['evidence'])
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['value'],12)
        event = self.event('settle', self.settlement())
        session.apply(self.path,event)
        self.assertTrue(session.apply(self.path,event)['duplicate'])
        saved = session.view(self.path,gm=True)['state']
        self.assertEqual(saved['actors']['pc1']['resources']['mp']['value'],11)
        self.assertEqual(saved['actors']['pc1']['resources']['hp']['value'],10)
        self.assertEqual(saved['pending'], self.state['pending'])
        self.assertEqual(saved['private']['positions'],self.state['private']['positions'])

    def test_cold_recovery_preserves_pending_choice_and_evidence(self):
        self.roll_action()
        self.send('wait',{'actor':'pc1','prompt':'是否继续？','options':{'yes':'继续','no':'停止'}})
        output = self.root/'gm.json'
        run = subprocess.run([sys.executable,'-X','utf8',str(Path(actions.__file__)),str(self.path),
                              'view','--private-output',str(output)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertNotIn('GM_SECRET',run.stdout)
        restored=json.loads(output.read_text(encoding='utf-8'))['actions']['a']
        self.assertEqual(restored,self.action())
        with self.assertRaises(ValueError): self.send('settle',self.settlement())
        with self.assertRaises(ValueError): self.send('choose',{'actor':'pc2','option':'yes'})
        self.send('choose',{'actor':'pc1','option':'yes'})
        self.send('settle',self.settlement())
        self.assertEqual(self.action()['decisions'][0]['selected'],'yes')

    def test_player_projection_and_recap_keep_private_details(self):
        self.roll_action()
        self.send('wait',{'actor':'pc1','prompt':'选择','options':{'ok':'同意'}})
        self.assertEqual(actions.view(self.path,player='pc2')['actions'],{})
        own=session.view(self.path,player='pc1')['actions']['a']
        self.assertEqual(set(own),{'summary','status','decision'})
        self.assertNotIn('GM_SECRET',json.dumps(own))
        self.assertNotIn('evidence',own)
        recap=session_review.recap(self.path,gm=True)
        self.assertEqual(recap['next_prep']['pending_actions'][0]['status'],'waiting')
        self.assertNotIn('pending_actions',session_review.recap(self.path,player='pc2'))

    def test_invalid_settlement_rolls_back_cost_and_status(self):
        self.roll_action(); rev=self.revision()
        bad=self.settlement();bad['effects'][0]['delta']=-999
        with self.assertRaises(ValueError): self.send('settle',bad)
        self.assertEqual(self.revision(),rev)
        self.assertEqual(self.action()['status'],'rolled')
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['mp']['value'],12)
        self.send('settle',self.settlement())

    def test_changed_request_stale_revision_and_profile_fail_before_rng(self):
        self.send('declare',self.declaration())
        event=self.event('roll',{})
        with patch('vendor.dice_rd.secrets.randbelow',return_value=1) as rng:
            for bad in (dict(event,revision=0),dict(event,profile={'system':'wrong'})):
                with self.assertRaises(ValueError): session.apply(self.path,bad)
            rng.assert_not_called()
            session.apply(self.path,event)
            changed=copy.deepcopy(event);changed['resolution']='changed request'
            with self.assertRaises(ValueError): session.apply(self.path,changed)
            self.assertEqual(rng.call_count,1)

    def test_concurrent_identical_roll_consumes_randomness_once(self):
        self.send('declare',self.declaration());event=self.event('roll',{})
        with patch('vendor.dice_rd.secrets.randbelow',return_value=1) as rng:
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(lambda _:session.apply(self.path,event),range(2)))
            self.assertEqual(rng.call_count,1)
        self.assertEqual(sorted(r['duplicate'] for r in results),[False,True])

    def test_no_roll_and_cancelled_actions(self):
        data=self.declaration();data['roll']=None
        self.send('declare',data)
        with self.assertRaises(ValueError): self.send('roll',{})
        self.send('settle',{'outcome':'no-check','effects':[]})
        self.assertIsNone(self.action()['evidence'])
        self.send('declare',self.declaration(),'b')
        self.send('cancel',{'reason':'player withdrew before attempt'},'b')
        with self.assertRaises(ValueError): self.send('roll',{},'b')
        self.assertEqual(self.action('b')['status'],'cancelled')

    def test_manual_roll_is_labelled_unverified(self):
        self.send('declare',self.declaration('manual'))
        self.send('roll',{'total':4,'note':'player reported physical d6'})
        self.assertFalse(self.action()['evidence']['verified_randomness'])
        self.assertNotIn('randomness',self.action()['evidence'])

    def receipt_spec(self,operation='die',command='.r 1d6'):
        path=self.root/'dice.sqlite'
        if not path.exists(): dice_local.execute(path,'table','p','.nn Hero','setup',0)
        revision=dice_local.read(path,'table')['revision']
        receipt=dice_local.execute(path,'table','p',command,operation,revision)
        data=self.declaration('receipt')
        data['roll']['source']={'database':str(path),'scope':'table','actor':'p','operation':operation}
        return data,receipt

    def test_bridge_imports_existing_receipt_without_reroll_or_dice_mutation(self):
        data,receipt=self.receipt_spec(command='.rh 1d6')
        path=Path(data['roll']['source']['database']);before=path.read_bytes()
        self.send('declare',data)
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=AssertionError('must not reroll')):
            self.send('roll',{})
        self.assertEqual(self.action()['evidence']['roll'],receipt['result'])
        self.assertEqual(self.action()['evidence']['audience'],['p'])
        self.assertEqual(path.read_bytes(),before)
        self.send('settle',self.settlement())
        self.assertEqual(path.read_bytes(),before)

    def test_bridge_rejects_wrong_actor_expression_and_resource_command(self):
        for index,command in enumerate(('.r 1d8','.st HP12')):
            data,_=self.receipt_spec('die'+str(index),command)
            self.send('declare',data,'a'+str(index))
            with self.assertRaises(ValueError): self.send('roll',{},'a'+str(index))
        data,_=self.receipt_spec('wrongactor')
        data['roll']['source']['actor']='someone-else'
        self.send('declare',data)
        with self.assertRaises(ValueError): self.send('roll',{})

    def test_receipt_cannot_be_bound_or_consumed_twice(self):
        data,_=self.receipt_spec();self.send('declare',data);self.send('roll',{})
        with self.assertRaises(ValueError): self.send('declare',data,'b')
        copied=self.root/'copy.sqlite';shutil.copyfile(data['roll']['source']['database'],copied)
        data['roll']['source']['database']=str(copied)
        self.send('declare',data,'c')
        with self.assertRaises(ValueError): self.send('roll',{},'c')

    def test_missing_receipt_can_resume_after_source_commits(self):
        data,_=self.receipt_spec();data['roll']['source']['operation']='later'
        self.send('declare',data);event=self.event('roll',{})
        with self.assertRaises(ValueError): session.apply(self.path,event)
        self.receipt_spec('later')
        session.apply(self.path,event)
        self.assertEqual(self.action()['status'],'rolled')

    def test_restore_keeps_workflow_on_active_branch(self):
        self.roll_action();before=self.revision()
        self.send('settle',self.settlement())
        event=self.event('unused',{})
        event['changes']=[{'kind':'restore','revision':before}]
        session.apply(self.path,event)
        self.assertEqual(self.action()['status'],'rolled')
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['hp']['value'],12)
        self.send('settle',self.settlement())
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['hp']['value'],10)

    def test_workflow_cannot_be_overwritten_or_mixed_with_other_changes(self):
        self.roll_action()
        event=self.event('settle',self.settlement())
        event['changes'].append({'kind':'clock','minutes':1})
        with self.assertRaises(ValueError):session.apply(self.path,event)
        event['changes']=[{'kind':'private','value':{}}]
        with self.assertRaises(ValueError):session.apply(self.path,event)
        self.assertEqual(self.action()['status'],'rolled')

    def test_invalid_declaration_and_unaffordable_cost_do_not_roll(self):
        for update in ({'costs':[{'kind':'resource','actor':'pc1','resource':'mp','delta':-99}]},
                       {'roll':{'mode':'tool','expression':'1d6 invalid'}}, {'actor':'missing'}):
            data=self.declaration();data.update(update)
            with patch('vendor.dice_rd.secrets.randbelow',side_effect=AssertionError('no roll')):
                with self.assertRaises((ValueError,KeyError)):self.send('declare',data)
            self.assertEqual(self.revision(),0)

    def test_terminal_action_rejects_new_operation(self):
        self.roll_action();self.send('settle',self.settlement())
        for step,data in (('settle',self.settlement()),('roll',{}),('cancel',{'reason':'too late'})):
            with self.assertRaises(ValueError):self.send(step,data)

    def test_rolled_attempt_cannot_cancel_to_avoid_cost(self):
        self.roll_action()
        with self.assertRaises(ValueError): self.send('cancel',{'reason':'avoid cost'})
        self.assertEqual(self.action()['status'],'rolled')

    def test_reserved_budget_requires_explicit_release_before_external_spend(self):
        self.roll_action()
        event=self.event('unused',{})
        event['changes']=[{'kind':'resource','actor':'pc1','resource':'mp','delta':-12}]
        with self.assertRaises(ValueError): session.apply(self.path,event)
        self.send('release',{'reason':'GM adjudicated forced resource loss'})
        event.update(id='forced-loss',revision=self.revision())
        session.apply(self.path,event)
        with self.assertRaises(ValueError):self.send('settle',self.settlement())
        self.assertEqual(self.action()['status'],'rolled')
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc1']['resources']['hp']['value'],12)

    def test_later_choice_does_not_erase_earlier_decision(self):
        self.roll_action()
        for option in ('first','second'):
            self.send('wait',{'actor':'pc1','prompt':option,'options':{option:'continue'}})
            self.send('choose',{'actor':'pc1','option':option})
        self.assertEqual([d['selected'] for d in self.action()['decisions']],['first','second'])

    def test_import_requires_explicit_faces_at_declaration(self):
        data,_=self.receipt_spec()
        data['roll']['expression']='2d'
        with self.assertRaises(ValueError):self.send('declare',data)
        self.assertEqual(self.revision(),0)


if __name__=='__main__':unittest.main()
