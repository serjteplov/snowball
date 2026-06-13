# Template: ADR Drafting

## When to use
Before the first implementation pass on a greenfield project, large feature, or architectural change. Spec-first workflow for ambiguous tasks.

## Prompting style note
For complex or multi-step tasks, structure the prompt with labeled sections (e.g., `Context:`, `Task:`, `Constraints:`, `Verification:`) to keep instructions unambiguous.

---

## Prompt

```text
Context:
Read @CLAUDE.md, existing ADRs in @docs/adr/, and the relevant code.
Read relevant `.claude/rules/` files (e.g., `python-style.md`, `testing.md`, `typing.md`) before proceeding.

Task:
We need to make an architectural decision about [topic].

Do not implement yet.

Please:
1. Interview me to clarify:
   - use cases and non-goals
   - constraints (performance, security, compatibility)
   - options considered and rejected
   - failure modes and mitigations
   - impact on existing code and APIs
   - rollout / migration strategy
   - observability and testing implications
2. Summarize the decision, context, and consequences.
3. Draft the ADR to @docs/adr/NNNN-[short-title].md using this format:
   - Title
   - Status (proposed)
   - Context
   - Decision
   - Consequences (positive, negative, neutral)
   - Compliance (how we will verify this decision is followed)

Keep asking until the spec is complete.
Stop after this step.
```

---

## Constraints

- Python 3.13
- Follow existing project patterns
- Preserve backward compatibility unless explicitly approved
- Keep the design simple

## Output format

1. **Context summary** — what problem the decision solves
2. **Decision** — the chosen option, stated clearly
3. **Consequences** — positive, negative, and neutral
4. **ADR file** — path and status (proposed / accepted / deprecated)
5. **Open questions** — anything that needs human resolution before implementation
