# Genesis — Production-Ready Skills for Claude Code

**The origin of intelligent workflows.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)]()
[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1%2B-green.svg)]()

Genesis is a comprehensive hub of production-ready skills for Claude Code. Built on the proven **Project BRAIN** system for intelligent workflow management.

## Why Genesis?

Claude Code is powerful, but context is fragile. Genesis solves real problems:
- 💾 **Lost progress?** Save checkpoints, resume anywhere
- 🔄 **Switching models?** Hand off context to Opus or Sonnet without losing state
- 🧠 **Forgetting patterns?** Remember what you learned across sessions
- 🛡️ **Safety first?** Validate operations before executing

## Quick Start

### Installation

```bash
# Install the entire genesis hub
/plugin install genesis

# Or install specific brain skills individually
/skill install genesis@brain
/skill install genesis@brain-init
/skill install genesis@brain-ops
```

### 3-Minute Tutorial

```bash
# 1. Setup your project
/brain setup

# 2. Save checkpoint during work
/brain checkpoint "Designed database schema"

# 3. Do more work... 30 minutes pass

# 4. Check current state anytime
/brain load
# Shows recent checkpoints, decisions, and issues

# 5. Handoff to another model
/brain handoff --to=opus "Continue this design"
# Opus has full context, no copy-paste needed
```

## Brain System: Core Foundation

Genesis is built on the proven **Project BRAIN** system for intelligent workflow management.

### Core Skills (v1.0)

| Skill | Purpose | Status |
|-------|---------|--------|
| **brain** | Smart router for all BRAIN commands | ✅ Ready |
| **brain-init** | One-time project setup | ✅ Ready |
| **brain-ops** | Daily operations (checkpoints, handoffs, hygiene) | ✅ Ready |
| **brain-memory** | Persistent learning system (patterns + recall) | 🔄 v1.1 |

### Available Commands

```bash
# Setup & initialization
/brain setup                     # One-time project setup
/brain init                      # Alternative to setup

# Daily operations
/brain checkpoint "description"  # Save progress snapshot
/brain handoff --to=opus         # Hand off to another model
/brain hygiene                   # Health check
/brain report                    # Session summary

# State management
/brain load                       # Check current state
/brain status                     # Quick status
/brain current                    # Alias for load

# Knowledge management
/brain organize                   # Organize raw notes
/brain consolidate               # Synthesize learnings
/brain remember "pattern"        # Save pattern (v1.1)
/brain recall "topic"            # Find pattern (v1.1)
```

### BRAIN Directory Structure

Each project gets a `BRAIN/` directory:

```
BRAIN/
├── checkpoints/     # Progress snapshots (save/resume)
├── sessions/        # Session summaries
├── decisions/       # Key decisions made
├── learnings/       # Extracted insights
├── bugs/            # Hard cases encountered
├── patterns/        # Reusable patterns (v1.1)
└── handoffs/        # Cross-model transfer docs
```

### Helper Scripts

**brain_load.py** — Get current state briefing
```bash
python .claude/scripts/brain_load.py
# Shows: latest handoff, recent checkpoints, decisions, bugs
```

**brain_consolidate.py** — Prepare knowledge synthesis
```bash
python .claude/scripts/brain_consolidate.py
# Shows: raw material + structured entries for consolidation
```

## Philosophy

- **Quality over quantity** — Production-tested before release
- **Single responsibility** — Each skill solves one problem well
- **Composable** — Skills work together seamlessly
- **Transparent** — System prompts and patterns visible
- **Evolvable** — Grows with real-world feedback

## Roadmap

- **v1.0** (June 2026) — Brain system + foundation
- **v1.1** (July 2026) — brain-memory + Research patterns
- **v1.2** (August 2026) — Performance optimization
- **v2.0** (Q3 2026) — Multi-agent orchestration + enterprise

## Documentation

- **[CLAUDE.md](./CLAUDE.md)** — Project structure and setup
- **[ROADMAP.md](./docs/ROADMAP.md)** — v1.0 through v2.0 timeline
- **[CONTRIBUTING.md](./docs/CONTRIBUTING.md)** — How to create skills
- **[Skills Directory](./docs/SKILL_DIRECTORY.md)** — All skills documented

## License

MIT — Use freely in your projects.

## Support

- 🐛 **Issues:** [Report bugs](https://github.com/themattwick/claude-code-genesis/issues)
- 💬 **Discussions:** [Share ideas](https://github.com/themattwick/claude-code-genesis/discussions)
- 📚 **Docs:** [Full documentation](./docs)

---

**Built with ⚓ by [themattwick](https://github.com/themattwick)**

*"The origin of intelligent workflows."*
