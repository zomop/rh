# RH Activity Tracker

This repository contains a small Python tool for recording real work completed in the project and committing genuine repository changes. It never invents tasks, creates fake activity, or creates empty commits.

## Requirements

- Python 3.9 or newer
- Git with a configured identity and remote

## Record completed work

Run from the repository root:

```cmd
python src\activity_tracker.py log --category coding --description "Implemented input validation for the configuration parser"
```

This appends one user-reported entry to `activity/worklog.jsonl` and commits it. Use only an accurate description of work you actually completed. Add `--push` to push that commit to the configured remote.

## Automatically commit real changes

The activity tracker watches the repository and commits detected file changes:

```cmd
python src\activity_tracker.py watch --interval 10
python src\activity_tracker.py watch --interval 10 --push
```

The existing lightweight watcher is also available:

```cmd
python tools\auto_commit.py --once --message "docs: update README"
python tools\auto_commit.py --interval 10 --push
```

Stop a continuous watcher with `Ctrl+C`. No changes means no commit. Review `git status` first so unrelated work is not included.

## Inspect activity and history

```cmd
git status
git log --oneline -5
type activity\worklog.jsonl
```

## Configure Git

Set your Git identity before committing if needed:

```cmd
git config user.name "Your GitHub username"
git config user.email "your-verified-github-email@example.com"
```
