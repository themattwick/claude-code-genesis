# Project BRAIN — Quick Reference

**Main location:** `BRAIN/` (project-local, or `~/BRAIN/` for a global setup)

## When to write here
- After significant debugging or analysis
- After discovering important domain-specific edge cases
- After making architectural decisions
- During long sessions (use `checkpoints/`)
- After extracting a reusable insight from messy work

## Subfolders
- `learnings/` — General important conclusions
- `decisions/` — Why we chose X instead of Y + reasoning
- `patterns/` — Recurring good/bad patterns
- `bugs/` — Hard problems and their solutions
- `checkpoints/` — Lightweight notes during long work (every 60-90 min recommended)
- `sessions/` — Bigger session retrospectives
- `handoffs/` — Cross-model transfer documents

## Rules for AI assistants
1. Check `BRAIN/` at the start of any serious work.
2. Write with dated filenames.
3. Be concrete (paths, examples, line numbers).
4. This is the main way different AIs (Claude ↔ Grok) communicate across sessions.

## Recommended rhythm
- Every 60-90 minutes of deep work → create a checkpoint in `checkpoints/`
- End of major block → summarize into `learnings/`, `bugs/`, or `decisions/`
- After long session → extract key points into `learnings/` or `decisions/`

This system is part of the DAILY workflow for projects that need strong cross-session and cross-AI knowledge (Project BRAIN).