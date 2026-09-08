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

# brain — Unified Project BRAIN Interface

Single entry point for everything related to Project BRAIN. Always start with the word **"brain"**.

## Commands

### Setup (one-time)
- `brain setup` / `brain init` / `brain bootstrap`

### Daily Operations
- `brain checkpoint [description]` — Save progress snapshot
- `brain handoff` — Prepare cross-model context transfer
- `brain hygiene` — Health check on BRAIN/ structure
- `brain report` — Session summary
- `brain organize` — Synthesize raw notes into structured entries

### Loading State
- `brain load` / `brain status` / `brain briefing`

When asked to load state, prefer the generated index:
1. If `BRAIN/INDEX.md` exists, read it — it already summarizes current state,
   active knowledge, and retired entries.
2. If it's missing or looks stale, regenerate it first:
   `python .claude/skills/brain-ops/scripts/build_index.py <project-root>`
3. Present the current-state header plus anything relevant to the task.

### Indexing
- `brain index` / `brain reindex`

Regenerate `BRAIN/INDEX.md` from entry frontmatter. Run after adding or retiring
entries. See `docs/FRONTMATTER.md` for the entry format.

### Consolidation
- `brain consolidate`

Review raw material in `BRAIN/checkpoints/` and `BRAIN/sessions/`, then synthesize into structured entries in `BRAIN/decisions/`, `BRAIN/learnings/`, `BRAIN/bugs/`, `BRAIN/patterns/`, `BRAIN/reference/`, or `BRAIN/specs/`.

### Glossary
- `brain define <term>` / `brain glossary`

Write or redefine a domain-term entry in `BRAIN/glossary/`. A redefinition never
edits in place — it supersedes the old entry so the drift in meaning is kept.

## Routing Table

| Phrase | Routes to |
|--------|-----------|
| "brain setup", "brain init", "brain bootstrap" | `brain-init` |
| "brain checkpoint", "brain handoff", "brain hygiene", "brain report" | `brain-ops` |
| "brain load", "brain status", "brain briefing" | Read `BRAIN/INDEX.md` |
| "brain index", "brain reindex" | `brain-ops` (build_index.py) |
| "brain consolidate", "brain organize" | `brain-ops` |
| "brain define", "brain glossary" | `brain-ops` |
| "brain ..." (general) | Decide best action |

## Related Skills

- `brain-init` — One-time project setup
- `brain-ops` — Core operations engine
- `brain-memory` — Persistent learning (v1.1)
