# Genesis Project Documentation

## Overview

Genesis is a production-ready skills hub for Claude Code focused on intelligent workflows: checkpoints, handoffs, memory, and cross-model collaboration. Built on the proven **Project BRAIN** system.

## Project Structure

```
genesis/
├── .claude/
│   └── skills/
│       ├── brain/           ← Main router (entry point for all BRAIN commands)
│       ├── brain-init/      ← One-time project setup
│       ├── brain-ops/       ← Daily operations (checkpoints, handoffs, hygiene)
│       └── brain-memory/    ← Persistent learning (v1.1)
├── docs/
│   ├── ROADMAP.md           ← v1.0 → v2.0 timeline
│   ├── CONTRIBUTING.md      ← How to create skills
│   └── SKILL_DIRECTORY.md   ← All skills documented
├── README.md                ← User-facing intro
├── CLAUDE.md                ← This file
├── LICENSE                  ← MIT
└── .gitignore
```

## v1.0 Goals

- ✅ **brain** — Smart router for all BRAIN commands
- ✅ **brain-init** — One-time project setup (BRAIN/ directory structure)
- ✅ **brain-ops** — Daily operations: checkpoints, handoffs, hygiene, consolidation
- 🔄 **brain-memory** — Persistent learning across sessions (v1.1)

## How Skills Work

Each skill lives in `.claude/skills/<name>/` and contains a `SKILL.md` with YAML frontmatter. Claude Code reads the frontmatter description to decide when to activate the skill.

The `brain` skill acts as the main entry point — it routes all `brain ...` phrases to the right sub-skill.

## Development Workflow

1. **Create skill** — Add to `.claude/skills/[name]/`
2. **Test locally** — Use in Claude Code session
3. **Document** — Add SKILL.md with proper frontmatter
4. **Commit** — Clear, descriptive messages
5. **Release** — Tag version, update ROADMAP

## Skill Format

```yaml
---
name: my-skill
description: >
  One-line description Claude uses to trigger this skill.
metadata:
  short-description: "Brief summary"
  category: "workflow"
  tags: ["tag1", "tag2"]
---

# my-skill — Title

## What it does
...
```

## Key Principles

- **Quality** — Production-tested before release
- **Focus** — One skill, one responsibility
- **Composable** — Skills work together seamlessly
- **Transparent** — System patterns visible to users
- **Evolvable** — Grows with real-world feedback

## Timeline

- **v1.0** (June 2026) — brain-* system: router, init, ops
- **v1.1** (July 2026) — brain-memory + research patterns
- **v1.2** (August 2026) — Performance optimization
- **v2.0** (Q3 2026) — Enterprise features

## Team

- **Creator:** themattwick
- **Contributors:** Community-driven

## Links

- GitHub: https://github.com/themattwick/claude-code-genesis
- Issues: https://github.com/themattwick/claude-code-genesis/issues
- Discussions: https://github.com/themattwick/claude-code-genesis/discussions
