from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import actions
import dice_local
import dice_archive as archive
import dicebot


class DiceArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.path=self.root/'dice.sqlite'
        self.response=dice_local.execute(self.path,'table','pc1','.r 1d6','roll',0)
    def mutate(self,sql,args=()):
        with closing(sqlite3.connect(self.path)) as db:
            with db:db.execute(sql,args)
    def test_roundtrip_and_retry_without_reroll(self):
        target=self.root/'copy.sqlite';result=archive.backup(self.path,target)
        self.assertTrue(archive.check(target,result['file_sha256'])['ok'])
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=AssertionError('reroll')):
            self.assertEqual(dice_local.execute(target,'table','pc1','.r 1d6','roll',0),self.response)
    def test_receipt_bridge_reads_recovered_dice(self):
        target=self.root/'copy.sqlite';archive.backup(self.path,target)
        spec={'mode':'receipt','expression':'1d6','source':{'database':str(target.resolve()),'scope':'table','actor':'pc1','operation':'roll'}}
        with patch('vendor.dice_rd.secrets.randbelow',side_effect=AssertionError('reroll')):
            receipt=actions.imported_receipt(spec)
        self.assertEqual(receipt['roll'],self.response['result'])
    def test_cards_and_logs_survive_copy(self):
        for revision,command in enumerate(('.kp','.nn Investigator','.st STR50 HP10','.log on Session','A private local note'),start=1):
            dice_local.execute(self.path,'table','pc1',command,f'op-{revision}',revision)
        target=self.root/'cards.sqlite';archive.backup(self.path,target)
        self.assertEqual(dice_local.read(self.path,'table'),dice_local.read(target,'table'))
        self.assertTrue(dice_local.read(target,'table')['players']['pc1']['cards'])
        self.assertTrue(dice_local.read(target,'table')['logs']['Session'])
    def test_multiple_scopes(self):
        dice_local.execute(self.path,'other','other-pc','.r 1d6','roll',0)
        self.assertEqual(archive.check(self.path)['tables'],2)
    def test_readonly_and_private(self):
        before=self.path.read_bytes();report=archive.check(self.path)
        self.assertEqual(self.path.read_bytes(),before);self.assertNotIn('pc1',json.dumps(report))
    def test_missing_receipt_rejected(self):
        self.mutate('DELETE FROM requests')
        with self.assertRaises(ValueError):archive.check(self.path)
    def test_identity_mismatch_rejected(self):
        response=dict(self.response,operation='wrong')
        self.mutate('UPDATE requests SET response=?',(json.dumps(response),))
        with self.assertRaises(ValueError):archive.check(self.path)
    def test_invalid_active_card_rejected(self):
        state=dice_local.read(self.path,'table');state['players']['pc1']={'active':'missing','cards':{}}
        self.mutate('UPDATE tables SET state=?',(json.dumps(state),))
        with self.assertRaises(ValueError):archive.check(self.path)
    def test_corrupt_copy_cleaned_up(self):
        self.mutate('DELETE FROM requests');target=self.root/'bad.sqlite'
        with self.assertRaises(ValueError):archive.backup(self.path,target)
        self.assertFalse(target.exists())
    def test_existing_copy_preserved(self):
        target=self.root/'copy.sqlite';target.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):archive.backup(self.path,target)
        self.assertEqual(target.read_bytes(),b'keep')
    def test_legacy_dialect_rejected(self):
        legacy=self.root/'legacy.sqlite';db=dicebot.connect(legacy);db.close()
        with self.assertRaises(ValueError):archive.check(legacy)
    def test_wal_copy_keeps_receipt(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute('PRAGMA journal_mode=WAL')
            dice_local.execute(self.path,'table','pc1','.r 1d6','second',1)
            target=self.root/'wal.sqlite';result=archive.backup(self.path,target)
        self.assertEqual(result['operations'],2)
    def test_file_checksum_changed(self):
        target=self.root/'copy.sqlite';result=archive.backup(self.path,target)
        with target.open('ab') as stream:stream.write(b'extra')
        with self.assertRaises(ValueError):archive.check(target,result['file_sha256'])


if __name__=='__main__':unittest.main()
