# Genesis — Skills for Claude Code

**The origin of intelligent workflows.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1%2B-green.svg)]()

Genesis is a focused set of skills for Claude Code, built on the **BRAIN** system — a memory layer battle-tested in daily cross-model work (Claude ↔ Grok). Start with checkpoints, handoffs, and persistent memory.

## Why Genesis?

Claude Code is powerful, but context is fragile. Genesis solves real problems:
- 💾 **Lost progress?** Save checkpoints, resume anywhere
- 🔄 **Switching models?** Hand off context to Opus or Sonnet without losing state
- 🧠 **Forgetting patterns?** Remember what you learned across sessions

## Installation

Copy the skills you want into your project's `.claude/skills/` directory:

```bash
# Clone the repo
git clone https://github.com/themattwick/claude-code-genesis.git

# Copy all brain skills to your project
cp -r claude-code-genesis/.claude/skills/brain* your-project/.claude/skills/
```

Then use them in any Claude Code session:

```
brain setup          # one-time project init
brain checkpoint "Designed database schema"
brain load           # check current state
brain handoff        # prepare context for another model
```

## Brain System: Core Foundation

Genesis is built on the **Project BRAIN** system — a filesystem-based long-term memory shared between AI sessions and models.

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
brain setup                      # One-time project setup
brain init                       # Alternative to setup

# Daily operations
brain checkpoint "description"   # Save progress snapshot
brain handoff                    # Prepare cross-model context transfer
brain hygiene                    # Health check on BRAIN/ structure
brain report                     # Session summary

# State management
brain load                       # Check current state
brain status                     # Quick status

# Knowledge management
brain organize                   # Organize raw notes into structured entries
brain consolidate                # Synthesize checkpoints into decisions/learnings
brain remember "pattern"         # Save pattern (v1.1)
brain recall "topic"             # Find pattern (v1.1)
```

### BRAIN Directory Structure

Each project gets a `BRAIN/` directory after running `brain setup`:

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

## See It In Action

Want to know what a real `BRAIN/` looks like after a week of work? Check out
[examples/sample-project/](./examples/sample-project) — a worked example with
real checkpoints, a decision record, and a cross-model handoff.

## Philosophy

- **Quality over quantity** — Each skill earns its place
- **Single responsibility** — Each skill solves one problem well
- **Composable** — Skills work together seamlessly
- **Transparent** — System prompts and patterns visible
- **Evolvable** — Grows with real-world feedback

## Roadmap

See [ROADMAP.md](./docs/ROADMAP.md) for what's shipped, what's next, and what's
still just an idea. Short version:

- **Now** — BRAIN system: router, init, ops (+ memory stub)
- **Next** — full brain-memory recall, smoother install, more examples
- **Exploring** — research/TDD patterns, semantic search, multi-agent workflows

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
