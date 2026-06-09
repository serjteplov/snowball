# English Prompt Handbook for LLM-Assisted Python Development

This handbook is a practical guide for working with Claude or another coding-focused LLM in English while building a Python application. It focuses on clear task framing, prompt structure, review loops, and a professional development workflow that keeps changes scoped, testable, and easy to review.[cite:181][cite:13][cite:174]

## Core Principles

Strong coding prompts define four things clearly: the task, the scope, the constraints, and the verification method. Anthropic’s guidance for Claude Code repeatedly emphasizes planning before editing, providing concrete context such as files and commands, and giving the model a way to verify whether the result actually works.[cite:181][cite:13]

Good prompts are operational rather than abstract. Instead of asking the model to “make it better,” ask it to inspect specific files, explain the current behavior, propose options, implement one bounded step, and run exact checks such as tests or lint commands.[cite:174][cite:181]

## Prompt Structure

A dependable prompt usually contains these blocks:

1. **Context** — what project this is, which files matter, and which rules to read first.[cite:13][cite:181]
2. **Task** — one concrete objective, stated in one or two sentences.[cite:174]
3. **Scope** — what may change and what must not change.[cite:181]
4. **Constraints** — Python version, dependency policy, API stability, style expectations, and performance or architectural limits.[cite:181][cite:174]
5. **Verification** — exact commands to run and the expectation to fix failures before reporting back.[cite:13][cite:181]
6. **Output format** — how the answer should be structured, such as plan, changed files, test results, and risks.[cite:174]

A simple default template:

```text
Read @CLAUDE.md and the relevant files first.

Task:
[one clear task]

Goal / expected outcome:
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

Implementation requirements:
- Reuse existing abstractions where possible
- Prefer simple, explicit code over cleverness
- Add or update tests only for behavior affected by this task

Verification:
- Run: [exact commands]
- If a check fails, fix the root cause and rerun
- Report the exact files changed and a brief rationale for each

Output format:
1. Short summary
2. Plan
3. Changes made
4. Verification results
5. Risks / follow-ups
```

## Best-Practice Prompts

### 1. Codebase Discovery

Use this before touching unfamiliar code. It keeps the model in analysis mode and prevents premature edits.[cite:13][cite:181]

```text
Read @CLAUDE.md and @src/myapp/auth.

Do not modify anything.

I need to understand how authentication works in this project.
Please:
1. Identify the main files and entry points.
2. Trace the login flow end to end.
3. Explain which abstractions are core vs incidental.
4. List likely extension points for adding OAuth later.

Keep the answer concise and concrete, with file references.
```

### 2. Plan Before Coding

Use this when the feature is non-trivial and you want options before implementation. This matches Claude Code’s documented plan-first workflow.[cite:13][cite:181]

```text
Read @CLAUDE.md, @src/myapp/config, and @tests.

Do not modify files yet.
I want to add environment-based config loading with validation.

Please:
1. Inspect the current config flow.
2. Propose 2 implementation options.
3. Recommend one option with trade-offs.
4. Produce a step-by-step plan.
5. List the exact files likely to change.
6. List the tests we should add.

Assume Python 3.13 and keep the design simple.
```

### 3. Focused Implementation

Use this for a single approved feature slice. It works best when the model already understands the area.[cite:13][cite:181]

```text
Read @CLAUDE.md, @src/myapp/config.py, and @tests/test_config.py.

Implement the approved config-loading plan.

Requirements:
- Load settings from environment variables.
- Validate required values at startup.
- Raise clear errors for missing or invalid values.
- Keep the public API stable.

Constraints:
- Minimal diff
- No new dependencies
- Follow existing code style

Verification:
- Run `pytest -q tests/test_config.py`
- Run `ruff check .`
- If checks fail, fix and rerun

At the end, report:
- files changed
- what changed in each file
- any remaining risks
```

### 4. Bug Fixing

Good bug-fix prompts describe the observable symptom, not only the desired patch. They also ask for a root-cause fix and targeted verification.[cite:181][cite:13]

