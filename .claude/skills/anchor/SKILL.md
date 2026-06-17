---
name: anchor
description: Checkpoint system for tracking progress in long-running tasks
version: 1.0.0
author: themattwick
requires: claude-code >= 2.1
tags: [checkpoint, memory, persistence, state-management]
keywords: [save, checkpoint, progress, resume, state, tracking]
---

# Anchor — Checkpoint System

Save and resume your work at any point. Anchor creates intelligent checkpoints that preserve context, decisions, and progress.

## Usage

### Create a Checkpoint

```
/anchor checkpoint "Completed database schema design"
```

Creates a snapshot of:
- Current task context
- Files modified
- Decisions made
- Progress so far

### Resume from Checkpoint

```
/anchor resume <checkpoint-name>
```

Restores:
- Full context from checkpoint
- Modified files
- Task state
- Previous decisions

### List Checkpoints

```
/anchor list
```

Shows all checkpoints with timestamps and descriptions.

### View Checkpoint Details

```
/anchor view <checkpoint-name>
```

Shows what was in that checkpoint—useful before resuming.

## Key Features

✅ **Atomic snapshots** — Captures complete state  
✅ **Zero friction** — One command to checkpoint  
✅ **Resumable** — Jump back instantly  
✅ **Documented** — Each checkpoint has context  
✅ **Safe** — Original files never overwritten without confirmation  

## Best Practices

1. **Checkpoint before context switch** — Before handing off to another model
2. **Descriptive names** — "Completed auth schema" beats "checkpoint-1"
3. **Regular checkpoints** — Every major milestone, not just at the end
4. **Review before resume** — Use `/anchor view` before resuming

## Examples

### Long-Running Task

```
# Start: Design database schema
/anchor checkpoint "Database schema v1"

# ... 30 minutes later, resume where you left off
/anchor resume "Database schema v1"
```

### Cross-Model Handoff

```
# In Claude Haiku
/anchor checkpoint "Completed initial design"

# Switch to Claude Opus
/anchor resume "Completed initial design"
# Opus continues with full context
```

### Iterative Refinement

```
/anchor checkpoint "Feature v1 complete"
# Iterate and improve
/anchor checkpoint "Feature v1.1 — improved error handling"
# Can always revert to v1 if needed
```

## Architecture

Checkpoints are stored in `.claude/checkpoints/` with:
- `meta.json` — Timestamp, description, metadata
- `context.md` — What was happening
- `files/` — Modified files snapshot
- `decisions.json` — Key choices made

## Related Skills

- **anchor-handoff** — Transfer between models
- **anchor-memory** — Long-term learning
- **anchor-security** — Validate before resuming
