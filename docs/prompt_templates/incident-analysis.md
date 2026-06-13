# Template: Incident Analysis

## When to use
Investigating a production issue, bug report, or unexpected behavior. Read-only exploratory mode.

## Prompting style note
For complex or multi-step tasks, structure the prompt with labeled sections (e.g., `Context:`, `Task:`, `Constraints:`, `Verification:`) to keep instructions unambiguous.

---

## Prompt

```text
Context:
Read @CLAUDE.md and the files involved in [affected area].
Read relevant `.claude/rules/` files before proceeding.

Task:
Do not modify anything.

Incident:
[observable symptom: error message, user report, metric anomaly, etc.]

Please:
1. Check recent commits in the affected area (`git log --oneline -- path/`).
2. Examine any available logs, error output, or telemetry.
3. Reproduce the issue mentally or with a targeted command.
4. Trace the execution path from entry point to failure.
5. Identify the root cause, not just the symptom.
6. List contributing factors (config, data, race condition, recent change, etc.).
7. Propose remediation options with trade-offs.
8. Suggest prevention measures (tests, monitoring, alerts, docs).

Keep the answer concise and concrete, with file references.
Stop after this step.
```

---

## Constraints

- Do not edit files during analysis
- Do not speculate beyond the evidence in code and logs
- Distinguish facts from hypotheses

## Output format

1. **Incident summary** — what happened, when, and impact
2. **Recent changes** — commits that touched the affected area
3. **Reproduction steps** — how to trigger the issue
4. **Execution trace** — file:line path from entry to failure
5. **Root cause** — the underlying defect or design flaw
6. **Contributing factors** — conditions that allowed the incident
7. **Remediation options** — short-term fix vs long-term fix, with trade-offs
8. **Prevention** — tests, monitoring, or process changes to avoid recurrence
9. **Open questions** — anything that needs logs, metrics, or human input to confirm
