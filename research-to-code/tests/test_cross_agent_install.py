"""Portable installation contract tests for Codex, OpenCode and Claude Code.

These tests verify discovery-path layout, byte-identical SKILL.md, isolation
and update behavior. They DO NOT exercise the three proprietary/CLI runtimes.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from install_skill import SKILL_NAME, discover_paths, install, validate_source


class CrossAgentInstallationTests(unittest.TestCase):
    def test_skill_metadata_matches_all_hosts_and_description_length(self):
        validate_source(ROOT)
        frontmatter = (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
        self.assertEqual(frontmatter.count("\nname:"), 1)
        self.assertEqual(frontmatter.count("\ndescription:"), 1)

    def test_project_individual_host_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            expected = {"codex": ".agents", "opencode": ".opencode", "claude": ".claude"}
            for host, top in expected.items():
                paths = discover_paths(target=host, scope="project", project_root=root)
                self.assertEqual(paths[host], root / top / "skills" / SKILL_NAME)

    def test_user_individual_host_paths(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            paths = {host: discover_paths(target=host, scope="user", home=home)[host]
                     for host in ("codex", "opencode", "claude")}
            self.assertEqual(paths["codex"], home / ".agents/skills" / SKILL_NAME)
            self.assertEqual(paths["opencode"], home / ".config/opencode/skills" / SKILL_NAME)
            self.assertEqual(paths["claude"], home / ".claude/skills" / SKILL_NAME)

    def test_install_all_uses_shared_codex_opencode_path_without_duplicate_skill(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = install(target="all", scope="project", project_root=root)
            self.assertEqual(result["installed"], ["codex", "claude"])
            self.assertTrue(result["opencode_also_discovers_codex_path"])
            self.assertFalse((root / ".opencode/skills" / SKILL_NAME).exists())
            for host in ("codex", "claude"):
                path = Path(result["paths"][host])
                self.assertEqual((path / "SKILL.md").read_bytes(), (ROOT / "SKILL.md").read_bytes())
                self.assertTrue((path / "scripts/run_self_tests.py").is_file())
                self.assertTrue((path / "references/math-to-python.md").is_file())
                self.assertTrue((path / "examples/frameworks/framework_ops.py").is_file())

    def test_explicit_opencode_single_install(self):
        with tempfile.TemporaryDirectory() as td:
            result = install(target="opencode", scope="project", project_root=Path(td))
            self.assertEqual(result["installed"], ["opencode"])
            self.assertTrue((Path(td) / ".opencode/skills" / SKILL_NAME / "SKILL.md").is_file())

    def test_safe_repeat_requires_force(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            install(target="codex", scope="project", project_root=root)
            with self.assertRaises(FileExistsError):
                install(target="codex", scope="project", project_root=root)
            replaced = install(target="codex", scope="project", project_root=root, force=True)
            self.assertEqual(replaced["installed"], ["codex"])

    def test_dry_run_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = install(target="all", scope="project", project_root=root, dry_run=True)
            self.assertEqual(out["installed"], [])
            self.assertFalse((root / ".agents").exists())
            self.assertFalse((root / ".claude").exists())

    def test_reject_symlink_destination(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake = root / "elsewhere"
            fake.mkdir()
            dest = root / ".agents/skills" / SKILL_NAME
            dest.parent.mkdir(parents=True)
            try:
                dest.symlink_to(fake, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks not permitted on this OS")
            with self.assertRaises(FileExistsError):
                install(target="codex", scope="project", project_root=root, force=True)
            self.assertTrue(fake.is_dir())

    def test_reject_nested_install_into_own_skill_directory(self):
        with self.assertRaises(ValueError):
            install(target="codex", scope="project", project_root=ROOT, dry_run=False)
        self.assertFalse((ROOT / ".agents").exists())

    def test_cli_installer_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts/install_skill.py"), "--target", "all",
                 "--scope", "project", "--project-root", td, "--dry-run"],
                capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["target"], "all")
            self.assertFalse((Path(td) / ".agents").exists())


if __name__ == "__main__":
    unittest.main()
