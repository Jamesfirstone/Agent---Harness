from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detector import detect  # noqa: E402


def load_policy():
    with (ROOT / "policy.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_action(path: str) -> dict:
    return {
        "call_id": "path-boundary",
        "session_id": "test-session",
        "actor": "tester",
        "tool": "read_file",
        "args": {"path": path},
    }


class PathBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy()

    def test_similar_prefix_is_not_inside_scope(self) -> None:
        decision = detect(read_action("workspace_evil/notes.txt"), self.policy)
        self.assertEqual("OUT_OF_SCOPE", decision.code)

    def test_backslash_traversal_is_normalized_and_denied(self) -> None:
        decision = detect(read_action(r"workspace\..\secrets.txt"), self.policy)
        self.assertEqual("OUT_OF_SCOPE", decision.code)

    def test_absolute_path_is_denied(self) -> None:
        decision = detect(read_action("/workspace/notes.txt"), self.policy)
        self.assertEqual("OUT_OF_SCOPE", decision.code)

    def test_windows_drive_path_is_denied(self) -> None:
        decision = detect(read_action(r"C:\workspace\notes.txt"), self.policy)
        self.assertEqual("OUT_OF_SCOPE", decision.code)


if __name__ == "__main__":
    unittest.main()
