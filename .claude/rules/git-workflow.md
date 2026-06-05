# Git Workflow Rules

## Commit hygiene
- Keep changes small and reviewable.
- Do not mix refactoring with feature work unless necessary.
- Avoid touching unrelated files.

## Before commit
Run:
```bash
make check
```

## Safety
- Never commit `.env`, secrets, tokens, or credentials.
- Ask before destructive actions, force-push, history rewrites, or deleting branches.
- Ask before changing CI, release flow, or dependency strategy.

## Review mindset
- Summarize changed files.
- Note risks and follow-ups.
- Mention which checks were run.
