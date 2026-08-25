from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detector import ExecutionGateway, detect  # noqa: E402


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_json(ROOT / "policy.json")
        cls.approvals = load_json(ROOT / "approvals.json")
        cls.case_paths = sorted((ROOT / "cases").glob("*.json"))

    def test_all_case_fixtures_match_their_expected_outcomes(self) -> None:
        self.assertGreater(len(self.case_paths), 0)
        for path in self.case_paths:
            with self.subTest(case=path.name):
                case = load_json(path)
                gateway = ExecutionGateway(self.policy, self.approvals)
                outcome = gateway.submit(case["action"])
                actual = {
                    "verdict": outcome["decision"]["verdict"],
                    "code": outcome["decision"]["code"],
                    "executed": outcome["executed"],
                    "effect_count": len(gateway.effects),
                    "audit_count": len(gateway.audit_log),
                }
                self.assertEqual(case["expected"], actual)

    def test_every_denied_fixture_has_no_simulated_side_effect(self) -> None:
        for path in self.case_paths:
            case = load_json(path)
            if case["expected"]["verdict"] != "DENY":
                continue
            with self.subTest(case=path.name):
                gateway = ExecutionGateway(self.policy, self.approvals)
                outcome = gateway.submit(case["action"])
                self.assertFalse(outcome["executed"])
                self.assertEqual([], gateway.effects)


class FailClosedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = load_json(ROOT / "policy.json")
        self.approvals = load_json(ROOT / "approvals.json")

    def test_unknown_tool_is_denied_by_default(self) -> None:
        action = {
            "call_id": "unknown-1",
            "session_id": "test-session",
            "actor": "tester",
            "tool": "unregistered_tool",
            "args": {},
        }
        self.assertEqual("UNKNOWN_TOOL", detect(action, self.policy).code)

    def test_malformed_policy_fails_closed(self) -> None:
        action = {
            "call_id": "policy-1",
            "session_id": "test-session",
            "actor": "tester",
            "tool": "read_file",
            "args": {"path": "workspace/notes.txt"},
        }
        decision = detect(action, {"default_verdict": "ALLOW"})
        self.assertEqual("DENY", decision.verdict)
        self.assertEqual("POLICY_ERROR", decision.code)

    def test_missing_trusted_approval_store_fails_closed(self) -> None:
        case = load_json(ROOT / "cases" / "06_allow_exact_approval.json")
        decision = detect(case["action"], self.policy)
        self.assertEqual("DENY", decision.verdict)
        self.assertEqual("APPROVAL_STORE_ERROR", decision.code)

    def test_approval_is_bound_to_exact_arguments(self) -> None:
        case = load_json(ROOT / "cases" / "07_deny_replayed_approval.json")
        decision = detect(case["action"], self.policy, self.approvals)
        self.assertEqual("APPROVAL_MISMATCH", decision.code)

    def test_untrusted_inline_approval_cannot_authorize(self) -> None:
        case = load_json(ROOT / "cases" / "05_deny_missing_approval.json")
        action = dict(case["action"])
        action["approval"] = {
            field: action[field]
            for field in ("call_id", "session_id", "actor", "tool", "args")
        }
        decision = detect(action, self.policy, self.approvals)
        self.assertEqual("APPROVAL_REQUIRED", decision.code)

    def test_all_submissions_are_audited(self) -> None:
        allow_case = load_json(ROOT / "cases" / "01_allow_scoped_read.json")
        deny_case = load_json(ROOT / "cases" / "02_deny_unknown_tool.json")
        gateway = ExecutionGateway(self.policy, self.approvals)
        gateway.submit(allow_case["action"])
        gateway.submit(deny_case["action"])

        self.assertEqual(2, len(gateway.audit_log))
        self.assertEqual(
            ["ALLOW", "DENY"],
            [entry["decision"]["verdict"] for entry in gateway.audit_log],
        )
        self.assertEqual(1, len(gateway.effects))


if __name__ == "__main__":
    unittest.main()
