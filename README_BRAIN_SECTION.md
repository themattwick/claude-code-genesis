## Brain System Integration

Genesis includes the proven **Project BRAIN** system for intelligent workflow management:

### Core Skills

- **brain** — Smart router for all BRAIN commands
- **brain-init** — One-time project setup
- **brain-ops** — Daily operations (checkpoints, handoffs, hygiene)
- **brain-memory** — Persistent learning (coming v1.1)

### Quick Start

```bash
# Setup your project
/brain setup

# Save checkpoint during work
/brain checkpoint "Completed authentication module"

# Check current state anytime
/brain load

# Hand off to another model
/brain handoff --to=opus "Continue implementation"

# Consolidate learnings
/brain consolidate
```

### BRAIN Directory Structure

Each project gets a `BRAIN/` directory:
- `checkpoints/` — Progress snapshots
- `decisions/` — Key decisions made
- `learnings/` — Extracted insights
- `bugs/` — Hard cases encountered
- `handoffs/` — Cross-model transfer docs

### Helper Scripts

- `python .claude/scripts/brain_load.py` — Current state briefing
- `python .claude/scripts/brain_consolidate.py` — Knowledge synthesis prep

See [CLAUDE.md](./CLAUDE.md) for full documentation.