```text
Read @CLAUDE.md and the files involved in the CLI startup path.

Bug:
Running the app with a missing config file crashes with an unhelpful traceback.

Please:
1. Reproduce the issue.
2. Find the root cause.
3. Write a failing test first if practical.
4. Fix the bug without suppressing the error incorrectly.
5. Make the user-facing error message clear and actionable.
6. Run the relevant tests and lint checks.

Do not refactor unrelated code.
```

### 5. Safe Refactoring

Use this when behavior must stay stable. The prompt explicitly limits architectural drift.[cite:181][cite:174]

```text
Read @CLAUDE.md and @src/myapp/parser.py.

Refactor this module to improve readability and separation of concerns.

Constraints:
- Preserve behavior exactly
- No API changes
- No dependency changes
- Keep changes incremental and minimal

Please:
1. Explain what is hard to maintain today.
2. Suggest a small refactor plan.
3. Implement it in the safest order.
4. Add or update tests only if needed to lock current behavior.
5. Run targeted verification and summarize behavior preservation.
```

### 6. Test Writing

Use this when implementation exists but coverage is weak. Anthropic’s workflow guidance favors meaningful verification over superficial code generation.[cite:13][cite:181]

```text
Read @CLAUDE.md, @src/myapp/validator.py, and the surrounding test files.

Add tests for validator behavior.

Focus on:
- invalid input
- boundary values
- empty values
- error message quality

Constraints:
- Match existing test style
- Prefer straightforward tests over heavy parametrization unless it improves clarity

Verification:
- Run only the relevant test module first
- Then report uncovered edge cases you still see
```

### 7. Self-Review

This is one of the highest-leverage prompts after coding. It turns the model from producer into critic.[cite:181]

```text
Review your own diff as a strict senior engineer.

Check for:
- unnecessary changes
- overengineering
- hidden breaking changes
- weak naming
- incomplete tests
- unclear error handling
- deviations from the stated task

Report only issues that affect correctness, maintainability, or scope.
Ignore cosmetic style preferences unless they materially improve the result.
```

### 8. Spec Interview

Use this before the first implementation pass on a greenfield project or large feature. Anthropic explicitly recommends spec-first workflows for ambiguous tasks.[cite:181][cite:13]

```text
I want to build a Python CLI app for [brief description].

Interview me in detail before implementation.
Ask about:
- use cases
- inputs and outputs
- failure modes
- CLI UX
- configuration
- logging
- testing strategy
- packaging
- edge cases
- non-goals

Keep asking until the spec is complete.
Then write a concise implementation spec to SPEC.md.
Do not start coding yet.
```

## Bad Prompt Patterns

### Vague Request

```text
Build me a Python app for note taking.
```

Why it is bad: there is no scope, no storage model, no interface definition, no limits, and no verification path. The model has to invent too much at once.[cite:174][cite:181]

Better version:

```text
Build a Python 3.13 CLI note-taking app.
Store notes in local markdown files under ./notes.
Support commands: add, list, show, delete.
Do not build a TUI or web UI.
Use only the standard library.
Add tests for command parsing and storage behavior.
Run pytest for the affected modules.
```

### Unbounded Refactor

```text
Analyze the whole repo and improve everything that looks bad.
```

Why it is bad: this creates a huge search space, encourages unrelated edits, and makes review difficult. Anthropic’s guidance favors tight scope and bounded tasks.[cite:181][cite:13]

Better version:

```text
Inspect only @src/myapp/cli and @tests/test_cli.py.
Find the top 3 maintainability issues that affect correctness or readability.
Do not change anything yet.
```

### No Verification

```text
Implement config validation.
```

Why it is bad: “done” is undefined, so the model may stop when the code merely looks plausible.[cite:181]

Better version:

```text
Implement config validation in @src/myapp/config.py.
Add tests covering missing required values and invalid integer parsing.
Run `pytest -q tests/test_config.py` and `ruff check .`.
```

### Overengineering Trigger

```text
Refactor this into a clean enterprise-grade architecture.
```

Why it is bad: it rewards abstraction for its own sake and often creates unnecessary layers.[cite:181]

Better version:

```text
Refactor only enough to separate parsing from validation.
No API changes, no new abstractions unless they reduce duplication immediately.
```

### Mixed Multi-Goal Prompt

