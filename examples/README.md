# Examples

Real, worked examples of the BRAIN system in action.

## [sample-project/](./sample-project)

A fictional project — *TaskFlow*, a small task-management API — after about a week
of development with the BRAIN system. It shows what a healthy `BRAIN/` actually
looks like once you've been using `brain checkpoint`, `brain handoff`, and
consolidating decisions:

```
sample-project/BRAIN/
├── checkpoints/   # Mid-session progress snapshots
├── decisions/     # Why we chose X over Y
├── bugs/          # Hard cases and their fixes
├── learnings/     # Extracted insights
└── handoffs/      # A real cross-model handoff (Claude → Grok)
```

Browse the files to get a feel for:
- **Granularity** — how much detail goes in a checkpoint vs a decision
- **Naming** — ISO date + kebab-case slug
- **Cross-references** — entries pointing at each other
- **A handoff** — how one model hands the baton to another with zero context loss

This is the single best way to understand the system. Read `handoffs/` first —
it's written so a fresh model can resume productive work in ~10 minutes.
