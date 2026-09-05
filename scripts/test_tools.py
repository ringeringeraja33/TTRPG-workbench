"""Meaningful mathematical, rejection, and local-reader regression checks."""
import tempfile, unittest, zipfile
from pathlib import Path
from dice import distribution, probability, roll
from library import units, classify

class ToolTests(unittest.TestCase):
    def test_dice_distribution(self):
        d=distribution('2d6'); self.assertEqual(sum(d.values()),36); self.assertEqual(d[7],6)
        f=distribution('4dF'); self.assertEqual(sum(f.values()),81); self.assertEqual(f[0],19); self.assertEqual(f[-4],1)
    def test_advantage(self):
        self.assertEqual(probability('1d20',11)['probability'],.5)
        self.assertEqual(probability('1d20',11,'advantage')['probability'],.75)
        self.assertEqual(probability('1d20',11,'disadvantage')['probability'],.25)
    def test_shared_units(self):
        self.assertEqual(probability('1d100',51,'coc-bonus')['probability'],.759)
        self.assertEqual(probability('1d100',51,'coc-penalty')['probability'],.261)
        self.assertEqual(probability('1d100',100,'coc-bonus')['probability'],1)
    def test_reject_bad_or_large(self):
        for text in ('__import__("os")','0d6','1000d1000','-1d6'):
            with self.assertRaises(ValueError): roll(text)
        with self.assertRaises(ValueError): probability('2d20',10,'advantage')
    def test_real_roll(self):
        r=roll('4d6+2'); self.assertEqual(len(r['raw']),4); self.assertTrue(all(1<=x<=6 for x in r['raw'])); self.assertEqual(sum(r['raw'])+2,r['total'])
    def test_utf8_and_xml(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'例子.txt'; p.write_text('调查\n线索',encoding='utf-8'); u=list(units(p)); self.assertEqual(u[1]['text'],'线索'); self.assertEqual(u[1]['anchor'],'line:2')
            p=Path(d)/'例子.docx'
            with zipfile.ZipFile(p,'w') as z: z.writestr('word/document.xml','<w:document xmlns:w="urn:test"><w:p><w:r><w:t>线索</w:t></w:r></w:p></w:document>'.encode('utf-8'))
            self.assertEqual(list(units(p))[0]['text'],'线索')
    def test_ambiguous_name(self):
        self.assertIn('not Evil Hat',classify('Fate GugDove 规则书.pdf'))
        self.assertIn('not game edition',classify('Pathfinder v2.01.chm'))
    def test_sparse_spreadsheet(self):
        import openpyxl
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'card.xlsx'; b=openpyxl.Workbook(); b.active['C3']='调查'; b.save(p); b.close()
            rows=list(units(p)); self.assertEqual(rows[0]['anchor'],'sheet:Sheet:row:3'); self.assertEqual(rows[0]['text'],'C3=调查')
if __name__=='__main__': unittest.main()
