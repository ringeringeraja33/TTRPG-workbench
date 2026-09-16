import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
import characters
import session
import actions
import test_actions


class CharacterImportTests(unittest.TestCase):
    setUp=test_actions.ActionTests.setUp
    revision=test_actions.ActionTests.revision
    event=test_actions.ActionTests.event
    send=test_actions.ActionTests.send
    declaration=test_actions.ActionTests.declaration
    action=test_actions.ActionTests.action

    def entry(self,actor='pc3',mode='create'):
        return {'mode':mode,'id':actor,'name':'新调查者','audience':[actor],'sheet_audience':[actor],
                'resources':{'hp':{'value':10,'max':12},'mp':{'value':8,'max':12}},
                'stats':{'spot_hidden':{'label':'侦查','aliases':['Spot Hidden'],'value':60}},'gm_notes':'GM_SECRET'}

    def manifest(self,entry=None):
        return {'schema':1,'profile':copy.deepcopy(self.state['profile']),'sources':['GM explicit test build'],
                'characters':[entry or self.entry()]}

    def create(self):
        plan=characters.preview(self.path,self.manifest(),'create')
        characters.apply_plan(self.path,plan)
        return plan

    def updated(self):
        return characters.export_manifest(self.path,'pc3')

    def test_preview_read_only_then_apply_retry_preserves_damage(self):
        before=self.path.read_bytes();plan=characters.preview(self.path,self.manifest(),'create')
        self.assertEqual(before,self.path.read_bytes());self.assertEqual(self.revision(),0)
        characters.apply_plan(self.path,plan)
        self.assertTrue(characters.apply_plan(self.path,plan)['duplicate'])
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc3']['resources']['hp']['value'],10)
        self.assertTrue(plan['changes'])

    def test_update_capacity_preserves_spent_and_conditions(self):
        self.create()
        event=self.event('unused',{});event['changes']=[{'kind':'conditions','actor':'pc3','value':['injured']}]
        session.apply(self.path,event)
        manifest=self.updated();manifest['characters'][0]['resources']['hp']['max']=20
        characters.apply_plan(self.path,characters.preview(self.path,manifest,'upgrade'))
        actor=session.view(self.path,gm=True)['state']['actors']['pc3']
        self.assertEqual(actor['resources']['hp'],{'value':18,'max':20})
        self.assertEqual(actor['conditions'],['injured'])

    def test_update_cannot_import_current_values_or_remove_resource(self):
        self.create();manifest=self.updated();manifest['characters'][0]['resources']['hp']['value']=12
        with self.assertRaises(ValueError):characters.preview(self.path,manifest,'refill')
        manifest=self.updated();manifest['characters'][0]['resources'].pop('hp')
        with self.assertRaises(ValueError):characters.preview(self.path,manifest,'remove')
        self.assertEqual(self.revision(),1)

    def test_capacity_reduction_clamps_without_refilling(self):
        self.create();manifest=self.updated();manifest['characters'][0]['resources']['hp']['max']=5
        characters.apply_plan(self.path,characters.preview(self.path,manifest,'shrink'))
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc3']['resources']['hp'],{'value':5,'max':5})

    def test_alias_lookup_is_case_whitespace_and_unicode_aware(self):
        self.create();state=session.view(self.path,gm=True)['state']
        for alias in ('侦查','spot_hidden',' SPOT   HIDDEN '):
            self.assertEqual(characters.resolve_stat(state,'pc3',alias)['id'],'spot_hidden')
        with self.assertRaises(ValueError):characters.resolve_stat(state,'pc3','missing')

    def test_ambiguous_alias_or_wrong_numeric_type_rejected(self):
        manifest=self.manifest();stats=manifest['characters'][0]['stats']
        stats['other']={'label':'Other','aliases':['spot hidden'],'value':20}
        with self.assertRaises(ValueError):characters.preview(self.path,manifest,'ambiguous')
        manifest=self.manifest();manifest['characters'][0]['stats']['spot_hidden']['value']=True
        with self.assertRaises(ValueError):characters.preview(self.path,manifest,'bool')
        self.assertEqual(self.revision(),0)

    def test_nested_unknown_fields_and_invalid_audiences_rejected(self):
        for path in ('stat','resource','audience'):
            manifest=self.manifest();entry=manifest['characters'][0]
            if path=='stat':entry['stats']['spot_hidden']['gm_secret']='hidden'
            elif path=='resource':entry['resources']['hp']['gm_secret']='hidden'
            else:entry['sheet_audience']='pc3'
            with self.assertRaises(ValueError):characters.preview(self.path,manifest,'invalid')
        self.assertEqual(self.revision(),0)

    def test_player_sheet_does_not_publish_gm_notes_or_sources(self):
        self.create();own=session.view(self.path,player='pc3')
        self.assertEqual(own['characters']['pc3']['stats']['spot_hidden']['value'],60)
        self.assertNotIn('GM_SECRET',json.dumps(own))
        self.assertEqual(session.view(self.path,player='pc1')['characters'],{})
        self.assertEqual(session.view(self.path)['characters'],{})

    def test_public_sheet_does_not_publish_private_resource_actor(self):
        manifest=self.manifest();manifest['characters'][0]['sheet_audience']=['all']
        characters.apply_plan(self.path,characters.preview(self.path,manifest,'public'))
        view=session.view(self.path)
        self.assertIn('pc3',view['characters']);self.assertNotIn('pc3',view['actors'])
        self.assertNotIn('resources',view['characters']['pc3'])

    def test_pending_action_binds_stat_snapshot_and_blocks_mechanical_update(self):
        self.create();data=self.declaration();data['actor']='pc3';data['audience']=['pc3'];data['costs']=[]
        data['stat_ref']={'actor':'pc3','stat':'Spot Hidden'}
        self.send('declare',data)
        self.assertEqual(self.action()['stat_snapshot']['value'],60)
        manifest=self.updated();manifest['characters'][0]['stats']['spot_hidden']['value']=70
        with self.assertRaises(ValueError):characters.preview(self.path,manifest,'blocked')
        self.send('cancel',{'reason':'finish pending preparation'})
        characters.apply_plan(self.path,characters.preview(self.path,manifest,'advance'))
        self.assertEqual(self.action()['stat_snapshot']['value'],60)

    def test_existing_combat_participant_blocks_mechanical_import(self):
        self.create();event=self.event('unused',{});event['changes']=[{'kind':'combat','step':'start','data':
            {'id':'fight','audience':['all'],'order':['pc3'],'refresh':[]}}]
        session.apply(self.path,event)
        manifest=self.updated();manifest['characters'][0]['stats']['spot_hidden']['value']=70
        with self.assertRaises(ValueError):characters.preview(self.path,manifest,'blocked')
        manifest=self.updated();manifest['characters'][0]['name']='改名'
        characters.apply_plan(self.path,characters.preview(self.path,manifest,'rename'))
        self.assertEqual(session.view(self.path,gm=True)['state']['private']['combat']['order'],['pc3'])

    def test_new_character_can_join_encounter_without_inheriting_facts(self):
        self.create();event=self.event('unused',{});event['changes']=[{'kind':'combat','step':'start','data':
            {'id':'fight','audience':['all'],'order':['pc1'],'refresh':[]}}];session.apply(self.path,event)
        event=self.event('unused',{});event['changes']=[{'kind':'combat','step':'join','data':
            {'actor':'pc3','position':1,'participation':'this-round','refresh':[],'reason':'arrives'}}];session.apply(self.path,event)
        self.assertEqual(session.view(self.path,gm=True)['state']['private']['combat']['order'],['pc1','pc3'])
        self.assertEqual(session.view(self.path,player='pc3')['facts'],[])

    def test_stale_plan_profile_mismatch_or_changed_plan_rejected(self):
        plan=characters.preview(self.path,self.manifest(),'create')
        self.send('declare',self.declaration())
        with self.assertRaises(ValueError):characters.apply_plan(self.path,plan)
        manifest=self.manifest();manifest['profile']['edition']='other'
        with self.assertRaises(ValueError):characters.preview(self.path,manifest,'wrong')
        plan=characters.preview(self.path,self.manifest(),'fresh');plan['event']['resolution']='tampered'
        with self.assertRaises(ValueError):characters.apply_plan(self.path,plan)

    def test_batch_failure_is_atomic(self):
        manifest=self.manifest();bad=self.entry('pc4');bad['resources']['hp']['value']=999
        manifest['characters'].append(bad)
        event=self.event('unused',{});event['changes']=[{'kind':'characters','manifest':manifest}]
        with self.assertRaises(ValueError):session.apply(self.path,event)
        self.assertNotIn('pc3',session.view(self.path,gm=True)['state']['actors'])
        self.assertEqual(self.revision(),0)

    def test_duplicate_actor_create_and_missing_update_fail(self):
        self.create()
        with self.assertRaises(ValueError):characters.preview(self.path,self.manifest(),'duplicate')
        manifest=self.updated();manifest['characters'][0]['id']='absent'
        with self.assertRaises(ValueError):characters.preview(self.path,manifest,'missing')

    def test_export_update_roundtrip_preserves_current_resources(self):
        self.create();manifest=self.updated();characters.apply_plan(self.path,characters.preview(self.path,manifest,'roundtrip'))
        self.assertEqual(session.view(self.path,gm=True)['state']['actors']['pc3']['resources']['hp']['value'],10)
        created=characters.export_manifest(self.path,'pc3','create')
        self.assertEqual(created['characters'][0]['resources']['hp']['value'],10)

    def test_cli_private_preview_apply_and_export(self):
        manifest=self.root/'manifest.json';manifest.write_text(json.dumps(self.manifest(),ensure_ascii=False),encoding='utf-8')
        plan=self.root/'plan.json';export=self.root/'export.json'
        base=[sys.executable,'-X','utf8',str(Path(characters.__file__)),str(self.path)]
        for args in (['preview','--manifest',str(manifest),'--event-id','cli-import','--private-output',str(plan)],
                     ['apply','--plan',str(plan)],['apply','--plan',str(plan)],
                     ['export','--actor','pc3','--private-output',str(export)]):
            run=subprocess.run(base+args,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(run.returncode,0,run.stderr);self.assertNotIn('GM_SECRET',run.stdout)
        self.assertEqual(json.loads(export.read_text(encoding='utf-8')),self.updated())

    def test_restore_removes_import_without_destroying_history(self):
        self.create();event=self.event('unused',{});event['changes']=[{'kind':'restore','revision':0}]
        session.apply(self.path,event)
        self.assertNotIn('pc3',session.view(self.path,gm=True)['state']['actors'])
        self.assertNotIn('characters',session.view(self.path,gm=True)['state']['private'])


if __name__=='__main__':unittest.main()
