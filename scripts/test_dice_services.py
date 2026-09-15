"""Local event, timer and nested deck integration tests with synthetic inputs."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from dice_local import execute, read, visible_log, wait_for_timers
from dice_services import draw_deck, validate_decks


class LocalServiceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name); self.db = self.root / 'dice.sqlite'
        self.send('.kp', 'gm')
        self.send('.log on events', 'gm')

    def send(self, command, actor='p', operation=None):
        revision = read(self.db, 's')['revision']
        return execute(self.db, 's', actor, command, operation or str(revision), revision)

    def test_replies_are_opt_in_private_and_non_executable(self):
        self.send('.reply set 秘密|.r1d100')
        self.assertNotIn('reply', self.send('秘密')['result'])
        self.send('.reply enable 秘密')
        revision = read(self.db, 's')['revision']
        value = execute(self.db, 's', 'p', '秘密', 'private-reply', revision)
        self.assertEqual(value['result']['reply'], '.r1d100')
        self.assertEqual(value['audience'], ['p'])
        self.assertEqual(value, execute(self.db, 's', 'p', '秘密', 'private-reply', revision))
        self.assertNotIn('reply', self.send('秘密', 'q')['result'])
        self.assertNotIn('reply', self.send('秘密 extra')['result'])
        self.assertFalse(any(x['operation']=='private-reply' for x in visible_log(read(self.db,'s'),'q','events')))
        self.send('.reply disable 秘密')
        self.assertNotIn('reply', self.send('秘密')['result'])

    def test_published_reply_is_an_explicit_snapshot(self):
        self.send('.reply set rules|Use core .rc', 'gm')
        with self.assertRaises(ValueError): self.send('.reply publish rules')
        self.send('.reply publish rules', 'gm')
        self.assertEqual(self.send('rules')['result']['reply'], 'Use core .rc')
        self.send('.reply set rules|Changed private draft', 'gm')
        self.assertEqual(self.send('rules')['result']['reply'], 'Use core .rc')
        self.send('.reply unpublish rules', 'gm')
        self.assertNotIn('reply', self.send('rules')['result'])

    def test_welcome_join_replay_leave_and_template_boundaries(self):
        self.send('.welcome 欢迎 {name} ({actor})', 'gm')
        self.send('.welcome open', 'gm')
        revision = read(self.db, 's')['revision']
        welcome = execute(self.db, 's', 'p', '.join 林蔚', 'join-p', revision)
        self.assertEqual(welcome['result']['welcome'], '欢迎 林蔚 (p)')
        self.assertEqual(welcome, execute(self.db, 's', 'p', '.join 林蔚', 'join-p', revision))
        self.assertNotIn('welcome', self.send('.join 林蔚')['result'])
        self.send('.nn 调查员'); before = copy.deepcopy(read(self.db,'s')['players']['p']['cards'])
        self.send('.leave'); self.assertEqual(read(self.db,'s')['players']['p']['cards'],before)
        self.assertIn('welcome', self.send('.join 林蔚')['result'])
        self.send('.welcome close','gm'); self.assertNotIn('welcome',self.send('.join 沈青','q')['result'])
        with self.assertRaises(ValueError): self.send('.welcome {secret}','gm')

    def test_timers_recover_require_ack_and_isolate_owners(self):
        with patch('dice_local.time.time', return_value=100):
            timer = self.send('.clock 10 收尾')['result']['id']
            with self.assertRaises(ValueError): self.send('.clock ack '+timer)
        with patch('dice_local.time.time', return_value=111):
            value = self.send('.clock poll')
            self.assertEqual(value['audience'],['p'])
            self.assertEqual(value['result']['clocks'][timer]['label'],'收尾')
            self.assertIn(timer, self.send('.clock poll')['result']['clocks'])
            self.assertEqual(self.send('.clock list','q')['result']['clocks'],{})
            with self.assertRaises(ValueError): self.send('.clock ack '+timer,'q')
            self.send('.clock ack '+timer)
            self.assertEqual(self.send('.clock poll')['result']['clocks'],{})
        timer2 = self.send('.clock 60 下一个节点')['result']['id']
        self.send('.clock cancel '+timer2)
        self.assertEqual(self.send('.clock list')['result']['clocks'][timer2]['status'],'cancelled')

    def test_timer_foreground_wait_private_output_and_timeout(self):
        with patch('dice_local.time.time', return_value=1): self.send('.clock 1 已到期')
        rev = read(self.db,'s')['revision']; output=self.root/'提醒.json'
        run=subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).with_name('dice_local.py')),
                            '--db',str(self.db),'--scope','s','--actor','p','--wait-timers','1',
                            '--expected',str(rev),'--operation','timer-delivery','--private-output',str(output)],
                           capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertNotIn('已到期',run.stdout)
        self.assertIn('已到期',output.read_text(encoding='utf-8'))
        self.assertTrue(json.loads(output.read_text(encoding='utf-8'))['result']['clocks'])
        with patch('dice_local.time.monotonic',side_effect=[0,2]):
            self.assertFalse(wait_for_timers(self.db,'s','q',1))
        with self.assertRaises(ValueError): wait_for_timers(self.db,'s','p',61)

    def test_nested_weighted_decks_preserve_sources_and_replay(self):
        self.send('.deck install child {"source":"Original fixture","entries":[{"text":"铜钥匙","weight":3},"绳索"]}','gm')
        self.send('.deck install parent {"source":"Original parent","entries":[{"ref":"child"}]}','gm')
        revision=read(self.db,'s')['revision']
        with patch('dice_services.secrets.randbelow',side_effect=[0,2]):
            result=execute(self.db,'s','p','.draw parent','weighted',revision)
        self.assertEqual(result['result']['draws'],['铜钥匙'])
        self.assertEqual([p['source'] for p in result['result']['paths'][0]],['Original parent','Original fixture'])
        with patch('dice_services.secrets.randbelow') as rng:
            self.assertEqual(result,execute(self.db,'s','p','.draw parent','weighted',revision))
            rng.assert_not_called()
        with self.assertRaises(ValueError): self.send('.deck remove child','gm')
        self.assertIn('child',read(self.db,'s')['decks'])

    def test_invalid_deck_graphs_fail_before_rng_and_atomic_install(self):
        self.send('.deck install a ["ok"]','gm')
        self.send('.deck install b {"source":"fixture","entries":[{"ref":"a"}]}','gm')
        before=read(self.db,'s')
        with self.assertRaises(ValueError):
            self.send('.deck install a {"source":"fixture","entries":[{"ref":"b"}]}','gm')
        self.assertEqual(before,read(self.db,'s'))
        bad=[{'source':'fixture','entries':[{'text':'x','weight':True}]},
             {'source':'fixture','entries':[{'ref':'missing'}]},
             {'source':'fixture','entries':[{'text':'x','ref':'a'}]},
             {'source':'','entries':['x']}]
        with patch('dice_services.secrets.randbelow') as rng:
            for value in bad:
                with self.assertRaises(ValueError): draw_deck({'a':value},'a',1)
            rng.assert_not_called()
        nested={'d0':['end']}
        for i in range(1,26): nested['d'+str(i)]={'source':'fixture','entries':[{'ref':'d'+str(i-1)}]}
        with self.assertRaises(ValueError): validate_decks(nested)


if __name__ == '__main__': unittest.main()
