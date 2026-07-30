import tempfile
import unittest
import subprocess
from pathlib import Path

from astralix.dependency_manager import build_uv_command, parse_requirements
from astralix.update_transaction import (
    current_branch,
    mark_update_ready,
    prepare_update_watchdog,
    transactional_checkout,
)


class DependencyManagerTests(unittest.TestCase):
    def test_parse_requirements_uses_only_explicit_directive(self):
        source = "import telethontl\n# requires: aiohttp pillow>=10\n"
        self.assertEqual(parse_requirements(source), ["aiohttp", "pillow>=10"])

    def test_parse_requirements_stops_at_end_of_directive_line(self):
        source = "# requires: pillow\nimport io\nfrom PIL import Image\n"
        self.assertEqual(parse_requirements(source), ["pillow"])

    def test_parse_requirements_does_not_guess_from_import(self):
        self.assertEqual(parse_requirements("import telethontl\n"), [])

    def test_build_uv_command_targets_running_python(self):
        self.assertEqual(
            build_uv_command(["aiohttp"], "/venv/bin/python", system=False),
            ["uv", "pip", "install", "--python", "/venv/bin/python", "--upgrade", "aiohttp"],
        )

    def test_build_uv_command_supports_system_python(self):
        self.assertEqual(
            build_uv_command(["aiohttp"], "/usr/bin/python3", system=True),
            [
                "uv",
                "pip",
                "install",
                "--system",
                "--break-system-packages",
                "--upgrade",
                "aiohttp",
            ],
        )


class UpdateTransactionTests(unittest.TestCase):
    def test_current_branch_reads_symbolic_head(self):
        with tempfile.TemporaryDirectory() as root:
            git_dir = Path(root) / ".git"
            git_dir.mkdir()
            (git_dir / "HEAD").write_text("ref: refs/heads/main\n")
            self.assertEqual(current_branch(root), "main")

    def test_transaction_rolls_back_when_validation_fails(self):
        calls = []

        def checkout(ref):
            calls.append(("checkout", ref))

        def install():
            calls.append(("install", None))

        def validate():
            calls.append(("validate", None))
            raise RuntimeError("broken")

        def rollback():
            calls.append(("rollback", None))

        with self.assertRaises(RuntimeError):
            transactional_checkout("old", "new", checkout, install, validate, rollback)

        self.assertEqual(
            calls,
            [
                ("checkout", "new"),
                ("install", None),
                ("validate", None),
                ("checkout", "old"),
                ("rollback", None),
            ],
        )

    def test_watchdog_rolls_back_when_ready_marker_is_missing(self):
        with tempfile.TemporaryDirectory() as root:
            state = prepare_update_watchdog(root, "old", timeout=1, spawn=False)
            self.assertEqual(state["previous"], "old")
            self.assertFalse(Path(state["ready_marker"]).exists())

    def test_ready_marker_clears_pending_watchdog(self):
        with tempfile.TemporaryDirectory() as root:
            state = prepare_update_watchdog(root, "old", timeout=30, spawn=False)
            mark_update_ready(root)
            self.assertTrue(Path(state["ready_marker"]).exists())
            self.assertFalse(Path(root, ".astralix-update.json").exists())

    def test_ready_marker_requires_target_commit(self):
        with tempfile.TemporaryDirectory() as root:
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
            Path(root, "file").write_text("x")
            subprocess.run(["git", "add", "file"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "init"], cwd=root, check=True)
            state = prepare_update_watchdog(
                root, "old", timeout=30, spawn=False, target="wrong"
            )
            mark_update_ready(root)
            self.assertFalse(Path(state["ready_marker"]).exists())
            self.assertTrue(Path(root, ".astralix-update.json").exists())


if __name__ == "__main__":
    unittest.main()
