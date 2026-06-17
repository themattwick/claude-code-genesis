---
name: brain
description: >
  Unified entry point for everything related to Project BRAIN.
  All BRAIN-related actions should start with the word "brain".
  This skill routes and coordinates between brain-init (initial setup) and brain-ops (ongoing checkpoints, handoffs, hygiene, organization).
  Say things like: "brain setup", "brain checkpoint", "brain handoff", "brain hygiene", "brain load", etc.
metadata:
  short-description: "Single entry point for Project BRAIN actions (setup + operations)"
  category: "workflow"
  tags: ["brain", "project-brain", "checkpoints", "handoff", "cross-model"]
---

# brain — Unified Project BRAIN Interface (Claude side)

This is the **recommended single entry point** for everything related to Project BRAIN.

From now on, start BRAIN-related requests with the word **"brain"**.

## Examples of good usage

- "brain setup this project"
- "brain init"
- "brain bootstrap"
- "brain checkpoint what I just finished"
- "brain handoff for Grok"
- "brain prepare final report"
- "brain hygiene check"
- "brain organize these notes"
- "brain create decision about X"

## How it works internally

This skill acts as a smart router:

| Your phrase starts with...                              | What actually happens                                      | Underlying skill used      |
|---------------------------------------------------------|------------------------------------------------------------|----------------------------|
| "brain setup", "brain init", "brain bootstrap"       | One-time creation of the full `BRAIN/` structure + ready sections for AGENTS.md / CLAUDE.md | `brain-init`             |
| "brain checkpoint", "brain handoff", "brain hygiene", "brain report", "brain organize", etc. | Active operations during or after work                     | `brain-ops`              |
| "brain ..." (general)                                  | The router decides the best action (may use both skills)   | `brain-ops` + `brain-init` |

## Relationship to other skills

- `brain-init` → the one-time setup skill (this is the new name for what used to be called the old `project-memory` skill). You normally invoke it by saying "brain init" or "brain setup".
- `brain-ops` → the core engine for ongoing operations. You can call it directly for advanced use, but the `brain` router is the recommended daily interface.
- This `brain` skill is the user-friendly front door for the whole system.

## Recommendation

Add the `brain` skill to your DAILY set for any serious project that uses Project BRAIN.

**Preferred way from now on:** Always start with the word "brain".

## Loading Current State

Commands like:
- brain load
- brain status
- brain briefing
- brain current state

Best way: Run the helper script:

```bash
python C:\Users\MaxOFFe\.claude\skills\brain\scripts\brain_load.py
# or with path
python C:\Users\MaxOFFe\.claude\skills\brain\scripts\brain_load.py "C:\CLAUDE"
```

The script finds the latest handoff/summary document, recent checkpoints, key decisions and hard cases, and prints a clean, structured briefing of the current state of the Project BRAIN.

This works at any time of day — not tied to morning or night work.

### Consolidation

- brain consolidate

Helps synthesize scattered material (checkpoints, raw notes, multiple related entries) into clean, high-quality entries in `decisions/`, `learnings/`, `bugs/`, etc.

This is different from Claude's native `/compact` — it's about long-term knowledge quality in the Project Brain, not just shrinking the current context.

**Practical helper:**
Run `python C:\Users\MaxOFFe\.claude\skills\brain\scripts\brain_consolidate.py` for a preparation report before doing consolidation work.

See full docs: `C:\Users\MaxOFFe\.grok\skills\brain\SKILL.md`
