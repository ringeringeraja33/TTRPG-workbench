import copy
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from corpus import build, connect, search, review, digest
from corpus_readers import decode, extract
from handout_manifest import project, validate
from library import classify
from local_rules import jiangshan_parry, jiangshan_death, toc_safe_rest, toc_psychotherapy
from sheet_audit import audit


class CorpusTests(unittest.TestCase):
    def test_unicode_retrieval_hash_change_invalidates_review(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); root = base/'books'; root.mkdir(); book = root/'规则.txt'
            book.write_text('线索：雨夜\u2028第二行', encoding='utf-8')
            index = base/'index.sqlite'; rows = build(root,index); db=connect(index)
            result = search(db,'线索')[0]
            self.assertTrue(result['source_current']); self.assertIn('第二行',result['text'])
            review(db,rows[0]['id'],'text:1','passage-verified','Checked original text')
            book.write_text('新线索',encoding='utf-8')
            self.assertFalse(search(db,'线索')[0]['source_current']); db.close()
            build(root,index); db=connect(index)
            self.assertEqual(search(db,'新线索')[0]['review_state'],'unreviewed'); db.close()

    def test_cached_json_unicode_line_separators_and_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp); root=base/'books';root.mkdir();cache=base/'cache';cache.mkdir()
            a=root/'a.txt';a.write_text('same',encoding='utf-8');(root/'b.txt').write_bytes(a.read_bytes())
            (cache/(digest(a)[:16]+'.jsonl')).write_text(json.dumps({'anchor':'line:1','text':'A\u0085B\u2028C','method':'fixture'},ensure_ascii=False)+'\n',encoding='utf-8')
            rows=build(root,base/'index.sqlite',cache_dir=cache)
            self.assertEqual(len(rows),2);self.assertTrue(all(r['unit_count']==1 for r in rows))
            self.assertNotEqual(rows[0]['id'],rows[1]['id'])

    def test_reader_failure_never_counts_as_read(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'books';root.mkdir();(root/'broken.pdf').write_bytes(b'bad')
            rows=build(root,base/'index.sqlite');self.assertEqual(rows[0]['status'],'error');self.assertEqual(rows[0]['unit_count'],0)

    def test_gb18030_and_chm_scripts_are_data(self):
        text='中文资料';self.assertEqual(decode(text.encode('gb18030'))[0],text)
        self.assertIn('Trail of Cthulhu',classify('TOC克苏鲁迷踪'))
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'book').mkdir();(root/'book'/'a.html').write_text('<h1>规则</h1><script>secret()</script><p>内容</p>',encoding='utf-8')
            u=list(extract(root/'book.chm',chm_root=root))[0]
            self.assertIn('内容',u['text']);self.assertNotIn('secret',u['text'])

    def test_handout_projection_and_hash_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'map.txt').write_text('map',encoding='utf-8')
            h={'id':'map','audience':'individual','recipients':['A'],'released':True,'player_title':'Map','player_text':'Entrance',
               'requires':['arrived'],'selected_variant':'clean','gm_secret':'monster',
               'variants':{'clean':{'path':'map.txt','sha256':digest(root/'map.txt'),'review':'player-safe'},'key':{'path':'map.txt','sha256':digest(root/'map.txt'),'review':'gm-only'}}}
            p={'handouts':[h],'revealed_facts':['arrived']}
            self.assertEqual(len(project(p,'A',root)['handouts']),1)
            self.assertEqual(project(p,'B',root)['handouts'],[])
            self.assertNotIn('monster',json.dumps(project(p,'A',root)))
            h['selected_variant']='key'
            with self.assertRaises(ValueError):project(p,'A',root)
            h['selected_variant']='clean';(root/'map.txt').write_text('changed',encoding='utf-8')
            self.assertTrue(any('hash mismatch' in x for x in validate(p,root)))

    def test_sheet_inspection_preserves_source_and_reports_error(self):
        import openpyxl
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'test.xlsx';b=openpyxl.Workbook();b.active['A1']='=1/0';b.active['B1']='#REF!';b.save(p);b.close()
            before=digest(p);r=audit(p)
            self.assertEqual(before,digest(p));self.assertEqual(r['formula_cells'],1)
            self.assertEqual(r['missing_formula_cache'],1);self.assertEqual(r['formula_errors'][0]['value'],'#REF!')


class LocalMechanicsTests(unittest.TestCase):
    def test_parry_overflow_and_exact_break(self):
        self.assertEqual(jiangshan_parry(10,4,3,7)['hp'],7)
        result=jiangshan_parry(10,4,3,4);self.assertEqual(result['hp'],10);self.assertEqual(result['action_points'],0)

    def test_undefined_death_boundaries_stay_pending(self):
        self.assertEqual(jiangshan_death(-1,10,5)['status'],'pending')
        self.assertEqual(jiangshan_death(-1,11,20)['status'],'pending')
        self.assertEqual(jiangshan_death(-1,10,20)['hp'],5)
        self.assertEqual(jiangshan_death(0,10,1)['status'],'not-triggered')

    def test_safe_rest_is_atomic_and_excludes_investigation(self):
        pools={'run':{'kind':'general','current':1,'rating':8},'history':{'kind':'investigation','current':0,'rating':2}}
        original=copy.deepcopy(pools)
        self.assertEqual(toc_safe_rest(pools,['run'],safe_minutes=59)['pools'],pools)
        self.assertEqual(toc_safe_rest(pools,['run'],safe_minutes=60,interrupted=True)['pools'],pools)
        self.assertEqual(toc_safe_rest(pools,['run'],safe_minutes=60)['pools']['run']['current'],8)
        self.assertEqual(pools,original)
        with self.assertRaises(ValueError):toc_safe_rest(pools,['history'],safe_minutes=60)
        with self.assertRaises(ValueError):toc_safe_rest(pools,['run'],safe_minutes=60,already_used=True)

    def test_psychotherapy_costs_are_separate(self):
        r=toc_psychotherapy(6,2,3,2,1,10);self.assertEqual((r['pool'],r['stability']),(1,7))
        r=toc_psychotherapy(6,1,3,1,1,10);self.assertFalse(r['success']);self.assertEqual(r['pool'],5)
        with self.assertRaises(ValueError):toc_psychotherapy(2,1,2,4,1,10)


if __name__=='__main__':unittest.main()
