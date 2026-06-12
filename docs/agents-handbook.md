# Agents Handbook for One-Repo Work

This handbook defines a practical v1 operating model for using agents and skills in tools like Claude Code and OpenCode inside one project-local repository. It assumes automatic routing is allowed, but important actions should remain approval-aware and incremental.[cite:47][cite:38][cite:58]

## Purpose

The goal is to improve coding, architecture/documentation, and governance work without letting context grow noisy, unstable, or hard to review. The system should keep the main thread clear, offload noisy subtasks, and return compact results from specialists rather than raw hidden chatter.[cite:48][cite:13]

## Assumptions

- One repo only for v1.
- One main orchestrator plus seven specialists.
- The main agent may auto-route to the closest specialist.[cite:47]
- Specialists may overlap lightly, but the narrowest specialist should win by default.[cite:47]
- Write actions happen stepwise, not as one large autonomous wave.
- Read-only parallelism is allowed for exploration, review, and incident triage.[cite:48]
- Drafting docs and ADRs is allowed, but important changes still require review before trust or merge.
- Specialist output is a proposal, not authority.[cite:48]

## Core Constraints

| Topic | Rule |
|---|---|
| Delegation | Auto-decide routing is allowed.[cite:47] |
| Execution | Ask before each implementation slice.[cite:38] |
| Weak specialist | The main agent may try another specialist automatically. |
| Overlap | Allowed, but keep it light; prefer the narrowest specialist first.[cite:47] |
| Architecture issues found off-scope | Note and continue. |
| ADR and docs | Produce options or draft text for approval. |
| Reviewer | Read-only. |
| Incident work | Suggest code, config, or recovery actions when needed. |
| Large autonomous refactors | Not allowed. |
| Giant instruction files | Not allowed. |
| Super-agent mega prompt | Not allowed. |
| AI-only governance enforcement | Not allowed. |

## V1 Operating Rules

1. The main agent owns the human conversation.
2. The main agent routes noisy subtasks to specialists.
3. Specialists return compact findings, not raw exploration chatter.[cite:48]
4. For implementation, use a slice workflow: explore, plan, ask, change, verify, ask next.[cite:38]
5. Use parallel specialists only for read-heavy tasks such as exploration, review, and incident triage.[cite:48]
6. Never let docs, configs, or architecture files change silently.[cite:38][cite:58]
7. If scope grows, stop and ask instead of improvising.
8. If one specialist underperforms, retry once with a better specialist rather than fanning out endlessly.

## Specialist Roster

Use these seven specialists in v1.

| Specialist | Purpose | Writes? |
|---|---|---|
| orchestrator-main | Talks to the human, routes work, merges results | Yes, with approval |
| implementer | Feature code, focused fixes, small refactors | Yes, stepwise |
| explorer | Codebase search, dependency tracing, impact scan | No |
| architect | Design options, boundaries, trade-offs, integration shape | Draft only |
| reviewer | Diff review, risk spotting, regression suspicion | No |
| doc-writer | ADR draft, architecture notes, task summaries | Draft only |
| incident-analyst | Triage, failure-path analysis, recovery suggestions | Suggest only |

The roster stays intentionally compact because delegation quality depends on clear role descriptions and low ambiguity between specialists.[cite:47]

## Agent File Design

Each agent file should stay short, stable, and mechanical. Claude-style delegation relies on the description field to decide when a subagent should be used, so role boundaries must be obvious and mutually distinguishable.[cite:47]

Each agent file should include only:

- Role.
- Use when.
- Do.
- Do not.
- Stop and ask when.
- Output shape.

Target size:

- Agent file: 20 to 40 lines.
- Keep only stable behavior.
- Split the file if it starts to become a mini-framework.

Do not put these into agent files:

- Long examples.
- Historical discussion.
- Repeated repo knowledge.
- Every policy in every file.
- Temporary task state.

## Skill File Design

