import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from dicebot import execute, inspect, percentile


class DicebotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'cards.sqlite'

    def send(self, command, scope='table1', owner='player1'):
        rev = inspect(self.db, scope, owner)['revision']
        return execute(self.db, scope, owner, command, str(rev), rev)['result']

    def test_registration_aliases_updates_and_display(self):
        self.send('.card new ada 阿达'); self.send('.st 力量60智力60侦查50SAN70HP12')
        self.assertEqual(self.send('.st show灵感')['value'], 60)
        self.send('.st 侦查+5 SAN-2')
        self.assertEqual(self.send('.st show侦查')['value'], 55)
        self.assertEqual(self.send('.st show')['stats']['SAN'], 68)
        with self.assertRaises(ValueError): self.send('.sn新名片')

    def test_malformed_batch_rolls_back_all_fields(self):
        self.send('.card new a A'); self.send('.st HP12 INT60')
        before = inspect(self.db, 'table1', 'player1')
        for command in ['.st HP+1 INT-61', '.st INT60灵感70', '.st HP+1垃圾', '.st HP+1 侦查+2']:
            with self.assertRaises(ValueError): self.send(command)
            self.assertEqual(inspect(self.db, 'table1', 'player1'), before)

    def test_scope_owner_switch_and_export_roundtrip(self):
        self.send('.card new a A'); self.send('.st 聆听60SAN70')
        exported = self.send('.st export')['command']
        self.send('.card new b B'); self.send(exported)
        self.assertEqual(self.send('.st show聆听')['value'], 60)
        self.send('.card use a'); self.send('.nn阿达')
        self.assertEqual(self.send('.st show')['name'], '阿达')
        self.assertEqual(inspect(self.db, 'table2', 'player1')['cards'], {})
        self.assertEqual(inspect(self.db, 'table1', 'player2')['cards'], {})

    def test_idempotent_roll_and_stale_rejection(self):
        with patch('dicebot.roll', return_value={'total': 9}) as rng:
            one = execute(self.db, 's', 'p', '.r3d6*5', 'roll1', 0)
            two = execute(self.db, 's', 'p', '.r3d6*5', 'roll1', 0)
            self.assertEqual(one, two); self.assertEqual(one['result']['total'], 45); self.assertEqual(rng.call_count, 1)
            with self.assertRaises(ValueError): execute(self.db, 's', 'p', '.r1d6', 'roll1', 0)
            with self.assertRaises(ValueError): execute(self.db, 's', 'p', '.r1d6', 'roll2', 0)

    def test_bonus_penalty_zero_tens(self):
        with patch('dicebot.secrets.randbelow', side_effect=[0, 0, 1]):
            self.assertEqual(percentile('bonus')['total'], 10)
        with patch('dicebot.secrets.randbelow', side_effect=[0, 0, 1]):
            self.assertEqual(percentile('penalty')['total'], 100)

    def test_check_uses_recorded_value_and_does_not_spend(self):
        self.send('.card new a A'); self.send('.st 侦查60SAN70')
        with patch('dicebot.secrets.randbelow', side_effect=[1, 1, 6]):
            r = self.send('.rap侦查')
        self.assertEqual(r['total'], 61); self.assertEqual(r['outcome'], 'failure')
        self.assertFalse(r['effects_applied'])
        self.assertEqual(self.send('.st show')['stats'], {'侦查': 60, 'SAN': 70})
        with self.assertRaises(ValueError): self.send('.ra图书馆使用')

    def test_hidden_and_unsafe_commands_refused(self):
        self.send('.card new a A')
        for command in ['.rh1d100', '.sc0/1d3', '.st clear', '.log end', '.r__import__(os)', '.st HP12\n.st SAN0']:
            with self.assertRaises(ValueError): self.send(command)

    def test_cold_process_readback(self):
        self.send('.card new ada 阿达'); self.send('.st 灵感60')
        script = Path(__file__).with_name('dicebot.py')
        raw = subprocess.check_output([sys.executable, '-X', 'utf8', str(script), '--db', str(self.db), '--scope', 'table1', '--owner', 'player1'])
        state = json.loads(raw.decode('utf-8'))
        self.assertEqual(state['cards']['ada']['stats']['INT'], 60)


if __name__ == '__main__': unittest.main()
