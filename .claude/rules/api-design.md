---
paths:
  - "src/**/*.py"
---

# API Design Rules

## Public surface
- Keep the public API narrow. Export intended names via `__all__`.
- Prefer modules over flat namespaces.

## Interfaces
- Use explicit arguments. Avoid `**kwargs` in public functions.
- Return concrete types; avoid large untyped dictionaries.

## Stability
- Preserve backward-compatible behavior unless asked otherwise.
- Ask before renaming or removing public symbols.
