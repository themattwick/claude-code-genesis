---
name: brain-ops
description: >
  Operational engine of Project BRAIN (Claude side). The active companion to the `brain` router.
  Handles checkpoints, handoffs, hygiene and knowledge capture. The preferred interface
  is the unified `brain` router skill. This engine can be called directly when needed.
metadata:
  short-description: "BRAIN ops engine (Claude). Preferred via 'brain ...' router."
  category: "workflow"
  tags: ["brain", "project-brain", "checkpoints", "cross-model", "hygiene"]
---

# brain-ops — BRAIN Operations Engine (Claude side)

This is the Claude Code version of the operations engine.

**Strong recommendation:** Use the `brain` router skill:
- "brain checkpoint ..."
- "brain handoff for Grok ..."
- "brain hygiene check on C:\CLAUDE\BRAIN"

It serves the same purpose as the Grok version:
- Maintain checkpoint discipline (60-90 min)
- Turn raw work into proper entries in `BRAIN/decisions/`, `bugs/`, `learnings/`, `patterns/`
- Prepare high-quality handoffs for Grok
- Keep the Project BRAIN healthy

See the main documentation:
`C:\Users\MaxOFFe\.grok\skills\brain-ops\SKILL.md`

Templates are available here for direct Claude use. The canonical location for the Project BRAIN of this monorepo is always `C:\CLAUDE\BRAIN/`.
