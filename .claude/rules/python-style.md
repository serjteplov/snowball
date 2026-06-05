# Python Style Rules

## General
- Follow the existing project structure and naming.
- Prefer readable code over compact code.
- Avoid premature abstraction.
- Keep functions focused and short.

## Imports
- Use absolute imports from `package_snowball`.
- Keep imports grouped and sorted.
- Remove unused imports.

## Error handling
- Raise specific exceptions.
- Do not swallow exceptions silently.
- Include useful error messages.

## Logging
- Do not use `print()` for application behavior.
- If logging is needed, use the standard `logging` module.

## Changes
- Avoid unrelated refactors in the same change.
- Preserve backward-compatible behavior unless the task requires otherwise.
