"""Regression coverage for the twelve confirmed repository review defects."""
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET
import dice_local as dl
import campaign_check as cc
import background_chargen as bc
import handout_manifest as hm
import corpus

ROOT = Path(__file__).resolve().parents[1]

class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / 'table.sqlite'
        self.send('.kp')
        self.send('.log on audit')
        self.send('.nn Ada', 'p')

    def send(self, command, actor='gm'):
        revision = dl.read(self.db, 's')['revision']
        return dl.execute(self.db, 's', actor, command, 'op-' + str(revision), revision)

    def cli(self, actor, *args):
        run = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'scripts/dice_local.py'),
            '--db', str(self.db), '--scope', 's', '--actor', actor, *args], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_R01_default_read_and_private_file(self):
        self.send('.st 侦查60', 'p')
        self.send('.table secret 1')
        self.send('.rc 侦查', 'p')
        before = dl.read(self.db, 's')['revision']
        self.assertNotIn('player', self.cli('p'))
        destination = self.root/'private.json'
        self.cli('p', '--private-output', str(destination))
        self.assertTrue(json.loads(destination.read_text(encoding='utf-8'))['player']['check_history'])
        self.assertEqual(before, dl.read(self.db, 's')['revision'])

    def test_R02_log_whitespace_is_private(self):
        self.send('.table secret 1')
        self.send('.r d6', 'p')
        for command in ('.log get audit', '.log\tget audit', '！log   get audit'):
            revision = dl.read(self.db, 's')['revision']
            result = self.cli('p', '--command', command, '--operation', 'cli-'+str(revision), '--expected', str(revision))
            self.assertIn('private_result_saved', result)
            self.assertNotIn('audience', result)
            self.assertNotIn('result', result)

    def test_R03_initiative_retains_audience(self):
        self.send('.table secret 1')
        self.send('.ri +2 SecretNPC')
        self.send('.table secret 0')
        self.assertEqual(self.send('.init', 'p')['result'], [])
        self.assertNotEqual(self.send('.init')['audience'], 'table')
        self.send('.ri +1 PublicNPC', 'p')
        self.assertEqual([r['name'] for r in self.send('.init', 'q')['result']], ['PublicNPC'])

    def test_R04_opposed_redacts_other_players_check(self):
        self.send('.table secret 1')
        self.send('.rcv 60', 'p')
        result = self.send('.rcv 80', 'q')
        self.assertEqual(result['result']['first'], {'hidden': True})
        self.send('.table secret 0')
        self.send('.rcv 60', 'p')
        result = self.send('.rcv 80', 'q')
        self.assertNotIn('hidden', result['result']['first'])

    def test_R05_deck_gate_normalizes_boundaries(self):
        self.send('.deck install weather ["rain"]')
        self.send('.table deck 0')
        before = dl.read(self.db, 's')['revision']
        for command in ('.draw weather', '.draw\tweather', '！draw\nweather'):
            with self.assertRaises(ValueError): self.send(command, 'p')
        self.assertEqual(before, dl.read(self.db, 's')['revision'])

    def test_R06_grown_skill_can_be_checked(self):
        self.send('.st 侦查100', 'p')
        self.send('.mark @p 侦查')
        with patch('vendor.dice_rd.secrets.randbelow', side_effect=[95, 3]):
            self.assertEqual(self.send('.en 侦查', 'p')['result']['after'], 104)
        self.send('.rc 侦查', 'p')
        for value in (0, 999): self.send('.rc '+str(value), 'p')
        with self.assertRaises(ValueError): self.send('.rc 1000', 'p')

    def test_R07_roll_prefixes_survive_clean_export(self):
        for prefix in ('!', '！', '。', '.'):
            self.send(prefix+'r(1+2)*3', 'p')
        target = self.root/'clean.txt'
        dl.export_log(self.db, 's', 'p', 'audit', target, 'clean-txt')
        content = target.read_text(encoding='utf-8')
        for prefix in ('!', '！', '。', '.'):
            self.assertIn(prefix+'r(1+2)*3', content)

    def test_R08_docx_rejects_invalid_xml_before_writing(self):
        valid = self.root/'valid.docx'
        dl.export_log(self.db, 's', 'p', 'audit', valid, 'docx')
        with zipfile.ZipFile(valid) as z: ET.fromstring(z.read('word/document.xml'))
        self.send('message'+chr(1)+'with-control', 'p')
        target = self.root/'invalid.docx'
        with self.assertRaises(ValueError): dl.export_log(self.db, 's', 'p', 'audit', target, 'docx')
        self.assertFalse(target.exists())

    def test_R09_clue_projection_whitelist(self):
        plan = {'clues':[{'id':'a','text':'visible','audience':['p'],'node':'secret','gm_secret':'SECRET'}]}
        self.assertEqual(cc.projection(plan, 'p')['clues'], [{'id':'a','text':'visible'}])
        plan['clues'][0]['audience'] = 'p'
        with self.assertRaises(ValueError): cc.projection(plan, 'p')

    def test_R10_nested_character_projection(self):
        for path in (ROOT/'assets/examples/background-chargen').glob('*/spec.json'):
            spec = json.loads(path.read_text(encoding='utf-8'))
            for card in spec['characters']:
                for key in ('wealth','background','combat'):
                    if key in card: card[key]['gm_secret'] = 'SECRET_MARKER'
            result = bc.player_view(bc.audit(spec))
            self.assertNotIn('SECRET_MARKER', json.dumps(result))
            self.assertTrue(result['cards'])

    def test_R11_handout_types_and_exact_recipient(self):
        item = {'id':'a','audience':'individual','recipients':'alice','released':'false',
            'player_title':'private','player_text':'SECRET','requires':[], 'selected_variant':'safe',
            'variants':{'safe':{'review':'player-safe'}}}
        pack = {'revealed_facts':[], 'handouts':[item]}
        self.assertTrue(hm.validate(pack))
        with self.assertRaises(ValueError): hm.project(pack, 'ali')
        item.update(released=True, recipients=['alice'])
        self.assertFalse(hm.validate(pack))
        self.assertEqual(hm.project(pack, 'ali')['handouts'], [])
        self.assertEqual(len(hm.project(pack, 'alice')['handouts']), 1)
        item['released'] = False
        self.assertEqual(hm.project(pack, 'alice')['handouts'], [])

    def test_R12_extraction_review_binding_and_history(self):
        books = self.root/'books'; books.mkdir()
        cache = self.root/'cache'; cache.mkdir()
        book = books/'source.txt'; book.write_text('same source', encoding='utf-8')
        cached = cache/(corpus.digest(book)[:16]+'.jsonl')
        index = self.root/'index.sqlite'
        def rebuild(text='old text', method='OCR'):
            cached.write_text(json.dumps({'anchor':'text:1','text':text,'method':method})+'\n', encoding='utf-8')
            return corpus.build(books, index, cache_dir=cache)
        def status():
            db = corpus.connect(index)
            try: return corpus.search(db, '', anchor='text:1')[0]['review_state']
            finally: db.close()
        rows = rebuild()
        db = corpus.connect(index)
        try: corpus.review(db, rows[0]['id'], 'text:1', 'passage-verified', 'checked')
        finally: db.close()
        rebuild(); self.assertEqual(status(), 'passage-verified')
        rebuild('new text'); self.assertEqual(status(), 'unreviewed')
        db = corpus.connect(index)
        try:
            self.assertEqual(db.execute('SELECT count(*) FROM review_history').fetchone()[0], 1)
            corpus.review(db, rows[0]['id'], 'text:1', 'passage-verified', 'checked again')
        finally: db.close()
        rebuild('new text', 'different method'); self.assertEqual(status(), 'unreviewed')

    def test_legacy_reviews_are_archived_without_inventing_provenance(self):
        import sqlite3
        index = self.root/'legacy.sqlite'
        db = sqlite3.connect(index)
        db.execute('CREATE TABLE reviews(source_id TEXT,anchor TEXT,state TEXT,note TEXT,PRIMARY KEY(source_id,anchor))')
        db.execute("INSERT INTO reviews VALUES('s','a','passage-verified','legacy evidence')")
        db.commit(); db.close()
        db = corpus.connect(index)
        try:
            self.assertEqual(db.execute('SELECT count(*) FROM reviews').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT note FROM review_history').fetchone()[0], 'legacy evidence')
        finally: db.close()
        db = corpus.connect(index)
        try: self.assertEqual(db.execute('SELECT count(*) FROM review_history').fetchone()[0], 1)
        finally: db.close()

    def test_changed_source_is_unreviewed_before_rebuild(self):
        books = self.root/'books'; books.mkdir()
        book = books/'source.txt'; book.write_text('original passage', encoding='utf-8')
        index = self.root/'index.sqlite'
        rows = corpus.build(books, index)
        db = corpus.connect(index)
        try:
            unit = corpus.search(db, 'original')[0]
            corpus.review(db, rows[0]['id'], unit['anchor'], 'passage-verified', 'checked')
            book.write_text('changed passage', encoding='utf-8')
            result = corpus.search(db, 'original')[0]
            self.assertFalse(result['source_current'])
            self.assertEqual(result['review_state'], 'unreviewed')
            self.assertIsNone(result['note'])
        finally: db.close()

if __name__ == '__main__': unittest.main()
