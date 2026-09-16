import json
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
import campaign_archive as archive
import session
import test_actions


class ArchiveTests(unittest.TestCase):
    setUp=test_actions.ActionTests.setUp
    revision=test_actions.ActionTests.revision
    event=test_actions.ActionTests.event
    send=test_actions.ActionTests.send
    declaration=test_actions.ActionTests.declaration

    def mutate(self,sql,args=()):
        with closing(sqlite3.connect(self.path)) as db:
            with db:db.execute(sql,args)
    def test_check_is_read_only_and_private(self):
        before=self.path.read_bytes();result=archive.check(self.path)
        self.assertEqual(self.path.read_bytes(),before);self.assertTrue(result['ok'])
        self.assertNotIn('positions',json.dumps(result))
    def test_backup_roundtrip_pending_action_without_reroll(self):
        self.send('declare',self.declaration());self.send('roll',{})
        target=self.root/'backup.sqlite';result=archive.backup(self.path,target)
        self.assertEqual(session.view(self.path,gm=True),session.view(target,gm=True))
        self.assertTrue(archive.check(target,result['file_sha256'])['ok'])
        self.send('settle',{'outcome':'success','effects':[]})
        self.assertEqual(session.view(target,gm=True)['revision'],2)
    def test_existing_destination_never_overwritten(self):
        target=self.root/'existing';target.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):archive.backup(self.path,target)
        self.assertEqual(target.read_bytes(),b'preserve')
    def test_source_destination_same_rejected(self):
        before=self.path.read_bytes()
        with self.assertRaises(ValueError):archive.backup(self.path,self.path)
        self.assertEqual(self.path.read_bytes(),before)
    def test_wal_commits_included_in_backup(self):
        db=sqlite3.connect(self.path)
        try:
            db.execute('PRAGMA journal_mode=WAL')
            self.send('declare',self.declaration())
            result=archive.backup(self.path,self.root/'wal-copy.sqlite')
            self.assertEqual(result['revision'],1)
            self.assertEqual(session.view(self.root/'wal-copy.sqlite',gm=True),session.view(self.path,gm=True))
        finally:db.close()
    def test_revision_gap_detected(self):
        self.send('declare',self.declaration());self.send('roll',{})
        self.mutate('DELETE FROM events WHERE revision=1')
        with self.assertRaises(ValueError):archive.check(self.path)
    def test_request_hash_corruption_detected(self):
        self.send('declare',self.declaration());self.mutate("UPDATE events SET request_hash='bad' WHERE revision=1")
        with self.assertRaises(ValueError):archive.check(self.path)
    def test_invalid_snapshot_detected(self):
        self.send('declare',self.declaration());state=session.view(self.path,gm=True)['state'];state['clock']=-1
        self.mutate('UPDATE events SET state=? WHERE revision=1',(session.encode(state),))
        with self.assertRaises(ValueError):archive.check(self.path)
    def test_restore_equality_checked(self):
        self.send('declare',self.declaration())
        session.apply(self.path,self.event('',{},changes=[{'kind':'restore','revision':0}]))
        self.assertTrue(archive.check(self.path)['ok'])
        state=session.view(self.path,gm=True)['state'];state['clock']=1
        self.mutate('UPDATE events SET state=? WHERE revision=2',(session.encode(state),))
        with self.assertRaises(ValueError):archive.check(self.path)
    def test_bad_backup_is_removed_source_preserved(self):
        self.mutate("UPDATE events SET request_hash='bad' WHERE revision=0")
        before=self.path.read_bytes();target=self.root/'bad-copy.sqlite'
        with self.assertRaises(ValueError):archive.backup(self.path,target)
        self.assertFalse(target.exists());self.assertEqual(self.path.read_bytes(),before)
    def test_external_checksum_detects_valid_schema_edit(self):
        target=self.root/'copy.sqlite';result=archive.backup(self.path,target)
        with target.open('ab') as file:file.write(b'changed file')
        with self.assertRaises(ValueError):archive.check(target,result['file_sha256'])
    def test_missing_file_not_created(self):
        missing=self.root/'missing.sqlite'
        with self.assertRaises(ValueError):archive.check(missing)
        self.assertFalse(missing.exists())
    def test_cli_cold_recovery_and_private_output(self):
        self.send('declare',self.declaration());target=self.root/'cold.sqlite'
        run=subprocess.run([sys.executable,'-X','utf8',str(Path(archive.__file__)),str(self.path),'backup','--output',str(target)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr);self.assertNotIn('GM_SECRET',run.stdout)
        result=json.loads(run.stdout)
        run=subprocess.run([sys.executable,'-X','utf8',str(Path(archive.__file__)),str(target),'check','--expected-sha256',result['file_sha256']],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)


if __name__=='__main__':unittest.main()
