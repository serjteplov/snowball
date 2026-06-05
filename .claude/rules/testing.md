---
paths:
  - "tests/**/*.py"
  - "src/**/*.py"
---

# Testing Rules

## Principles
- Every behavior change should have a test or a clear reason why not.
- Prefer fast deterministic unit tests.
- One test should validate one behavior focus.

## Test style
- Use `pytest`.
- Name tests clearly with expected behavior in mind.
- Arrange data explicitly inside the test.

## Scope
- Test public behavior first.
- Avoid over-mocking when simple real objects are enough.
- Do not add flaky time- or network-dependent tests.

## Minimum check
For changed Python code, run:
```bash
make test
```