Skills should be lightweight reusable procedures rather than judgment-heavy personas. OpenCode documents skills as reusable instructions discovered from the repo or home directory and loaded on demand when relevant.[cite:13]

Each skill file should include only:

- Trigger or use case.
- Exact procedure.
- Commands or checklist.
- Expected output.

Target size:

- Skill file: 15 to 30 lines.
- Prefer procedural steps over abstract advice.
- Split large skills into smaller ones by workflow.

## Where To Put Rules

Stable project truth belongs in one shared repo instruction file rather than being duplicated across all agents. OpenCode exposes a rules layer through AGENTS.md-style project instructions, while agents and skills should stay focused on role behavior and reusable procedures.[cite:58][cite:25][cite:13]

Use this separation:

- Shared repo rules: build, test, lint, architecture boundaries, approval policy, coding conventions.
- Agents: role identity and boundaries.
- Skills: reusable playbooks.
- Settings: hard guardrails such as permissions.
- Prompt templates: repeatable task entry points.

## What To Tune First

Tune in this order:

1. Agent and skill markdown files first.
2. Tool permissions and settings second.[cite:38]
3. Prompt templates third.
4. Free-form prompt style last.

This order works because role boundaries solve weak routing, permissions enforce ask-before-acting behavior, and templates improve repeatability after the structure is already sound.[cite:47][cite:38]

## Practical Work Plan

Follow this order by hand:

1. Create one shared repo instruction file with build, test, lint, architecture boundaries, coding conventions, and approval policy.
2. Create the seven agent files with clearly separated descriptions.
3. Create four to six small skills.
4. Tighten settings so write-capable tools require the right approval behavior.[cite:38]
5. Create one prompt template for each recurring task type.
6. Run five small real tasks in one repo.
7. After each run, edit only one lever: prompt template, agent file, skill file, or settings.

## Starter Skills

Start with these skills:

- explore-codebase
- implement-feature-slice
- review-diff
- draft-adr
- incident-triage
- refactor-small-safe

## Prompt Pattern

Use a repeatable prompt shape for the main agent.

```text
Goal: implement X.
Scope: only files under module Y.
First explore, then propose a 3-step plan.
Use implementer if coding is needed, explorer if codebase search is needed.
Ask before each implementation slice.
Do not change configs or docs silently.
Return: findings, plan, proposed first slice.
```

This prompt style works better than broad “do everything” prompts because it combines auto-routing with explicit scope, approval boundaries, and a concrete deliverable.[cite:47][cite:48][cite:38]

## First Week Plan

- Day 1: Write shared repo rules and three agent files.
- Day 2: Finish all seven agent files.
- Day 3: Write four starter skills.
- Day 4: Tighten OpenCode permissions and Claude project instructions.[cite:38][cite:58]
- Day 5: Create five prompt templates.
- Day 6: Run three tiny real tasks and record failures.
- Day 7: Prune overlaps, shorten markdown files, and remove anything not used.

## Direct Answers

### Should the main agent be trusted to decide when to use agents and skills?

Partly. Let the main agent auto-route, but control action through permissions, stepwise approval, and narrow definitions rather than total trust.[cite:47][cite:38]

### Should agents or skills be called explicitly in prompts?

Sometimes. Use explicit calls when the task is risky, ambiguous, or repeatedly routed poorly; otherwise let the main agent choose.[cite:47][cite:13]

### How often should agent and skill markdown files be changed?

Frequently at the beginning, then rarely. Change them after recurring pattern failures, not after every imperfect run.

### How should context be kept concise?

Keep stable rules in one shared file, keep agents short, keep skills procedural, and make specialists return summaries only rather than raw internal work.[cite:48][cite:58][cite:13]

## Mental Model

Use this model:

- Rules are the constitution.
- Agents are roles.
- Skills are playbooks.
- Settings are locks.
- Prompts are task tickets.

This separation keeps the system practical, reviewable, and easier to tune over time.[cite:58][cite:13][cite:38]
