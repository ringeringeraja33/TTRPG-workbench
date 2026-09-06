"""Inspect XLSX source formulas and saved values without executing or saving a workbook."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def audit(path):
    path = Path(path)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    with zipfile.ZipFile(path) as z:
        workbook = ET.fromstring(z.read('xl/workbook.xml'))
        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        links = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets = {r.attrib['Id']: r.attrib['Target'] for r in links}
        out = {'sha256': before, 'calculation': {}, 'sheets': [], 'formula_errors': [],
               'external_links': [n for n in z.namelist() if n.startswith('xl/externalLinks/')],
               'macros': any(n.endswith('vbaProject.bin') for n in z.namelist()),
               'defined_names': [], 'formula_cells': 0, 'missing_formula_cache': 0,
               'notice': 'Saved values may be stale. No formulas or macros executed.'}
        calc = workbook.find('s:calcPr', ns)
        if calc is not None: out['calculation'] = dict(calc.attrib)
        for node in workbook.findall('s:definedNames/s:definedName', ns):
            out['defined_names'].append({'name': node.get('name'), 'expression': node.text})
        for node in workbook.findall('s:sheets/s:sheet', ns):
            rid = node.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            target = targets[rid]
            entry = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            # OOXML relationship paths are POSIX, regardless of host OS.
            import posixpath
            entry = posixpath.normpath(entry)
            sheet = ET.fromstring(z.read(entry))
            row = {'name': node.get('name'), 'visibility': node.get('state', 'visible'),
                   'formulas': [], 'validation_ranges': [], 'protected': sheet.find('s:sheetProtection', ns) is not None}
            for cell in sheet.findall('.//s:sheetData/s:row/s:c', ns):
                formula = cell.find('s:f', ns); value = cell.find('s:v', ns)
                if formula is not None:
                    cached = value.text if value is not None else None
                    row['formulas'].append({'cell': cell.get('r'), 'expression': formula.text,
                                            'attributes': dict(formula.attrib), 'cached': cached})
                    out['formula_cells'] += 1
                    out['missing_formula_cache'] += cached is None
                if cell.get('t') == 'e':
                    out['formula_errors'].append({'sheet': node.get('name'), 'cell': cell.get('r'), 'value': value.text if value is not None else None})
            # Includes extended x14 validations that openpyxl can discard on saving.
            for item in sheet.iter():
                if item.tag.endswith('}dataValidation'):
                    row['validation_ranges'].append({'attributes': dict(item.attrib), 'xml': ET.tostring(item, encoding='unicode')})
            out['sheets'].append(row)
    if hashlib.sha256(path.read_bytes()).hexdigest() != before:
        raise RuntimeError('Source workbook changed during audit')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workbook', type=Path); ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    if a.output.resolve() == a.workbook.resolve(): raise ValueError('Output cannot overwrite workbook')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    value = json.dumps(audit(a.workbook), ensure_ascii=False, indent=2) + '\n'
    a.output.write_text(value, encoding='utf-8')
    assert a.output.read_text(encoding='utf-8') == value
    print('Audit saved; source workbook unchanged.')
