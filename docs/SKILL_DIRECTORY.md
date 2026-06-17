# Skill Directory

Complete catalog of all skills in the Genesis hub.

## Core Skills (v1.0)

### brain
**Entry point for Project BRAIN** — Smart router for all BRAIN-related actions.

- Trigger: "brain ...", "brain checkpoint", "brain handoff", "brain load"
- Routes to: `brain-init` (setup) or `brain-ops` (operations)
- Location: `.claude/skills/brain/`

---

### brain-init
**One-time BRAIN setup** — Creates the full `BRAIN/` directory structure.

- Trigger: "brain setup", "brain init", "brain bootstrap"
- Creates: `BRAIN/checkpoints/`, `BRAIN/decisions/`, `BRAIN/bugs/`, `BRAIN/learnings/`, `BRAIN/patterns/`
- Location: `.claude/skills/brain-init/`

---

### brain-ops
**Daily BRAIN operations** — Checkpoints, handoffs, hygiene, consolidation.

- Trigger: "brain checkpoint", "brain handoff", "brain hygiene", "brain consolidate"
- Scripts: `create_checkpoint.py` (timestamped checkpoint files)
- Location: `.claude/skills/brain-ops/`

---

### brain-memory
**Persistent learning** — Cross-session knowledge retention. *(v1.1)*

- Trigger: "brain remember", "brain recall", "brain patterns"
- Status: Stub — full implementation in v1.1
- Location: `.claude/skills/brain-memory/`

---

## See It In Action

[`examples/sample-project/`](../examples/sample-project) shows a healthy `BRAIN/`
after about a week of work — real checkpoints, a decision record, an N+1 bug with
its extracted learning, and a cross-model handoff. The fastest way to understand
how the pieces fit together.

## Roadmap Skills

See [ROADMAP.md](./ROADMAP.md) for planned skills:
- `genesis-research` (v1.1)
- `genesis-tdd` (v1.1)
- `genesis-performance` (v1.2)
