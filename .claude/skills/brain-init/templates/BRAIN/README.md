# Project BRAIN (Shared Long-Term Memory)

This directory is the **central long-term memory** for the project. It serves as the main communication layer between different AI sessions and different AI tools (Claude, Grok, etc.).

## Purpose

Native memory systems in AI coding tools do not communicate well with each other. This filesystem-based structured memory solves that problem.

## Directory Structure

- `learnings/` — Important conclusions, lessons learned, and insights from work
- `decisions/` — Architectural decisions and trade-offs with reasoning
- `patterns/` — Recurring good and bad patterns (especially domain-specific)
- `bugs/` — Difficult edge cases and their solutions
- `checkpoints/` — Lightweight mid-session notes during long work
- `sessions/` — Larger session summaries and retrospectives

## Rules

1. Always check this directory at the beginning of significant work.
2. After any meaningful progress, debugging session, or decision — document it here.
3. Use dated, descriptive filenames (e.g. `2026-05-27-scope-detection-overloads.md`).
4. Be specific: include file paths, code examples, and line numbers when relevant.
5. This is the primary shared knowledge base — both Claude and Grok are instructed to use it heavily.

## Integration

This system is designed to work together with:
- DAILY rules (AGENTS.md + CLAUDE.md)
- Strategic workflow practices (regular checkpoints, strategic-compact, /learn)
- Cross-AI communication between Claude Code and Grok Build

See `QUICK-REFERENCE.md` for fast usage guidelines.