import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
init=module('init_project');out=module('export_handoff')

class ToolTests(unittest.TestCase):
    def test_workflow_copy_is_current(self):
        self.assertEqual((ROOT/"WORKFLOW.md").read_text(),(ROOT/"templates/research/WORKFLOW.md").read_text())

    def test_conflict_copies_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'research').mkdir();(p/'research'/'STATUS.md').write_text('keep')
            with self.assertRaises(FileExistsError):init.initialize(p)
            self.assertEqual([x.name for x in (p/'research').iterdir()],['STATUS.md'])
            self.assertEqual((p/'research'/'STATUS.md').read_text(),'keep')
    def test_export_allowlist_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);init.initialize(p);(p/'research'/'private.txt').write_text('UNIQUE_SECRET_TEST')
            target=p/'exports'/'handoff.md';out.export(p,target)
            self.assertNotIn('UNIQUE_SECRET_TEST',target.read_text())
            self.assertIn('SHA256',target.read_text())
            self.assertIn('来源：research/DELIVERY_TEMPLATE.md',target.read_text())
            self.assertIn('来源：research/EXPERIMENT_TEMPLATE.md',target.read_text())
            self.assertIn('来源：research/RESEARCH_REVIEW.md',target.read_text())
            self.assertIn('来源：research/LESSONS.md',target.read_text())
            self.assertIn('来源：research/LITERATURE.md',target.read_text())
            self.assertIn('来源：research/CLAIMS.md',target.read_text())
            self.assertIn('来源：research/RESULTS_SUMMARY.md',target.read_text())
            with self.assertRaises(FileExistsError):out.export(p,target)
            with self.assertRaises(ValueError):out.export(p,p/'research'/'STATUS.md')
    def test_symlink_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);init.initialize(p);f=p/'research'/'STATUS.md';f.unlink();f.symlink_to(p/'research'/'BRIEF.md')
            with self.assertRaises(ValueError):out.export(p,p/'snapshot.md')
    def test_v1_project_can_export_without_optional_records(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);init.initialize(p)
            for name in out.OPTIONAL_FILES:(p/'research'/name).unlink()
            target=p/'snapshot.md';out.export(p,target)
            self.assertNotIn('来源：research/LESSONS.md',target.read_text())

    def test_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):out.export(d,Path(d)/'out.md')

if __name__=='__main__':unittest.main()
