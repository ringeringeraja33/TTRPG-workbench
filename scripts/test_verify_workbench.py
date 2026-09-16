from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import verify_workbench as verify


class VerificationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.output=Path(self.temp.name)/'results'
    def run_mocked(self,effect):
        with redirect_stdout(io.StringIO()),patch('verify_workbench.subprocess.run',side_effect=effect):
            return verify.run(self.output)
    def test_empty_artifacts_never_report_success(self):
        report=self.run_mocked(lambda *a,**kw:subprocess.CompletedProcess(a,0,'',''))
        self.assertFalse(report['passed']);self.assertEqual(report['archives'],[])
    def test_failures_retained_while_other_checks_continue(self):
        calls=[]
        def execute(*a,**kw):
            calls.append(a);return subprocess.CompletedProcess(a,1 if len(calls)==1 else 0,'out','failure detail')
        report=self.run_mocked(execute)
        self.assertEqual(len(calls),8);self.assertFalse(report['checks'][0]['passed'])
        self.assertEqual((self.output/'tests.stderr.txt').read_text(encoding='utf-8'),'failure detail')
        self.assertFalse(json.loads((self.output/'report.json').read_text(encoding='utf-8'))['passed'])
    def test_timeouts_mark_failure(self):
        def execute(*a,**kw):raise subprocess.TimeoutExpired('fixture',1)
        report=self.run_mocked(execute)
        self.assertTrue(all(x['error']=='TimeoutExpired' for x in report['checks']))
    def test_existing_output_preserved(self):
        self.output.mkdir();file=self.output/'keep';file.write_text('keep',encoding='utf-8')
        with self.assertRaises(FileExistsError):verify.run(self.output)
        self.assertEqual(file.read_text(encoding='utf-8'),'keep')
    def test_repository_output_rejected(self):
        with self.assertRaises(ValueError):verify.run(verify.ROOT/'do-not-create-verification')


if __name__=='__main__':unittest.main()
