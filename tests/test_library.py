from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/code-flow-map/scripts"))
import library
import render


class LibraryTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.folder = self.home / "code-flow-map"
        home = patch.object(Path, "home", return_value=self.home)
        home.start()
        self.addCleanup(home.stop)

    def run_cli(self, module, *args, stdin=""):
        stdout = io.StringIO()
        with patch.object(sys, "argv", [module.__name__, *args]), patch.object(sys, "stdin", io.StringIO(stdin)):
            with redirect_stdout(stdout):
                module.main()
        return stdout.getvalue()

    def assert_refused(self, module, *args):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as refused:
            self.run_cli(module, *args)
        self.assertEqual(refused.exception.code, 2)

    def test_create_list_and_delete_by_exact_file(self):
        example = ROOT / "examples/task-queue"
        manifest = (example / "flow.json").read_text(encoding="utf-8")
        args = ("--repo", str(example), "--manifest", "-")
        elsewhere = self.home / "other-folder"
        with patch.dict(os.environ, {"CODE_FLOW_MAP_DIR": str(elsewhere)}):
            self.run_cli(render, *args, stdin=manifest)
            self.run_cli(render, *args, stdin=manifest)
            self.assertFalse(elsewhere.exists())

        result = json.loads(self.run_cli(library, "list"))
        self.assertEqual(result["folder"], str(self.folder))
        chosen, other = result["maps"]
        self.assertEqual(chosen["title"], "What happens when a job fails?")
        self.assertEqual(chosen["project"], "Task queue")
        self.assertNotEqual(chosen["name"], other["name"])
        selected = Path(chosen["path"])
        self.assertEqual(selected.parent, self.folder)
        original = selected.read_bytes()
        self.assertIn(b'"focus":"retry"', original)

        self.assert_refused(library, "delete", "--", "../outside.html")
        self.assert_refused(library, "delete", "--", str(selected))
        self.assert_refused(render, *args, "--out", str(self.home / "outside.html"))
        archived = json.loads(self.run_cli(library, "delete", "--", chosen["name"]))
        archived_path = Path(archived["trash_path"])
        self.assertTrue(archived_path.is_relative_to(self.folder / ".trash"))
        self.assertEqual(archived_path.read_bytes(), original)
        self.assertFalse(selected.exists())
        self.assertEqual(json.loads(self.run_cli(library, "list"))["maps"], [other])

    def test_reject_symlinks_for_root_file_and_trash(self):
        outside = self.home / "outside"
        outside.mkdir()
        sentinel = outside / "keep.html"
        sentinel.write_text("keep", encoding="utf-8")
        try:
            self.folder.symlink_to(outside, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("symlinks are unavailable")
        self.assert_refused(library, "list")
        self.assert_refused(library, "delete", "keep.html")
        self.folder.unlink()

        self.folder.mkdir()
        (self.folder / "link.html").symlink_to(sentinel)
        self.assertEqual(json.loads(self.run_cli(library, "list"))["maps"], [])
        self.assert_refused(library, "delete", "link.html")

        local = self.folder / "legacy.html"
        local.write_text("<title>Legacy</title>", encoding="utf-8")
        saved, = json.loads(self.run_cli(library, "list"))["maps"]
        self.assertEqual(saved["title"], "legacy")
        (self.folder / ".trash").symlink_to(outside, target_is_directory=True)
        self.assert_refused(library, "delete", local.name)
        self.assertTrue(local.is_file())
        self.assertEqual(list(outside.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_focus_must_name_a_node(self):
        example = ROOT / "examples/task-queue"
        manifest = json.loads((example / "flow.json").read_text(encoding="utf-8"))
        manifest["focus"] = "missing"
        with self.assertRaisesRegex(ValueError, "Focus must name"):
            render.load_snapshot(manifest, example, None)
        self.assertFalse(self.folder.exists())


if __name__ == "__main__":
    unittest.main()
