---
paths:
  - "src/**/*.py"
---

# Typing Rules

## Expectations
- Add type hints to all new or modified functions.
- Add explicit return types for non-trivial functions.
- Prefer concrete types over `Any`.

## When to allow Any
- Only at boundaries where typing is impractical.
- Keep the unsafe area narrow and documented.

## Data structures
- Prefer `TypedDict`, `dataclass`, or small classes for structured data.
- Avoid passing around large untyped dictionaries without need.

## Mypy
- Keep the codebase mypy-clean for changed files.
- If a type ignore is required, keep it narrow and explain why.
