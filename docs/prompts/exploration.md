# Template: Exploration

## When to use
Before touching unfamiliar code. Keeps the model in analysis mode and prevents premature edits.

## Prompting style note
For complex or multi-step tasks, wrap major sections in XML tags (e.g., `<context>`, `<task>`, `<constraints>`, `<verification>`) to reduce ambiguity and improve instruction following.

---

## Variant A: General discovery

```text
<context>
Read @CLAUDE.md first.
Read relevant `.claude/rules/` files (e.g., `python-style.md`, `testing.md`, `typing.md`) before proceeding.
</context>

<task>
Read [relevant directories/files].

Do not modify anything.

I need to understand how [topic] works in this project.

Please:
1. Identify the main files and entry points.
2. Trace the [flow/topic] end to end.
3. Explain which abstractions are core vs incidental.
4. List likely extension points for [future change].

Keep the answer concise and concrete, with file references.
Stop after this step.
</task>
```

---

## Variant B: Targeted exploration

```text
<context>
Read @CLAUDE.md first.
Read relevant `.claude/rules/` files before proceeding.
</context>

<task>
Inspect only the files relevant to [topic].
Explain the current flow, relevant abstractions, and where a change should live.
Do not propose code yet.
Stop after this step.
</task>
```

---

## Output format

1. **Files examined** — list of paths read
2. **Current flow** — step-by-step trace with file:line references
3. **Core abstractions** — classes/functions that define the domain model
4. **Incidental details** — implementation choices that could change
5. **Extension points** — where new behavior would plug in
6. **Open questions** — anything unclear that needs clarification before editing
