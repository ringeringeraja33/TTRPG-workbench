import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch as mock_patch
import characters
import session
import test_characters as fixtures


class CharacterPatchTests(unittest.TestCase):
    setUp=fixtures.CharacterImportTests.setUp
    revision=fixtures.CharacterImportTests.revision
    event=fixtures.CharacterImportTests.event
    send=fixtures.CharacterImportTests.send
    declaration=fixtures.CharacterImportTests.declaration
    action=fixtures.CharacterImportTests.action
    entry=fixtures.CharacterImportTests.entry
    manifest=fixtures.CharacterImportTests.manifest
    create=fixtures.CharacterImportTests.create

    def patch(self,changes):return {'schema':1,'sources':['GM explicit advancement decision'],'changes':changes}
    def preview(self,changes):return characters.preview_update(self.path,'pc3',self.patch(changes),'upgrade')
    def saved(self):return session.view(self.path,gm=True)
    def test_partial_update_preserves_untouched_fields(self):
        self.create();before=self.saved();plan=self.preview({'stats':{'spot_hidden':{'label':'侦查','aliases':['Spot Hidden'],'value':70}}})
        self.assertEqual(self.saved(),before);characters.apply_plan(self.path,plan)
        after=self.saved()['state'];old=before['state']
        self.assertEqual(after['actors'],old['actors'])
        self.assertEqual(after['private']['characters']['records']['pc3']['gm_notes'],'GM_SECRET')
        self.assertEqual(after['private']['characters']['records']['pc3']['stats']['spot_hidden']['value'],70)
    def test_capacity_update_preserves_spent_and_other_resources(self):
        self.create();plan=self.preview({'resources':{'hp':{'max':20}}});characters.apply_plan(self.path,plan)
        balances=self.saved()['state']['actors']['pc3']['resources']
        self.assertEqual(balances,{'hp':{'value':18,'max':20},'mp':{'value':8,'max':12}})
        self.assertTrue(characters.apply_plan(self.path,plan)['duplicate'])
    def test_current_balance_injection_rejected(self):
        self.create();before=self.saved()
        with self.assertRaises(ValueError):self.preview({'resources':{'hp':{'value':20,'max':20}}})
        self.assertEqual(self.saved(),before)
    def test_new_resource_requires_initial_balance(self):
        self.create()
        with self.assertRaises(ValueError):self.preview({'resources':{'luck':{'max':3}}})
        characters.apply_plan(self.path,self.preview({'resources':{'luck':{'value':1,'max':3}}}))
        self.assertEqual(self.saved()['state']['actors']['pc3']['resources']['luck'],{'value':1,'max':3})
    def test_remove_stat_is_explicit(self):
        self.create();characters.apply_plan(self.path,self.preview({'remove_stats':['spot_hidden']}))
        self.assertEqual(self.saved()['state']['private']['characters']['records']['pc3']['stats'],{})
    def test_invalid_removal_rejected(self):
        self.create()
        for changes in ({'remove_stats':['missing']},{'remove_stats':['spot_hidden','spot_hidden']},
                        {'remove_stats':['spot_hidden'],'stats':{'spot_hidden':{'label':'Spot','aliases':[],'value':20}}}):
            with self.assertRaises(ValueError):self.preview(changes)
    def test_unknown_fields_and_incomplete_stat_rejected(self):
        self.create()
        for changes in ({'conditions':[]},{'profile':{}},{'resources':None},{'stats':{'spot_hidden':{'value':70}}},{}):
            with self.assertRaises(ValueError):self.preview(changes)
    def test_invalid_patch_schema_and_sources(self):
        self.create()
        for patch in ({'schema':True,'sources':['source'],'changes':{'name':'name'}},
                      {'schema':1,'sources':[],'changes':{'name':'name'}}):
            with self.assertRaises(ValueError):characters.preview_update(self.path,'pc3',patch,'bad')
    def test_pending_mechanics_blocked_cosmetic_allowed(self):
        self.create();data=self.declaration();data.update(actor='pc3',audience=['pc3'],costs=[],stat_ref={'actor':'pc3','stat':'spot_hidden'})
        self.send('declare',data)
        with self.assertRaises(ValueError):self.preview({'remove_stats':['spot_hidden']})
        characters.apply_plan(self.path,self.preview({'name':'New display name'}))
        self.assertEqual(self.action()['stat_snapshot']['value'],60)
    def test_concurrent_merge_uses_one_snapshot(self):
        self.create();original_view=session.view;calls=[]
        concurrent=self.event('',{},changes=[{'kind':'resource','actor':'pc3','resource':'hp','delta':-1}])
        def read_then_change(*args,**kwargs):
            saved=original_view(*args,**kwargs);calls.append(saved['revision'])
            if len(calls)==1:session.apply(self.path,concurrent)
            return saved
        with mock_patch('session.view',side_effect=read_then_change):plan=self.preview({'name':'New name'})
        self.assertEqual(calls,[1]);self.assertEqual(plan['revision'],1)
        with self.assertRaises(ValueError):characters.apply_plan(self.path,plan)
        self.assertEqual(self.saved()['state']['actors']['pc3']['resources']['hp']['value'],9)
    def test_cli_private_preview_and_cold_apply(self):
        self.create();patchfile=self.root/'patch.json';patchfile.write_text(json.dumps(self.patch({'gm_notes':'SECRET update'})),encoding='utf-8')
        out=self.root/'upgrade.json'
        base=[sys.executable,'-X','utf8',str(Path(characters.__file__)),str(self.path)]
        run=subprocess.run(base+['preview-update','--actor','pc3','--patch',str(patchfile),'--event-id','upgrade','--private-output',str(out)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr);self.assertNotIn('SECRET',run.stdout)
        run=subprocess.run(base+['apply','--plan',str(out)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertNotIn('SECRET',json.dumps(session.view(self.path,player='pc3')))
    def test_missing_sheet_requires_explicit_import(self):
        with self.assertRaises(ValueError):characters.preview_update(self.path,'pc1',self.patch({'name':'Name'}),'bad')
    def test_restore_patch_and_resources_together(self):
        self.create();before=self.saved();characters.apply_plan(self.path,self.preview({'resources':{'hp':{'max':20}},'name':'Upgraded'}))
        session.apply(self.path,self.event('',{},changes=[{'kind':'restore','revision':before['revision']}]))
        self.assertEqual(self.saved()['state'],before['state'])


if __name__=='__main__':unittest.main()
