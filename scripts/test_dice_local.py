import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from unittest.mock import patch
from dice_local import execute, read, export_log, visible_log
from vendor.dice_rd import roll, Expression, pool


class RDTests(unittest.TestCase):
    def test_keeps_arithmetic_and_raw_faces(self):
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=[0,5,2,3]):
            value=roll('(4d6k3+2)*5/2')['results'][0]
        self.assertEqual(value['total'],37.5)
        self.assertEqual(value['dice'][0]['raw'],[1,6,3,4])
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=[0,19]):
            self.assertEqual(roll('2d20q1')['results'][0]['total'],1)

    def test_validation_and_zero_division(self):
        with patch('vendor.dice_rd.secrets.randbelow') as rng:
            for expr in ['1d0','3d6k4','1d6junk','0#d','101#d','100#100d6','('*50+'d'+')'*50]:
                with self.assertRaises(ValueError): roll(expr)
            rng.assert_not_called()
        with self.assertRaises(ValueError): roll('2/0')

    def test_default_fate_percentile_and_pool(self):
        with patch('vendor.dice_rd.secrets.randbelow',return_value=0):
            self.assertEqual(roll('df')['results'][0]['total'],-4)
            self.assertEqual(roll('2#d',20)['results'][1]['dice'][0]['faces'],20)
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=[0,0,1]):
            self.assertEqual(roll('b')['results'][0]['total'],10)
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=[0,0,1]):
            self.assertEqual(roll('p')['results'][0]['total'],100)
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=[9,0,7]):
            result=pool(2,10,8)
        self.assertEqual(result['waves'],[[10,1],[8]])
        self.assertEqual(result['total'],2)


class LocalTableTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        self.root=Path(t.name); self.db=self.root/'table.sqlite'
        self.send('.kp')

    def send(self,cmd,actor='gm',scope='s'):
        revision=read(self.db,scope)['revision']
        return execute(self.db,scope,actor,cmd,str(revision),revision)['result']

    def register(self,who,name='调查员',stats='STR60 CON60 SIZ60 DEX60 INT60 POW60 EDU60 LUCK50 SAN60 HP12 侦查60'):
        self.send('.nn '+name,who); self.send('.st '+stats,who)

    def test_cards_named_import_copy_rename_scope(self):
        self.register('p')
        self.send('.st莉娜-STR50 CON70','p')
        self.assertEqual(self.send('.st show力量','p')['value'],50)
        self.send('.st cp 莉娜 @q','p'); self.send('.nn 莉娜','q')
        self.send('.stc STR+5','q')
        self.assertEqual(self.send('.st show力量','p')['value'],50)
        self.send('.team set @p')
        self.send('.st rename 新莉娜','p')
        self.assertEqual(read(self.db,'s')['team']['p'],['p','新莉娜'])
        self.assertEqual(read(self.db,'other')['players'],{})
        with self.assertRaises(ValueError): self.send('.st rm 新莉娜','p')

    def test_atomic_team_failure_and_permissions(self):
        self.register('p'); self.register('q',stats='HP1 SAN40')
        self.send('.team set @p @q')
        before=read(self.db,'s')
        with self.assertRaises(ValueError): self.send('.team hp all 2')
        self.assertEqual(read(self.db,'s'),before)
        with self.assertRaises(ValueError): self.send('.team hp all 1','p')
        with self.assertRaises(ValueError): self.send('.kp','p')
        result=self.send('.team hp all 1')
        self.assertEqual(result['members']['p']['stats']['HP'],11)
        self.assertEqual(result['members']['q']['stats']['HP'],0)

    def test_log_visibility_restart_export_idempotence(self):
        self.send('.log on 测试')
        revision=read(self.db,'s')['revision']
        with patch('vendor.dice_rd.secrets.randbelow',return_value=41) as rng:
            one=execute(self.db,'s','p','.rhd100','secret',revision)
            two=execute(self.db,'s','p','.rhd100','secret',revision)
            self.assertEqual(one,two); self.assertEqual(rng.call_count,1)
        self.send('我走向门口','p')
        self.assertEqual(len(visible_log(read(self.db,'s'),'q','测试')),1)
        self.assertEqual(len(visible_log(read(self.db,'s'),'gm','测试')),2)
        self.send('.log off')
        dest=self.root/'记录.html'; export_log(self.db,'s','q','测试',dest,'html')
        self.assertIn('我走向门口',dest.read_text(encoding='utf-8'))
        self.assertNotIn('secret',dest.read_text(encoding='utf-8'))
        with self.assertRaises(FileExistsError): export_log(self.db,'s','q','测试',dest)
        output=subprocess.check_output([sys.executable,'-X','utf8',str(Path(__file__).with_name('dice_local.py')),'--db',str(self.db),'--scope','s','--actor','p'],encoding='utf-8')
        self.assertEqual(json.loads(output)['revision'],read(self.db,'s')['revision'])

    def test_private_cli_never_prints_result(self):
        revision=read(self.db,'s')['revision']; path=self.root/'private.json'
        args=[sys.executable,'-X','utf8',str(Path(__file__).with_name('dice_local.py')),'--db',str(self.db),'--scope','s','--actor','p','--command','.rh1d100','--operation','hidden','--expected',str(revision),'--private-output',str(path)]
        result=json.loads(subprocess.check_output(args,encoding='utf-8'))
        self.assertNotIn('result',result); self.assertTrue(result['private_result_saved'])
        self.assertIn('result',json.loads(path.read_text(encoding='utf-8')))

    def test_sanity_fumble_bout_and_development(self):
        self.register('p',stats='SAN60 HP12 侦查60')
        with patch('vendor.dice_rd.secrets.randbelow',return_value=99):
            result=self.send('.sc 0/1d10','p')
        self.assertEqual(result['after'],50); self.assertTrue(result['int_check_required'])
        self.send('.san bout on','p')
        with patch('vendor.dice_rd.secrets.randbelow') as rng:
            self.assertEqual(self.send('.sc 0/1d10','p')['loss'],0); rng.assert_not_called()
        with self.assertRaises(ValueError): self.send('.en 侦查','p')
        self.send('.mark @p 侦查')
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=[95,2]):
            self.assertEqual(self.send('.en 侦查','p')['after'],63)
        with self.assertRaises(ValueError): self.send('.en 侦查','p')

    def test_house_and_core_are_explicit(self):
        with patch('vendor.dice_rd.secrets.randbelow',return_value=2):
            self.assertEqual(self.send('.ra 60')['outcome'],'critical')
            self.assertNotEqual(self.send('.rc 60')['outcome'],'critical')
        self.send('.crule set 2')
        with patch('vendor.dice_rd.secrets.randbelow',return_value=2):
            self.assertNotEqual(self.send('.ra 60')['outcome'],'critical')

    def test_npc_initiative_clues_and_local_data(self):
        self.send('.npc st管家-HP10 侦查30')
        with patch('vendor.dice_rd.secrets.randbelow',return_value=10):
            self.assertEqual(self.send('.rc 管家:侦查')['target'],30)
        self.send('.ri +4 地精')
        with self.assertRaises(ValueError): self.send('.ri +4 地精')
        self.send('.init set 地精 9'); self.assertEqual(self.send('.init')[0]['value'],9)
        cid=self.send('.clue 钥匙在门边','p')['id']
        with self.assertRaises(ValueError): self.send('.clue rm '+cid,'q')
        self.send('.clue rm '+cid,'p')
        self.send('.des set 门厅|这里有一扇门','p')
        self.assertEqual(self.send('.des 门厅','p')['text'],'这里有一扇门')
        with self.assertRaises(ValueError): self.send('.des 门厅','q')
        self.send('.deck install 测试 ["门", "钥匙"]')
        self.assertEqual(len(self.send('.draw 测试 3')['draws']),3)

    def test_failed_edits_and_reused_operation(self):
        self.register('p'); before=read(self.db,'s')
        for command in ('.st HP+2INT-999','.st HP+2 垃圾','.st INT60灵感70','.system update','.fire'):
            with self.assertRaises(ValueError): self.send(command,'p')
            self.assertEqual(read(self.db,'s'),before)
        rev=before['revision']; execute(self.db,'s','p','.rf','op',rev)
        with self.assertRaises(ValueError): execute(self.db,'s','p','.rf','op',rev+1)
        with self.assertRaises(ValueError): execute(self.db,'s','p','.rf','new',rev)

    def test_opposition_house_batch_and_history(self):
        with patch('vendor.dice_rd.secrets.randbelow',return_value=29):
            self.assertTrue(self.send('.rcv 60','p')['pending'])
            result=self.send('.rcv 80','q')
        self.assertEqual(result['winner'],'q')
        with patch('vendor.dice_rd.secrets.randbelow',return_value=2):
            self.assertEqual(len(self.send('.rcl 60 3')['checks']),3)
        self.send('.rc 50','p')
        self.assertEqual(len(self.send('.hiy','p')['history']),1)

    def test_document_and_ooc_exports(self):
        self.send('.log on Test'); self.send('进入门厅（场外(嵌套)讨论）继续调查','p'); self.send('.r(1+2)*3','p'); self.send('.log off')
        text=self.root/'clean.txt'; export_log(self.db,'s','p','Test',text,'clean-txt')
        content=text.read_text(encoding='utf-8'); self.assertNotIn('场外',content); self.assertIn('.r(1+2)*3',content)
        doc=self.root/'test.docx'; export_log(self.db,'s','p','Test',doc,'docx')
        with zipfile.ZipFile(doc) as archive:
            xml=archive.read('word/document.xml'); ET.fromstring(xml)
            self.assertIn('进入门厅',xml.decode('utf-8'))

    def test_profiles_local_switches_and_decks(self):
        with self.assertRaises(ValueError): self.send('.magic5e 火球术')
        self.send('.lookup import dnd5e-2014 {"source":"Original test fixture; no official rules","entries":{"示例术":"测试条目"}}')
        self.assertEqual(self.send('.5ey 示例术')['text'],'测试条目')
        with self.assertRaises(ValueError): self.send('.3ry 示例术')
        self.send('.admin DisabledDraw=1')
        with self.assertRaises(ValueError): self.send('.draw test')
        self.send('.admin DisabledDraw=0')
        self.send('.deck install ti ["Original test symptom"]')
        self.assertEqual(self.send('.ti')['draws'],['Original test symptom'])
        self.send('.strRoll {nick}: {res}')
        self.assertTrue(self.send('.r1d6')['rendered'].startswith('gm:'))
        self.send('.group simple 1'); self.assertNotIn('rendered',self.send('.r1d6'))

    def test_private_history_and_cross_scope_logs(self):
        self.send('.log on Same'); self.send('public','p'); self.send('.group secret 1')
        revision=read(self.db,'s')['revision']
        response=execute(self.db,'s','p','.rc 60','hidden-check',revision)
        self.assertIsInstance(response['audience'],list)
        self.assertFalse(any(x['operation']=='hidden-check' for x in visible_log(read(self.db,'s'),'q','Same')))
        self.send('.kp','gm','second'); self.send('.log on Same','gm','second'); self.send('second public','p','second')
        result=self.send('.log group get s,second Same','p')
        self.assertEqual({x['scope'] for x in result['entries']},{'s','second'})
        self.send('hello','q')
        with self.assertRaises(ValueError): self.send('.log group get s,second Same','q')

    def test_new_characters_survive_restart(self):
        batch=self.send('.coc5','p'); bid=batch['batch']
        self.send('.coc take '+bid+' 2 ada 阿达','p')
        self.assertEqual(read(self.db,'s')['players']['p']['cards']['ada']['stats'],batch['candidates'][1]['stats'])
        self.assertEqual(len(self.send('.dnd 2','q')['candidates']),2)


if __name__=='__main__': unittest.main()
