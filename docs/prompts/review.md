# Template: Review

## When to use
After coding, before human review. Covers both self-review and peer/PR review.

## Prompting style note
For complex or multi-step tasks, wrap major sections in XML tags (e.g., `<context>`, `<task>`, `<constraints>`, `<verification>`) to reduce ambiguity and improve instruction following.

---

## Severity taxonomy (use for both variants)

- **Critical** — must fix before merge; affects correctness, security, or data integrity
- **Recommendations** — should fix or discuss; affects maintainability or clarity
- **Questions** — need author clarification; may or may not require changes

---

## Variant A: Self-Review

### Prompt

```text
<context>
Read @CLAUDE.md and relevant `.claude/rules/` files first.
</context>

<task>
Review the current diff against the approved plan as a strict senior engineer.

Check for:
- plan alignment and scope creep
- unnecessary changes
- overengineering
- hidden breaking changes
- weak naming
- incomplete tests
- duplicate logics
- unclear error handling
- deviations from the stated task

Report only issues that affect correctness, maintainability, or scope.
Ignore cosmetic style preferences unless they materially improve the result.
</task>
```

### Output format

1. **Plan alignment** — does the diff match what was approved, with no scope creep?
2. **Critical issues** — correctness risks, logic errors, race conditions, edge cases
3. **Recommendations** — naming, duplication, complexity, hidden coupling
4. **Test gaps** — missing coverage, fragile assertions
5. **Breaking changes** — API or behavior changes not explicitly approved
6. **Go / no-go verdict** — whether the diff is ready for human review

---

## Variant B: Peer / PR Review

### Prompt

```text
<context>
Read @CLAUDE.md and relevant `.claude/rules/` files first.
</context>

<task>
Review the following diff as a strict senior engineer.

Focus on:
- correctness and edge-case handling
- clarity and readability
- test coverage and quality
- adherence to project conventions
- hidden coupling or unintended side effects
- whether the change is the minimal correct fix

Do not suggest purely cosmetic changes unless they materially improve maintainability.
For each issue, cite the file and line, explain the risk, and suggest a fix or ask a clarifying question.
</task>
```

### Output format

1. **Summary** — what the PR does and overall quality judgment
2. **Critical issues** — must fix before merge
3. **Recommendations** — should fix or discuss
4. **Questions** — clarifications needed from the author
5. **Approval status** — approve / approve with comments / request changes
