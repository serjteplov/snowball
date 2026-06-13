# Template: Feature Implementation

## When to use
Implementing a scoped feature or fix in a single verified slice.

## Prompting style note
For complex or multi-step tasks, structure the prompt with labeled sections (e.g., `Context:`, `Task:`, `Constraints:`, `Verification:`) to keep instructions unambiguous.

---

## Variant A: Single-shot prompt
Use this for small, well-understood changes.

```text
Context:
Read @CLAUDE.md and the relevant files first.
Read relevant `.claude/rules/` files (e.g., `python-style.md`, `testing.md`, `typing.md`) before proceeding.

Task:
[one clear task]

Goal:
[what should be true when done]

Scope:
- Change only: [files/modules/areas]
- Do not change: [out-of-scope areas]

Constraints:
- Python 3.13
- Follow existing project patterns
- Keep the diff minimal
- Do not introduce new dependencies unless necessary
- Preserve backward compatibility unless explicitly approved

Specialist hint:
[if applicable: use explorer first, then summarize; or invoke a specific skill]

Approval rule:
[if applicable: stop and ask for approval before X]

Implementation:
- Reuse existing abstractions where possible
- Prefer simple, explicit code over cleverness
- Add or update tests only for behavior affected by this task

Verification:
- Run: `make test`, `make lint`, `make typecheck`, or `make check` for the full gate
- If a check fails, fix the root cause and rerun
- Report the exact files changed and a brief rationale for each

Output:
1. Short summary
2. Plan
3. Changes made
4. Verification results
5. Risks / follow-ups
```

---

## Variant B: Decomposed workflow
Use these blocks one at a time for non-trivial features.

### Frame the task
```text
We are working on a Python 3.13 package in `src/package_snowball`.
Read @CLAUDE.md first.
Read relevant `.claude/rules/` files before proceeding.

I want to implement [feature].
Do not code yet.

First, restate the task, list assumptions, identify ambiguities, and ask only the non-obvious questions that materially affect implementation.
```

### Explore relevant code
```text
Inspect only the files relevant to this feature.
Explain the current flow, relevant abstractions, and where the change should live.
Do not propose code yet.
Stop after this step.
```

### Produce a plan
```text
Propose 2-3 implementation options, recommend one, and produce a step-by-step plan.
List exact files to change and exact tests to add.
Keep the solution minimal.
Stop after this step.
```

### Approve and narrow
```text
Revise the plan with these constraints:
- no new dependencies
- preserve the current public API
- avoid touching unrelated modules
Now produce the final approved plan.
Stop after this step.
```

### Implement one slice
```text
Implement only steps 1 and 2 of the approved plan.
Stop after that.
Run the targeted tests for those changes.
Report changed files and any problems encountered.
```

### Verify
```text
Run the relevant tests, lint checks, and type checks for the files you changed.
If something fails, fix the root cause and rerun.
Show the exact commands and summarize the results.
```

### Self-review
```text
Review the current diff against the approved plan.
Flag only:
- correctness gaps
- scope violations / plan misalignment
- missing edge-case tests
- hidden breaking changes

Ignore cosmetic suggestions unless they improve maintainability materially.
```
