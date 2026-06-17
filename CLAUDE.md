# Genesis Project Documentation

## Overview

Genesis is a production-ready skills hub for Claude Code focused on intelligent workflows: checkpoints, handoffs, memory, and security.

## Project Structure

```
genesis/
├── .claude/
│   ├── skills/
│   │   ├── anchor/                  ← Main checkpoint skill
│   │   ├── anchor-handoff/          ← Cross-model transfer
│   │   ├── anchor-memory/           ← Persistent learning
│   │   └── anchor-security/         ← Security guardrails
│   ├── agents/                      ← Specialized agents
│   ├── hooks/                       ← Automation hooks
│   └── rules/                       ← Development standards
├── docs/
│   ├── ROADMAP.md                   ← v1.0 → v2.0 timeline
│   ├── CONTRIBUTING.md              ← How to create skills
│   └── SKILL_DIRECTORY.md           ← All skills documented
├── README.md                        ← User-facing intro
├── CLAUDE.md                        ← This file
├── LICENSE                          ← MIT
└── .gitignore
```

## v1.0 Goals

- ✅ **Anchor** — Checkpoint tracking for long-running tasks
- ✅ **Anchor-Handoff** — Seamless cross-model context transfer
- ✅ **Anchor-Memory** — Persistent learning across sessions
- 🔄 **Anchor-Security** — Optional safety guardrails

## Development Workflow

1. **Create skill** — Add to `.claude/skills/[name]/`
2. **Test locally** — Use in Claude Code session
3. **Document** — Add SKILL.md frontmatter
4. **Commit** — Clear, descriptive messages
5. **Release** — Tag version, update ROADMAP

## Skill Format

Each skill uses SKILL.md format with YAML frontmatter:

```markdown
---
name: anchor
description: Checkpoint system for tracking long-running tasks
requires: claude-code >= 2.1
---

# Usage...
```

## Key Principles

- **Quality** — Production-tested before release
- **Focus** — One skill, one responsibility
- **Composable** — Skills work together seamlessly
- **Transparent** — System patterns visible to users
- **Evolvable** — Grows with real-world feedback

## Timeline

- **v1.0** (June 2026) — Launch with 4 core skills
- **v1.1** (July 2026) — Research + TDD patterns
- **v1.2** (August 2026) — Performance optimization
- **v2.0** (Q3 2026) — Enterprise features

## Team

- **Creator:** themattwick
- **Contributors:** Community-driven

## Links

- GitHub: https://github.com/themattwick/claude-code-genesis
- Issues: https://github.com/themattwick/claude-code-genesis/issues
- Discussions: https://github.com/themattwick/claude-code-genesis/discussions
