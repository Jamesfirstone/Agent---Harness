# Local verification results

Date: 2026-08-20  
Platform: Windows, PowerShell, bundled Python 3

## `mcp-pep-agent-security`

Command (from `repos/supplement/mcp-pep-agent-security/prototype`):

```powershell
python -m unittest discover -s tests -v
```

Result: 42 tests discovered; 39 passed, 1 failed, 2 errored.

- The initial sandboxed run had six additional permission errors because the prototype creates a local `workspace/`. The command was rerun outside the sandbox to separate sandbox effects from repository behavior.
- Two remaining errors are Windows privilege limitations in tests that call `Path.symlink_to`; the current account lacks `SeCreateSymbolicLinkPrivilege` (`WinError 1314`).
- The remaining failure is a platform assumption in `tests/test_path_normalization.py:200-208`: `/etc/passwd` resolves to `C:/etc/passwd` on Windows, whereas the assertion accepts only `None` or a string beginning with `/`. This does not show a bypass by itself, but it means the audit-field portability claim is not covered by the test on Windows.
- All intent-taint, information-flow label, filesystem-prefix, and non-symlink path-containment cases passed in the elevated rerun.

No dependency installation or source modification was performed.

## `agent-policy-guard`

The documented test suite requires `pytest`. The bundled reproducibility runtime did not contain `pytest` (`No module named pytest`), and dependencies were not installed solely to make a third-party suite run. The repository was therefore assessed through immutable commit, source paths, and bundled test code, not through a claimed passing local run.
