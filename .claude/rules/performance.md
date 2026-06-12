---
paths:
  - "src/**/*.py"
---

# Performance Guidelines

## General
- Do not optimize without profiling or a clear performance requirement.
- Keep code readable first.

## I/O and loops
- Be conscious of big-O for loops over large inputs.
- Batch I/O operations when possible.

## Anti-patterns
- No sleep/busy-waiting loops for synchronization.
- Do not load large files entirely into memory if streaming is possible.
