# Genesis — Production-Ready Skills for Claude Code

**The origin of intelligent workflows.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)]()
[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1%2B-green.svg)]()

Genesis is a comprehensive hub of production-ready skills for Claude Code. Start with intelligent checkpoints, cross-model handoffs, and persistent memory—then expand to security guardrails, research automation, and beyond.

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

# Or install specific skills individually
/skill install genesis@anchor
/skill install genesis@anchor-handoff
/skill install genesis@anchor-memory
```

### 3-Minute Tutorial

```bash
# 1. Create a checkpoint
/anchor checkpoint "Designed database schema"

# 2. Do more work... 30 minutes pass

# 3. Resume from checkpoint
/anchor resume "Designed database schema"
# Full context restored instantly

# 4. Handoff to another model
/anchor handoff --to=opus "Continue this design"
# Opus has full context, no copy-paste needed
```

## Core Skills (v1.0)

| Skill | Purpose | Status |
|-------|---------|--------|
| **anchor** | Checkpoint system for tracking progress | ✅ Ready |
| **anchor-handoff** | Cross-model context transfer | 🔄 In Progress |
| **anchor-memory** | Persistent learning across sessions | 🔄 In Progress |
| **anchor-security** | Safety guardrails & validation | 🔄 Planned |

## Philosophy

- **Quality over quantity** — Production-tested before release
- **Single responsibility** — Each skill solves one problem well
- **Composable** — Skills work together seamlessly
- **Transparent** — System prompts and patterns visible
- **Evolvable** — Grows with real-world feedback

## Documentation

- **[CLAUDE.md](./CLAUDE.md)** — Project structure and setup
- **[ROADMAP.md](./docs/ROADMAP.md)** — v1.0 through v2.0 timeline
- **[CONTRIBUTING.md](./docs/CONTRIBUTING.md)** — How to create skills
- **[Skills Directory](./docs/SKILL_DIRECTORY.md)** — All skills documented

## Roadmap

- **v1.0** (June 2026) — Launch with 4 core skills
- **v1.1** (July 2026) — Research automation + TDD patterns
- **v1.2** (August 2026) — Performance optimization guides
- **v2.0** (Q3 2026) — Multi-agent orchestration + enterprise features

## License

MIT — Use freely in your projects.

## Support

- 🐛 **Issues:** [Report bugs](https://github.com/themattwick/claude-code-genesis/issues)
- 💬 **Discussions:** [Share ideas](https://github.com/themattwick/claude-code-genesis/discussions)
- 📚 **Docs:** [Full documentation](./docs)

---

**Built with ⚓ by [themattwick](https://github.com/themattwick)**

*"The origin of intelligent workflows."*
