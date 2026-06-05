---
name: start-task
description: Use when starting a new coding task, issue, bugfix, or feature in this Python repository.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - MultiEdit
---

# Start Task

## Goal
Start work safely and consistently in this repository.

## Steps
1. Read `CLAUDE.md`.
2. Read relevant files from `.claude/rules/`.
3. Read `README.md`, `pyproject.toml`, and affected source files.
4. Summarize the task in 3-6 bullets.
5. Identify risks, assumptions, and unknowns.
6. Propose a minimal implementation plan before editing.
7. Prefer the smallest working change.
8. After edits, run the minimum relevant checks.

## Repository defaults
- Python code lives under `src/`.
- Tests live under `tests/`.
- Use `ruff format`, `ruff check`, `mypy`, and `pytest`.
- Do not edit `.env`.
- Do not add dependencies unless necessary.

## Output style
Return:
- short task summary,
- affected files,
- implementation plan,
- checks to run.
