"""Run the short-chain compliance fixtures through the gated demo executor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from detector import ExecutionGateway


ROOT = Path(__file__).resolve().parent


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_case(
    case_path: Path,
    policy: dict[str, Any],
    trusted_approvals: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    case = load_json(case_path)
    gateway = ExecutionGateway(policy, trusted_approvals)
    outcome = gateway.submit(case["action"])
    actual = {
        "verdict": outcome["decision"]["verdict"],
        "code": outcome["decision"]["code"],
        "executed": outcome["executed"],
        "effect_count": len(gateway.effects),
        "audit_count": len(gateway.audit_log),
    }
    expected = case["expected"]
    passed = all(actual.get(key) == value for key, value in expected.items())
    return passed, {
        "case": case["name"],
        "covers": case["covers"],
        "expected": expected,
        "actual": actual,
        "detail": outcome["decision"]["detail"],
        "passed": passed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect and gate single-action instruction-compliance cases."
    )
    parser.add_argument(
        "--case",
        type=Path,
        help="Run one case JSON file; defaults to every file under cases/.",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=ROOT / "policy.json",
        help="Policy JSON path.",
    )
    parser.add_argument(
        "--approvals",
        type=Path,
        default=ROOT / "approvals.json",
        help="Trusted approval-store JSON path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of the compact text report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy = load_json(args.policy)
    trusted_approvals = load_json(args.approvals)
    case_paths = [args.case] if args.case else sorted((ROOT / "cases").glob("*.json"))
    results = [run_case(path, policy, trusted_approvals) for path in case_paths]
    reports = [report for _, report in results]
    passed = sum(ok for ok, _ in results)

    if args.json:
        print(
            json.dumps(
                {"passed": passed, "total": len(results), "results": reports},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for report in reports:
            mark = "PASS" if report["passed"] else "FAIL"
            actual = report["actual"]
            print(
                f"[{mark}] {report['case']}: "
                f"{actual['verdict']}/{actual['code']} executed={actual['executed']}"
            )
        print(f"summary: {passed}/{len(results)} cases passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
