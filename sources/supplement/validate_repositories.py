"""Record immutable commits and checkout quality for selected repositories."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPO_DIR = ROOT / "repos" / "supplement"
SELECTION = Path(__file__).with_name("selected_repositories.json")


def git(path: Path, *args: str) -> tuple[int, str]:
    process = subprocess.run(
        ["git", "-C", str(path), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return process.returncode, process.stdout.strip()


def main() -> None:
    selected = json.loads(SELECTION.read_text(encoding="utf-8"))
    manifest: list[dict[str, object]] = []
    for repository in selected:
        path = REPO_DIR / repository["id"]
        record: dict[str, object] = {
            **repository,
            "path": path.relative_to(ROOT).as_posix(),
            "git_directory": (path / ".git").exists(),
        }
        code, head = git(path, "rev-parse", "HEAD") if record["git_directory"] else (1, "")
        record["commit"] = head if code == 0 else None
        remote_code, remote = git(path, "remote", "get-url", "origin") if code == 0 else (1, "")
        record["resolved_remote"] = remote if remote_code == 0 else None
        status_code, status = git(path, "status", "--short") if code == 0 else (1, "")
        status_lines = [
            line
            for line in status.splitlines()
            if len(line) >= 3 and line[2] == " " and all(char in " MADRCU?!" for char in line[:2])
        ]
        deleted = sum(1 for line in status_lines if "D" in line[:2])
        changed = len(status_lines)
        file_count = sum(1 for item in path.rglob("*") if item.is_file() and ".git" not in item.parts) if path.exists() else 0
        record.update(
            {
                "checkout_state": "complete" if status_code == 0 and changed == 0 else "partial",
                "worktree_changes": changed,
                "deleted_tracked_paths": deleted,
                "worktree_files": file_count,
                "note": (
                    "Windows checkout is partial or case-collided; the Git object database and immutable HEAD are present."
                    if changed
                    else None
                ),
            }
        )
        manifest.append(record)

    output = REPO_DIR / "manifest.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    complete = sum(item["checkout_state"] == "complete" for item in manifest)
    print(json.dumps({"repositories": len(manifest), "complete_checkouts": complete, "partial_checkouts": len(manifest) - complete}, indent=2))
    if any(not item["commit"] for item in manifest):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
