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

Single entry point. Always start with the word **"brain"**. This skill only **routes**:
what each operation does lives in `brain-ops` (and `brain-init` for setup), nowhere else.

## Routing Table

| Phrase | Routes to |
|--------|-----------|
| "brain setup", "brain init", "brain bootstrap" | `brain-init` (see note below) |
| "brain checkpoint", "brain handoff", "brain report" | `brain-ops` |
| "brain index", "brain reindex" | `brain-ops` |
| "brain consolidate", "brain organize" | `brain-ops` |
| "brain define", "brain glossary" | `brain-ops` |
| "brain hygiene" | `brain-ops` |
| "brain remove" | `brain-ops` |
| "brain load", "brain status", "brain briefing" | handled here — see below |
| "brain ..." (anything else) | Decide the best action |

`brain-init` is not model-invoked. If it cannot be started from here, tell the user to
run `/brain-init`.

## brain load

Read `BRAIN/INDEX.md` — it already summarizes current state, active knowledge and retired
entries. If it is missing or stale, run `brain index` first (a `brain-ops` operation), then
present the current-state header plus whatever is relevant to the task.

## Related Skills

- `brain-init` — One-time project setup
- `brain-ops` — Core operations engine
- `brain-memory` — Persistent learning (v1.1)