```text
Fix the parser bug, then suggest naming improvements, then audit auth, then improve docs.
```

Why it is bad: it mixes unrelated goals and degrades context quality. Claude Code docs recommend clearing or splitting sessions when tasks diverge materially.[cite:181][cite:13]

Better version:

Split this into separate conversations or at least separate blocks:
- bug fix
- refactor review
- auth audit
- docs pass

## Typical Professional Workflow

A strong LLM-assisted workflow is staged, reviewable, and test-driven in the broad sense of “always verify.” Anthropic’s documented patterns align well with the workflow many experienced developers use in practice: explore, plan, implement in small slices, verify, review, and only then proceed to the next step.[cite:181][cite:13]

### Block 1. Frame the Task

Define the objective and force clarification before coding.

```text
We are working on a Python 3.13 CLI app.
Read @CLAUDE.md first.

I want to implement [feature].
Do not code yet.

First, restate the task, list assumptions, identify ambiguities, and ask only the non-obvious questions that materially affect implementation.
```

### Block 2. Explore Relevant Code

Ground the model in the actual implementation area.

```text
Inspect only the files relevant to this feature.
Explain the current flow, relevant abstractions, and where the change should live.
Do not propose code yet.
```

### Block 3. Produce a Plan

Ask for alternatives and explicit trade-offs before code changes.[cite:13][cite:181]

```text
Propose 2-3 implementation options, recommend one, and produce a step-by-step plan.
List exact files to change and exact tests to add.
Keep the solution minimal.
```

### Block 4. Approve and Narrow

Tighten the boundaries before execution.

```text
Revise the plan with these constraints:
- no new dependencies
- preserve the current public API
- avoid touching unrelated modules
Now produce the final approved plan.
```

### Block 5. Implement One Slice

Bound the work to one coherent unit. This makes diffs smaller and review easier.[cite:181][cite:169]

```text
Implement only steps 1 and 2 of the approved plan.
Stop after that.
Run the targeted tests for those changes.
Report changed files and any problems encountered.
```

### Block 6. Verify

Make the model prove correctness with concrete commands.[cite:13][cite:181]

```text
Run the relevant tests, lint checks, and type checks for the files you changed.
If something fails, fix the root cause and rerun.
Show the exact commands and summarize the results.
```

### Block 7. Self-Review

Add a critique pass before human review.[cite:181]

```text
Review the current diff against the approved plan.
Flag only:
- correctness gaps
- scope violations
- missing edge-case tests
- hidden breaking changes

Ignore cosmetic suggestions unless they improve maintainability materially.
```

### Block 8. Human Review

At this stage, review the diff in VS Code, inspect changed files, stage only the acceptable hunks, and either request a follow-up patch or continue. This pairs well with a terminal-first Claude workflow and VS Code as the review surface.[cite:169]

### Block 9. Update Project Memory

Persistent instructions should stay short and stable, while changing status belongs in separate progress documents.[cite:181][cite:172][cite:173]

```text
Update progress.md with:
- what was completed
- what remains
- known risks

Update decisions.md only if an architectural or API decision changed.
Keep both concise and factual.
```

### Block 10. Prepare Commit / PR Summary

Close the task with a clean human-facing summary.

```text
Prepare a commit message and a short PR summary.
Include:
- what changed
- why
- how it was verified
- notable risks
Do not commit yet.
```

## Recommended Defaults for This Project Style

For a Python 3.13 terminal-first workflow on Ubuntu with VS Code as the diff and review surface, these defaults are strong:

- Communicate in English with short, explicit prompts.[cite:171]
- Ask Claude to read project rules first and stop after each major step.[cite:169][cite:172]
- Keep diffs minimal and avoid unrelated edits.[cite:172][cite:173]
- Always define exact verification commands.[cite:181][cite:13]
- Use separate conversations when the task changes substantially.[cite:181]
- Keep `CLAUDE.md` stable; put volatile task state in `progress.md` or a spec file.[cite:172][cite:173]

A simple default loop is:

**spec -> explore -> plan -> implement one slice -> verify -> self-review -> human diff review -> update progress -> next slice**.[cite:181][cite:13]
