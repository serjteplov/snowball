# CLAUDE.md

## Project overview
This repository contains a Python project using:
- `src/` layout
- `pytest` for tests
- `ruff` for formatting and linting
- `mypy` for static typing
- `pre-commit` for local quality gates

Main package:
- `src/package_snowball`

## Working conventions
- Prefer small, focused changes.
- Read relevant rules in `.claude/rules/` before editing.
- Keep implementation simple and explicit.
- Ask before introducing new dependencies or changing project structure.
- Do not modify `.env`.
- Never commit secrets.

## Commands
Use these commands from the repository root:

```bash
make format
make lint
make typecheck
make test
make check
```

## Code style
- Use Python 3.13 syntax.
- Add type hints to new or changed functions.
- Prefer clear names over clever code.
- Keep functions small and single-purpose.
- Prefer standard library unless an external package is justified.

## Testing
- Add or update tests for behavior changes.
- Keep tests deterministic and fast.
- Put tests in `tests/`.
- Start with unit tests before broader integration coverage.

## Repository map
- `src/package_snowball/` — application/package code
- `tests/` — test suite
- `.claude/rules/` — modular repository rules
- `.claude/skills/` — reusable workflows
- `docs/adr/` — architecture decisions
- `PROGRESS.md` — project progress notes

## Rule loading
Check these files when relevant:
- `.claude/rules/python-style.md`
- `.claude/rules/testing.md`
- `.claude/rules/typing.md`
- `.claude/rules/git-workflow.md`

## Behavior expectations
When working on a task:
1. Understand the goal first.
2. Propose a short plan for non-trivial changes.
3. Make the smallest correct change.
4. Run relevant checks.
5. Summarize what changed and any remaining risks.
