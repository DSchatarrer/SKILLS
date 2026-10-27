"""Offline skill tests: no imports of Flask or SQLAlchemy, no external network/DB."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'examples/backend_async'


def load(name):
    location = ROOT / 'scripts' / name
    spec = importlib.util.spec_from_file_location(name.removesuffix('.py'), location)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

installer = load('install_skill.py')
verify = load('verify_examples.py')
auditor = load('audit_flask.py')


class TestManifest(unittest.TestCase):
    def test_valid_frontmatter(self):
        installer.validate_skill(ROOT)
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertRegex(text, r'(?m)^name: flask-async-backend$')
        self.assertLess(len(text.splitlines()), 500)
        self.assertRegex(text, r'(?m)^description: .{60,1024}$')

    def test_all_internal_links_exist(self):
        for doc in [ROOT / 'SKILL.md', ROOT / 'README.md', ROOT/'examples/README.md', *sorted((ROOT/'references').glob('*.md'))]:
            source = doc.read_text(encoding='utf-8')
            for href in re.findall(r'(?<!!)(?:\]\()([^\s)]+)(?:\))', source):
                if href.startswith(('https://', 'http://', '#')) or href.upper().startswith('C:'):
                    continue
                href = href.split('#')[0]
                if not href or not href.endswith(('.md', '.py', '.txt', '.json', '.example')):
                    continue
                path = (doc.parent / href).resolve()
                self.assertTrue(path.is_relative_to(ROOT) and path.is_file(), f'{doc.relative_to(ROOT)} -> {href}')

    def test_examples_manifest_integrity(self):
        data = json.loads((ROOT/'examples/source-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['files']), 46)
        self.assertEqual(sum(item['skill_path'].startswith('examples/backend_async/') for item in data['files']), 45)
        self.assertEqual(sum(item['skill_path'].endswith('.py') for item in data['files']), 36)
        self.assertTrue(verify.verify()['ok'])

    def test_code_can_parse(self):
        files = [*BACKEND.rglob('*.py'), *ROOT.glob('scripts/*.py'), *ROOT.glob('tests/*.py')]
        self.assertGreaterEqual(len(files), 40)
        for file in files:
            with self.subTest(path=str(file.relative_to(ROOT))):
                ast.parse(file.read_text(encoding='utf-8'), filename=str(file))

    def test_evaluations(self):
        values = json.loads((ROOT/'evals/evals.json').read_text(encoding='utf-8'))['scenarios']
        self.assertGreaterEqual(len(values), 8)
        self.assertGreaterEqual(sum(not x['should_activate'] for x in values), 3)
        self.assertTrue(all(x.get('checks') for x in values))

    def test_async_contracts(self):
        manager = (BACKEND/'src/core/manager_db.py').read_text(encoding='utf-8')
        for item in ('create_async_engine(', 'async_sessionmaker(', 'class_=AsyncSession', 'poolclass=NullPool',
                     'AsyncGenerator[AsyncSession, None]', 'await db.rollback()', '@asynccontextmanager', 'await view_func('):
            self.assertIn(item, manager)
        self.assertIn('WsgiToAsgi', (BACKEND/'src/asgi.py').read_text(encoding='utf-8'))
        self.assertIn('asyncio.run', (BACKEND/'src/core/commands.py').read_text(encoding='utf-8'))
        self.assertIn('await self.db.commit()', (BACKEND/'src/applications/login/controller.py').read_text(encoding='utf-8'))


class TestInstaller(unittest.TestCase):
    def test_shared_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = root/'.agents/skills/flask-async-backend'
            self.assertEqual(list(installer.destinations('both', 'project', root).values()), [expected])
            self.assertEqual(list(installer.destinations('codex', 'user', root).values()), [expected])
            self.assertEqual(list(installer.destinations('opencode', 'user', root).values()), [root/'.config/opencode/skills/flask-async-backend'])

    def test_dry_run_does_not_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = installer.install(target='both', scope='project', root=root, dry_run=True)
            self.assertEqual(report['installed'], [])
            self.assertFalse((root/'.agents').exists())

    def test_install_and_force_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            installer.install(target='both', scope='project', root=root)
            installed = root/'.agents/skills/flask-async-backend'
            self.assertTrue((installed/'SKILL.md').is_file())
            self.assertTrue((installed/'examples/backend_async/src/asgi.py').is_file())
            self.assertTrue(verify.verify(installed)['ok'])
            with self.assertRaises(FileExistsError):
                installer.install(target='both', scope='project', root=root)
            installer.install(target='both', scope='project', root=root, force=True)
            self.assertTrue(verify.verify(installed)['ok'])

    def test_reject_symlink_destination(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as elsewhere:
            root=Path(tmp)
            (root/'.agents/skills').mkdir(parents=True)
            (root/'.agents/skills/flask-async-backend').symlink_to(Path(elsewhere), target_is_directory=True)
            with self.assertRaises(ValueError):
                installer.install(target='both', scope='project', root=root, force=True)


class TestAuditor(unittest.TestCase):
    def test_detect_real_routes(self):
        report = auditor.audit(BACKEND)
        found = {(x['method'],x['path']) for x in report['endpoints']}
        self.assertEqual(found, {('GET','/'),('GET','/health'),('POST','/login/'),('POST','/login/register'),('GET','/users/users')})
        self.assertEqual(report['parse_errors'], [])

    def test_detect_async_and_legacy(self):
        report = auditor.audit(BACKEND)
        self.assertGreaterEqual(report['python_files_parsed'], 20)
        self.assertTrue(any('apikey' in w['finding'].lower() or 'api key' in w['finding'].lower() for w in report['warnings']))

    def test_detect_project_root(self):
        report = auditor.audit(ROOT/'examples')
        self.assertEqual(len(report['endpoints']), 5)


if __name__ == '__main__':
    unittest.main()
