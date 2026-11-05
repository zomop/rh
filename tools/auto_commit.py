#!/usr/bin/env python3
"""Commit real repository changes; never generates synthetic activity."""
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check
    )

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Watch this Git repository and commit actual file changes."
    )
    parser.add_argument("--interval", type=int, default=10,
                        help="Seconds between checks (default: 10)")
    parser.add_argument("--once", action="store_true",
                        help="Check once, then exit")
    parser.add_argument("--message", default="chore: save project changes",
                        help="Commit message")
    args = parser.parse_args()

    if args.interval < 1:
        parser.error("--interval must be at least 1 second")

    if git("rev-parse", "--is-inside-work-tree").stdout.strip() != "true":
        print("ERROR: This folder is not inside a Git repository.")
        return 1

    print(f"Watching {ROOT} for real file changes. Press Ctrl+C to stop.")
    while True:
        # Stage tracked modifications/deletions and untracked files.
        git("add", "-A")
        status = git("status", "--porcelain").stdout.strip()

        if status:
            # Do not commit ignored files or empty changes.
            result = git("diff", "--cached", "--quiet", check=False)
            if result.returncode == 1:
                git("commit", "-m", args.message)
                commit_hash = git("rev-parse", "--short", "HEAD").stdout.strip()
                subject = git("log", "-1", "--pretty=%s").stdout.strip()
                print(f"Committed {commit_hash}: {subject}")
            elif result.returncode not in (0,):
                print("Could not inspect staged changes:", result.stderr.strip())
        else:
            print("No real changes detected; nothing to commit.")

        if args.once:
            return 0
        time.sleep(args.interval)

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nStopped.")
