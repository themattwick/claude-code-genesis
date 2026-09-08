---
name: brain-ops
description: >
  Operational engine of Project BRAIN: writing checkpoints, preparing cross-model
  handoffs, consolidating raw notes into durable knowledge, retiring stale entries,
  and running hygiene checks.
  Use when the user says "brain checkpoint", "brain handoff", "brain hygiene",
  "brain consolidate", "brain organize", "brain report" or "brain index" — and also
  at natural capture points: a hard bug was just solved, a decision was made between
  alternatives, context is filling up, or work is about to move to another model.
metadata:
  short-description: "BRAIN ops engine: capture, consolidate, retire, verify"
  category: "workflow"
  tags: ["brain", "project-brain", "checkpoints", "cross-model", "hygiene"]
---

# brain-ops — BRAIN Operations Engine

Turns work into durable, retrievable knowledge — and retires it when it goes stale.
Every operation below has preconditions, steps, and a defined output. Follow them
rather than improvising, so results are repeatable across sessions and models.

## Capture triggers

Capture is most valuable at the moment information is fresh and about to be lost.
Act at these points without waiting to be asked:

| Situation | Action | Write or ask |
|---|---|---|
| A hard bug was just solved | `bugs/` entry | draft, then confirm |
| Chose X over Y, with a real trade-off | `decisions/` entry | draft, then confirm |
| Surprising or non-obvious discovery | `learnings/` entry | draft, then confirm |
| An external fact worth remembering (repo location, API/vendor note) | `reference/` entry | write |
| A spec/worksheet exists but isn't a settled decision yet | `specs/` entry | write |
| A task or phase just completed | checkpoint | write |
| About to do something risky (migration, large refactor, reset) | checkpoint first | write |
| Context is filling up / before compaction | checkpoint | write |
| End of session, or handing to another model | handoff | write |
| Many active checkpoints, or hygiene flags stale ones | consolidate | propose |

## Write or ask

Writing is cheap and reversible — it is a file in git the user can delete. Asking
costs their attention. So the two are not symmetric:

- **Checkpoints, handoffs, session reports: just write them.** Report the path in
  one line afterwards. Do not ask for permission first.
- **Decisions, bugs, learnings: draft the entry, then confirm in one line.** These
  encode judgement, so a beat is worth it — but show the draft, don't ask whether
  you may write one.

Anti-nag rules, which matter as much as the triggers:

- Never interrupt mid-task. Act on a natural boundary, once something is finished.
- One line, not a paragraph.
- Never propose the same entry twice. If the user declines a category, drop that
  category for the rest of the session.
- Batch related proposals into a single message.

## Before any operation

`BRAIN/` must exist. If it does not, say so, point to `brain init`, and stop —
do not create the structure by hand here; that is `brain-init`'s job.

## Operations

### checkpoint

Trigger: `brain checkpoint [description]`, or a capture trigger above.

1. Run `python .claude/skills/brain-ops/scripts/create_checkpoint.py "<short title>"`
   — it writes a timestamped file with frontmatter and the section skeleton.
2. Fill the sections with concrete facts: file paths with line numbers, test counts,
   measured numbers. Not prose.
3. Keep it to a few minutes of writing. This is continuity, not a report.
4. Regenerate the index (see below).

Output: the path written, in one line. Shape reference: `templates/checkpoint-template.md`.

### handoff

Trigger: `brain handoff`, end of session, or switching models.

1. Start from `BRAIN/INDEX.md` for current state (regenerate it first if stale).
2. Read the most recent checkpoints plus any decisions and bugs touched this session.
3. Fill `templates/handoff-template.md`.
4. Save as `BRAIN/handoffs/YYYY-MM-DD-<from>-to-<to>.md` with frontmatter
   (`type: handoff`, `status: active`, `date`, `tags`).
5. Regenerate the index.

Quality bar: the receiving model must be productive within ~10 minutes without
re-discovering context. Use concrete paths and line numbers, and make the
"first 3 moves" section specific enough to act on immediately.

### consolidate

Trigger: `brain consolidate` or `brain organize`, or when hygiene reports stale
checkpoints.

This is the step that keeps `BRAIN/` from drowning: it turns raw material into
durable knowledge **and retires the source**. Both halves are required.

1. Select sources: active checkpoints and sessions older than ~14 days, or
   everything since the last consolidation.
2. Synthesize into durable entries under `decisions/`, `bugs/`, `learnings/` or
   `patterns/`. Give each frontmatter with `tags` and `links:` back to its sources.
   For bug write-ups use `templates/entries/bug-hard-case.md`.
3. **Retire the sources**: set `status: archived` on every checkpoint you consolidated.
   Never delete — history stays, it just leaves the active set.
4. If a new entry replaces an existing durable one, set `supersedes: <old-file>` on
   the new entry and `status: superseded` on the old one.
5. Regenerate the index.
6. Verify with `brain hygiene` — it should report no lifecycle inconsistencies.

Output: what was created and what was archived, with counts and paths.

### hygiene

Trigger: `brain hygiene`, before a handoff, or periodically.

1. Run `python .claude/skills/brain-ops/scripts/brain_hygiene.py <project-root>`
   (optional `--days N` to change the staleness threshold).
2. Present the report as-is.
3. Offer fixes in the order it suggests: HIGH findings first (broken links,
   lifecycle inconsistencies), then consolidate stale checkpoints, then reindex.

Do not hand-improvise the checks — the script is their definition, so the same
knowledge base always yields the same findings.

### report

Trigger: `brain report`.

Summarize the session from its checkpoints — what shipped, key numbers, open
threads — into `BRAIN/sessions/YYYY-MM-DD-<slug>.md` with `type: session`
frontmatter. Then regenerate the index.

### index

Trigger: `brain index` or `brain reindex`.

```bash
python .claude/skills/brain-ops/scripts/build_index.py <project-root>
```

**Run this after any entry is written, retired, or edited.** Otherwise
`BRAIN/INDEX.md` goes stale and `brain load` reports the wrong current state.

## Templates

| Template | Use for |
|---|---|
| `templates/checkpoint-template.md` | Shape of a checkpoint |
| `templates/handoff-template.md` | Cross-model handoff document |
| `templates/entries/bug-hard-case.md` | Hard bug write-ups during consolidation |
| `templates/QUICK-REFERENCE.md` | Day-to-day cheat sheet |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/create_checkpoint.py` | Timestamped checkpoint with frontmatter |
| `scripts/build_index.py` | Regenerate `BRAIN/INDEX.md` |
| `scripts/brain_hygiene.py` | Deterministic health report (`--days`, `--strict`) |

Entries carry a small optional frontmatter block (`type`, `status`, `tags`,
`links`, `supersedes`) — see `docs/FRONTMATTER.md`. Every tool degrades gracefully
for entries without it.

## Related Skills

- `brain` — Router / entry point (recommended daily interface)
- `brain-init` — One-time project setup
- `brain-memory` — Persistent learning (v1.1)
