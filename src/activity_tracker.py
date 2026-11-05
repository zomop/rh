#!/usr/bin/env python3
"""Record genuine project work and commit real changes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "activity"
LOG_FILE = LOG_DIR / "worklog.jsonl"


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result


def ensure_repo() -> None:
    result = run_git("rev-parse", "--is-inside-work-tree", check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise RuntimeError(f"{ROOT} is not inside a Git repository.")


def has_staged_changes() -> bool:
    return run_git("diff", "--cached", "--quiet", check=False).returncode == 1


def commit_changes(message: str, push: bool = False) -> None:
    run_git("add", "activity/worklog.jsonl")
    if not has_staged_changes():
        print("No new changes to commit.")
        return
    run_git("commit", "-m", message)
    print(run_git("log", "-1", "--oneline").stdout.strip())
    if push:
        run_git("push")
        print("Pushed to the configured Git remote.")


def record_work(description: str, category: str, push: bool) -> None:
    clean_description = " ".join(description.split()).strip()
    if len(clean_description) < 12:
        raise ValueError("Description must be at least 12 characters and describe real work.")
    if len(clean_description) > 500:
        raise ValueError("Description must be 500 characters or fewer.")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "category": category,
        "description": clean_description,
        "record_type": "user_reported_work",
    }
    with LOG_FILE.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Recorded genuine work in {LOG_FILE.relative_to(ROOT)}")
    commit_changes(f"docs(activity): record {category} work", push=push)


def watch(interval: int, push: bool) -> None:
    if interval < 5:
        raise ValueError("Watch interval must be at least 5 seconds.")
    print(f"Watching {ROOT} for actual file changes every {interval}s. Press Ctrl+C to stop.")
    try:
        while True:
            if run_git("status", "--porcelain").stdout.strip():
                run_git("add", "-A")
                if has_staged_changes():
                    run_git("commit", "-m", "chore: save actual project changes")
                    print(run_git("log", "-1", "--oneline").stdout.strip())
                    if push:
                        run_git("push")
                        print("Pushed to the configured Git remote.")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nWatcher stopped.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Record genuine project work and commit real changes.")
    sub = parser.add_subparsers(dest="command", required=True)
    log_parser = sub.add_parser("log", help="Record a real task you completed, then commit it.")
    log_parser.add_argument("--description", required=True, help="What you actually completed.")
    log_parser.add_argument("--category", choices=["coding", "documentation", "testing", "research", "design", "maintenance"], default="coding")
    log_parser.add_argument("--push", action="store_true", help="Push the new commit to origin.")
    watch_parser = sub.add_parser("watch", help="Commit actual repository file changes.")
    watch_parser.add_argument("--interval", type=int, default=10)
    watch_parser.add_argument("--push", action="store_true", help="Push each new commit to origin.")
    args = parser.parse_args()
    try:
        ensure_repo()
        if args.command == "log":
            record_work(args.description, args.category, args.push)
        else:
            watch(args.interval, args.push)
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
