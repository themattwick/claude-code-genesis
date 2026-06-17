---
name: brain-ops
description: >
  Operational engine of Project BRAIN. The active companion to the `brain` router.
  Handles checkpoints, handoffs, hygiene and knowledge capture. The preferred interface
  is the unified `brain` router skill. This engine can be called directly when needed.
metadata:
  short-description: "BRAIN ops engine. Preferred via 'brain ...' router."
  category: "workflow"
  tags: ["brain", "project-brain", "checkpoints", "cross-model", "hygiene"]
---

# brain-ops — BRAIN Operations Engine

**Recommended:** Use the `brain` router skill as your daily interface:
- "brain checkpoint [description]"
- "brain handoff"
- "brain hygiene check"

## Responsibilities

- Checkpoint discipline (save progress every 60-90 min)
- Turn raw work into structured entries in `BRAIN/decisions/`, `bugs/`, `learnings/`, `patterns/`
- Prepare high-quality handoffs for other models
- Keep the Project BRAIN healthy

## Commands

```bash
# Save progress
/brain checkpoint "what I just completed"

# Cross-model handoff
/brain handoff

# Health check
/brain hygiene

# Session summary
/brain report
```

## Helper Scripts

```bash
# Check current state
python .claude/scripts/brain_load.py

# Prepare consolidation
python .claude/scripts/brain_consolidate.py
```

## Related Skills

- `brain` — Router/entry point (recommended)
- `brain-init` — One-time project setup
- `brain-memory` — Persistent learning (v1.1)
