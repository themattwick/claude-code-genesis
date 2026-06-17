---
name: brain-memory
description: Persistent learning system — store and recall patterns across sessions
metadata:
  short-description: "Persistent learning across sessions (v1.1)"
  category: "workflow"
  tags: ["brain", "memory", "persistence", "learning", "patterns"]
---

# brain-memory — Persistent Learning System

Store and recall important patterns, decisions, and insights across sessions.

## Status

🔄 **v1.1 Feature** — Foundation being planned for Genesis v1.0 launch.
Currently, use `brain-ops` for session-specific tracking.

## Planned Usage

```
brain remember "Pattern: Always validate user input before processing"
brain recall "patterns about validation"
brain patterns list
```

## Architecture (Planned)

- Storage: BRAIN/patterns/, BRAIN/learnings/, BRAIN/insights/
- Retrieval: Semantic search across stored patterns
- Integration: Works with brain-ops checkpoints

## Coming in Genesis v1.1

See ROADMAP.md for timeline.
