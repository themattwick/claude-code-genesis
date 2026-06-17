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

```
brain checkpoint "what I just completed"   # Save progress
brain handoff                               # Cross-model handoff
brain hygiene                               # Health check
brain report                                # Session summary
```

## Helper Script

```bash
# Create a timestamped checkpoint file
python .claude/skills/brain-ops/scripts/create_checkpoint.py "Short title"
```

## Related Skills

- `brain` — Router/entry point (recommended)
- `brain-init` — One-time project setup
- `brain-memory` — Persistent learning (v1.1)
