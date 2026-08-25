"""A minimal, deterministic policy gate for single-action compliance tests."""

from __future__ import annotations

import copy
import posixpath
from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class Decision:
    verdict: str
    code: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _deny(code: str, detail: str) -> Decision:
    return Decision("DENY", code, detail)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _path_is_within(path: str, allowed_prefixes: list[str]) -> bool:
    candidate = path.replace("\\", "/")
    if candidate.startswith("/") or ":" in candidate.split("/", 1)[0]:
        return False

    normalized = posixpath.normpath(candidate)
    if normalized == ".." or normalized.startswith("../"):
        return False

    for prefix in allowed_prefixes:
        normalized_prefix = posixpath.normpath(prefix.replace("\\", "/"))
        if normalized == normalized_prefix or normalized.startswith(
            normalized_prefix.rstrip("/") + "/"
        ):
            return True
    return False


def _approval_matches(action: Mapping[str, Any], approval: Any) -> bool:
    if not isinstance(approval, Mapping):
        return False
    bound_fields = ("call_id", "session_id", "actor", "tool", "args")
    return all(approval.get(field) == action.get(field) for field in bound_fields)


def detect(action: Any, policy: Any, trusted_approvals: Any = None) -> Decision:
    """Return a fail-closed decision for one candidate action.

    This detector deliberately handles a short, single-step path. It validates the
    action envelope, tool registry membership, argument schema, resource scope and
    optional approval binding. It does not model temporal or cross-agent state.
    """

    if not isinstance(policy, Mapping):
        return _deny("POLICY_ERROR", "policy must be an object")
    if policy.get("default_verdict") != "DENY":
        return _deny("POLICY_ERROR", "default_verdict must be DENY")

    tools = policy.get("tools")
    if not isinstance(tools, Mapping):
        return _deny("POLICY_ERROR", "policy.tools must be an object")
    if not isinstance(action, Mapping):
        return _deny("INVALID_REQUEST", "action must be an object")

    for field in ("call_id", "session_id", "actor", "tool"):
        if not _is_non_empty_string(action.get(field)):
            return _deny("INVALID_REQUEST", f"{field} must be a non-empty string")

    args = action.get("args")
    if not isinstance(args, Mapping):
        return _deny("INVALID_REQUEST", "args must be an object")

    tool_name = action["tool"]
    tool_policy = tools.get(tool_name)
    if not isinstance(tool_policy, Mapping):
        return _deny("UNKNOWN_TOOL", f"tool is not allowed: {tool_name}")

    required_args = tool_policy.get("required_args", {})
    optional_args = tool_policy.get("optional_args", {})
    if not isinstance(required_args, Mapping) or not isinstance(optional_args, Mapping):
        return _deny("POLICY_ERROR", "tool argument schemas must be objects")

    type_registry = {"string": str, "boolean": bool, "integer": int}
    declared_args = {**required_args, **optional_args}
    missing = sorted(name for name in required_args if name not in args)
    unexpected = sorted(name for name in args if name not in declared_args)
    if missing or unexpected:
        return _deny("INVALID_ARGUMENTS", f"missing={missing}; unexpected={unexpected}")

    for name, type_name in declared_args.items():
        expected_type = type_registry.get(type_name)
        if expected_type is None:
            return _deny("POLICY_ERROR", f"unknown schema type: {type_name}")
        if name in args and type(args[name]) is not expected_type:
            return _deny("INVALID_ARGUMENTS", f"{name} must have type {type_name}")

    allowed_prefixes = tool_policy.get("allowed_path_prefixes", [])
    if not isinstance(allowed_prefixes, list) or not all(
        _is_non_empty_string(prefix) for prefix in allowed_prefixes
    ):
        return _deny("POLICY_ERROR", "allowed_path_prefixes must be strings")
    if "path" in args and not _path_is_within(args["path"], allowed_prefixes):
        return _deny("OUT_OF_SCOPE", f"path is outside the allowed scope: {args['path']}")

    approval_required = tool_policy.get("approval_required", False)
    if type(approval_required) is not bool:
        return _deny("POLICY_ERROR", "approval_required must be boolean")
    if approval_required:
        approval_id = action.get("approval_id")
        if not _is_non_empty_string(approval_id):
            return _deny("APPROVAL_REQUIRED", "this action requires approval")
        if not isinstance(trusted_approvals, Mapping):
            return _deny("APPROVAL_STORE_ERROR", "trusted approval store is unavailable")
        approval = trusted_approvals.get(approval_id)
        if approval is None:
            return _deny("APPROVAL_NOT_FOUND", "approval_id is not in the trusted store")
        if not _approval_matches(action, approval):
            return _deny(
                "APPROVAL_MISMATCH",
                "approval is not bound to this exact call, session, actor, tool and args",
            )

    return Decision("ALLOW", "ALLOWED", "all configured checks passed")


class ExecutionGateway:
    """The only demo path that can append a simulated side effect."""

    def __init__(
        self,
        policy: Mapping[str, Any],
        trusted_approvals: Mapping[str, Any] | None = None,
    ) -> None:
        self._policy = copy.deepcopy(policy)
        self._trusted_approvals = copy.deepcopy(trusted_approvals)
        self.audit_log: list[dict[str, Any]] = []
        self.effects: list[dict[str, Any]] = []

    def submit(self, action: Any) -> dict[str, Any]:
        decision = detect(action, self._policy, self._trusted_approvals)
        action_snapshot = copy.deepcopy(action)
        self.audit_log.append({"action": action_snapshot, "decision": decision.to_dict()})

        executed = decision.verdict == "ALLOW"
        if executed:
            self.effects.append(
                {
                    "call_id": action_snapshot["call_id"],
                    "tool": action_snapshot["tool"],
                    "args": action_snapshot["args"],
                }
            )
        return {"decision": decision.to_dict(), "executed": executed}
