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

When asked to load state, read the BRAIN/ directory directly:
1. Find the latest file in `BRAIN/handoffs/` or any `*HANDOFF*.md` in root
2. List recent files in `BRAIN/checkpoints/`
3. List recent files in `BRAIN/decisions/`
4. List recent files in `BRAIN/bugs/`
5. Present a structured briefing

### Consolidation
- `brain consolidate`

Review raw material in `BRAIN/checkpoints/` and `BRAIN/sessions/`, then synthesize into structured entries in `BRAIN/decisions/`, `BRAIN/learnings/`, `BRAIN/bugs/`, or `BRAIN/patterns/`.

## Routing Table

| Phrase | Routes to |
|--------|-----------|
| "brain setup", "brain init", "brain bootstrap" | `brain-init` |
| "brain checkpoint", "brain handoff", "brain hygiene", "brain report" | `brain-ops` |
| "brain load", "brain status", "brain briefing" | Read BRAIN/ directly |
| "brain consolidate", "brain organize" | `brain-ops` |
| "brain ..." (general) | Decide best action |

## Related Skills

- `brain-init` — One-time project setup
- `brain-ops` — Core operations engine
- `brain-memory` — Persistent learning (v1.1)
