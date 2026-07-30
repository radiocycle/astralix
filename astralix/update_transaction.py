import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable


def current_branch(repo_path: str) -> str:
    head = Path(repo_path, ".git", "HEAD").read_text(encoding="utf-8").strip()
    if head.startswith("ref: refs/heads/"):
        return head.removeprefix("ref: refs/heads/")
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or "main"


def transactional_checkout(
    previous: str,
    target: str,
    checkout: Callable[[str], None],
    install: Callable[[], None],
    validate: Callable[[], None],
    rollback: Callable[[], None] | None = None,
) -> None:
    checkout(target)
    try:
        install()
        validate()
    except Exception:
        checkout(previous)
        (rollback or install)()
        raise


def prepare_update_watchdog(
    repo_path: str,
    previous: str,
    timeout: int = 120,
    spawn: bool = True,
    target: str | None = None,
    freeze_path: str | None = None,
) -> dict:
    root = Path(repo_path)
    ready_marker = root / ".astralix-update-ready"
    state_path = root / ".astralix-update.json"
    ready_marker.unlink(missing_ok=True)
    state = {
        "previous": previous,
        "target": target,
        "freeze_path": freeze_path,
        "deadline": time.time() + timeout,
        "ready_marker": str(ready_marker),
    }
    state_path.write_text(json.dumps(state), encoding="utf-8")
    if spawn:
        subprocess.Popen(
            [sys.executable, "-m", "astralix.update_transaction", "watch", str(root)],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    return state


def mark_update_ready(repo_path: str) -> None:
    root = Path(repo_path)
    state_path = root / ".astralix-update.json"
    if not state_path.exists():
        return
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("target"):
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip() != state["target"]:
            return
    Path(state["ready_marker"]).touch()
    state_path.unlink(missing_ok=True)
    if state.get("freeze_path"):
        Path(state["freeze_path"]).unlink(missing_ok=True)


def rollback_pending_update(repo_path: str) -> bool:
    root = Path(repo_path)
    state_path = root / ".astralix-update.json"
    if not state_path.exists():
        return False
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if Path(state["ready_marker"]).exists():
        state_path.unlink(missing_ok=True)
        return False
    if time.time() < state["deadline"]:
        return False
    subprocess.run(["git", "reset", "--hard", state["previous"]], cwd=root, check=True)
    if state.get("freeze_path") and Path(state["freeze_path"]).exists():
        subprocess.run(
            [
                "uv",
                "pip",
                "sync",
                "--python",
                sys.executable,
                state["freeze_path"],
            ],
            cwd=root,
            check=False,
            timeout=600,
            capture_output=True,
        )
        Path(state["freeze_path"]).unlink(missing_ok=True)
    state_path.unlink(missing_ok=True)
    subprocess.run(["systemctl", "restart", "astralix.service"], check=False)
    return True


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "watch":
    while True:
        if rollback_pending_update(sys.argv[2]):
            break
        state_path = Path(sys.argv[2]) / ".astralix-update.json"
        if not state_path.exists():
            break
        time.sleep(5)
