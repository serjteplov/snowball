---
name: implement-feature-slice
description: Implement a scoped feature or fix in a single verified slice.
allowed-tools:
  - Read
  - Bash
  - Edit
  - MultiEdit
---

# Implement Feature Slice

## Trigger
Coding a scoped feature, bugfix, or small refactor.

## Procedure
1. Read affected files and `CLAUDE.md`.
2. Write the smallest change that works.
3. Add or update tests for new behavior.
4. Run `make check`.
5. Propose the next slice or mark as done.

## Output
- Changed files list.
- `make check` results.
- Proposed next slice or completion note.
