import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MARKER = '<!-- handoff: compact-v1 -->'
FULL_SOURCES = [
    'START_HERE.md', 'WORKFLOW.md', 'BRIEF.md', 'PREFERENCES.md', 'STATUS.md',
    'IDEAS.md', 'EVIDENCE.md', 'DECISIONS.md', 'DELIVERIES.md', 'ENVIRONMENT.md',
    'HANDOFF_CHECKLIST.md', 'DELIVERY_TEMPLATE.md', 'EXPERIMENT_TEMPLATE.md',
    'RESEARCH_REVIEW.md', 'LESSONS.md', 'LITERATURE.md', 'CLAIMS.md', 'RESULTS_SUMMARY.md',
]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


init = module('init_project')
out = module('export_handoff')


def snapshot_sources(text):
    prefix = '## 来源：research/'
    return [line[len(prefix):] for line in text.splitlines() if line.startswith(prefix)]


class ToolTests(unittest.TestCase):
    def test_workflow_copy_is_current(self):
        self.assertEqual((ROOT/"WORKFLOW.md").read_text(),(ROOT/"templates/research/WORKFLOW.md").read_text())

    def test_conflict_copies_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'research').mkdir()
            (p / 'research' / 'STATUS.md').write_text('keep')
            with self.assertRaises(FileExistsError):
                init.initialize(p)
            self.assertEqual([x.name for x in (p / 'research').iterdir()], ['STATUS.md'])
            self.assertEqual((p / 'research' / 'STATUS.md').read_text(), 'keep')


class ExportTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.project = Path(directory.name)
        init.initialize(self.project)
        self.research = self.project / 'research'
        self.status = self.research / 'STATUS.md'
        self.status.write_text('# Current status\n' + MARKER + '\n')
        self.target = self.project / 'exports' / 'handoff.md'
        (self.research / 'private.txt').write_text('UNIQUE_SECRET_TEST')

    def test_compact_includes_whole_files_and_their_hashes(self):
        for name in ['STATUS.md', 'PREFERENCES.md']:
            with (self.research / name).open('a') as stream:
                stream.write('完整的上下文\n' * 1500 + '结尾 ' + name)
        out.export(self.project, self.target)
        snapshot = self.target.read_text()
        self.assertEqual(snapshot_sources(snapshot), ['STATUS.md', 'PREFERENCES.md'])
        self.assertNotIn('UNIQUE_SECRET_TEST', snapshot)
        for name in ['STATUS.md', 'PREFERENCES.md']:
            source = self.research / name
            self.assertIn(source.read_text(), snapshot)
            self.assertIn('SHA256：' + hashlib.sha256(source.read_bytes()).hexdigest(), snapshot)

    def test_legacy_default_exports_original_allowlist(self):
        self.status.write_text('# A legacy project\n')
        out.export(self.project, self.target)
        snapshot = self.target.read_text()
        self.assertEqual(snapshot_sources(snapshot), FULL_SOURCES)
        self.assertNotIn('UNIQUE_SECRET_TEST', snapshot)

    def test_cli_default_and_explicit_full(self):
        for filename, flags, expected in [
            ('default.md', [], ['STATUS.md', 'PREFERENCES.md']),
            ('full.md', ['--full'], FULL_SOURCES),
        ]:
            with self.subTest(filename=filename):
                target = self.project / filename
                subprocess.run([
                    sys.executable, str(ROOT / 'tools' / 'export_handoff.py'),
                    '--project', str(self.project), '--output', str(target), *flags,
                ], check=True, capture_output=True, text=True)
                self.assertEqual(snapshot_sources(target.read_text()), expected)
                self.assertNotIn('UNIQUE_SECRET_TEST', target.read_text())

    def test_no_overwrite(self):
        out.export(self.project, self.target)
        for full in [False, True]:
            with self.subTest(full=full):
                with self.assertRaises(FileExistsError):
                    out.export(self.project, self.target, full=full)
                with self.assertRaises(ValueError):
                    out.export(self.project, self.status, full=full)
                with self.assertRaises(ValueError):
                    out.export(self.project, self.research / 'new.md', full=full)
        link = self.project / 'linked-target'
        link.symlink_to(self.project / 'missing.md')
        with self.assertRaises(ValueError):
            out.export(self.project, link)
        self.assertFalse(link.exists())

    def test_symlink_source_rejected(self):
        for name in ['PREFERENCES.md', 'STATUS.md']:
            path = self.research / name
            original = path.read_bytes()
            path.unlink()
            path.symlink_to(self.research / 'BRIEF.md')
            with self.subTest(name=name), self.assertRaises(ValueError):
                out.export(self.project, self.target)
            self.assertFalse(self.target.exists())
            path.unlink()
            path.write_bytes(original)

    def test_full_rejects_dangling_optional_symlink(self):
        record = self.research / 'LESSONS.md'
        record.unlink()
        record.symlink_to(self.project / 'missing.md')
        with self.assertRaises(ValueError):
            out.export(self.project, self.target, full=True)
        self.assertFalse(self.target.exists())

    def test_v1_project_can_export_without_optional_records(self):
        self.status.write_text('# A legacy project\n')
        for name in out.OPTIONAL_FILES:
            (self.research / name).unlink()
        for full in [False, True]:
            target = self.project / f'v1-{full}.md'
            out.export(self.project, target, full=full)
            self.assertEqual(snapshot_sources(target.read_text()), list(out.FILES))

    def test_missing_file_rejected(self):
        (self.research / 'PREFERENCES.md').unlink()
        with self.assertRaises(ValueError):
            out.export(self.project, self.target)
        self.status.unlink()
        with self.assertRaises(ValueError):
            out.export(self.project, self.target)
        self.assertFalse(self.target.exists())

    def test_unavailable_git_status(self):
        for mode in ['outside-repository', 'missing-git']:
            target = self.project / (mode + '.md')
            with self.subTest(mode=mode):
                if mode == 'missing-git':
                    with patch.object(out.subprocess, 'run', side_effect=FileNotFoundError):
                        out.export(self.project, target)
                else:
                    out.export(self.project, target)
                text = target.read_text()
                self.assertIn('代码 HEAD：unavailable', text)
                self.assertIn('Git 工作区有改动：unavailable', text)


if __name__ == '__main__':
    unittest.main()
