---
name: brain-init
description: >
  One-time initialization of Project BRAIN.
  Creates the full BRAIN/ directory structure, README, QUICK-REFERENCE,
  ready-to-paste sections for AGENTS.md / CLAUDE.md, and starter hooks.
  Use this when starting a new serious project that needs long-term cross-model knowledge.
  Recommended invocation: "brain init" or "brain setup".
metadata:
  short-description: "Bootstrap / initialize Project BRAIN (one-time setup)"
  category: "workflow"
  tags: ["brain", "project-brain", "setup", "init", "bootstrap"]
---

# brain-init — Project BRAIN Bootstrap / Setup

Performs the **one-time setup** of Project BRAIN for a new project.

## Usage

- "brain init"
- "brain setup"
- "brain bootstrap"

## What It Creates

```
BRAIN/
├── README.md              # Project BRAIN overview
├── QUICK-REFERENCE.md     # Cheat sheet for daily use
├── checkpoints/           # Progress snapshots
├── sessions/              # Session summaries
├── decisions/             # Key decisions made
├── bugs/                  # Hard cases encountered
├── learnings/             # Extracted insights
├── patterns/              # Reusable patterns
└── handoffs/              # Cross-model transfer docs
```

## Related Skills

- `brain` — Router/entry point (recommended daily interface)
- `brain-ops` — Daily operations after setup is complete
