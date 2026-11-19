---
name: brain-ops
description: >
  Operational engine of Project BRAIN: writing checkpoints, preparing cross-model
  handoffs, consolidating raw notes into durable knowledge, defining domain terms,
  retiring stale entries, and running hygiene checks.
  Use when the user says "brain checkpoint", "brain handoff", "brain hygiene",
  "brain consolidate", "brain organize", "brain report", "brain index", "brain
  define" or "brain glossary" — and also at natural capture points: a hard bug
  was just solved, a decision was made between alternatives, a domain term was
  coined or redefined, context is filling up, or work is about to move to
  another model.
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
| A domain term was coined, clarified, or redefined | `glossary/` entry | draft, then confirm |
| Something was deliberately removed (a feature, a file, a dependency, an approach) | `removed/` entry | draft, then confirm |
| An external fact worth remembering (repo location, API/vendor note) | `reference/` entry | write |
| A spec/worksheet exists but isn't a settled decision yet | `specs/` entry | write |
| A task or phase just completed | checkpoint | write |
| Work changes phase: research → plan, plan → implementation | checkpoint | write |
| An approach just failed and you are switching to another | checkpoint (what was tried, why it failed) | write |
| About to switch to an unrelated topic | checkpoint | write |
| About to do something risky (migration, large refactor, reset) | checkpoint first | write |
| Context is filling up / before compaction | checkpoint | write — **hook-driven**, see Scripts |
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

`BRAIN/` must exist. If it does not, say so, point to `/brain-init`, and stop —
do not create the structure by hand here; that is `brain-init`'s job.

## Operations

### checkpoint

Trigger: `brain checkpoint [description]`, or a capture trigger above.

1. Run `python .claude/skills/brain-ops/scripts/create_checkpoint.py "<short title>"
   --summary "..." --left-off "..." --next "..." --next "..."` — it writes a
   timestamped file with frontmatter and the section skeleton, with the mandatory
   fields already filled. Without `--left-off` and `--next` it warns and leaves the
   sections empty (`--strict` refuses to write at all).
2. Fill the sections with concrete facts: file paths with line numbers, test counts,
   measured numbers. Not prose.
3. **Two fields are mandatory: `Left off` and `Next steps`.** `Left off` names one concrete
   place (file, function or error); `Next steps` is an ordered list. A checkpoint with only
   a title is worse than none — it looks like continuity and carries none. Also fill
   `Summary` (at most 10 words), `Decisions` (what + why) and `Blockers` (or "none").
4. Keep it to a few minutes of writing. This is continuity, not a report.
5. Regenerate the index (see below).

Phase changes and failed attempts are natural checkpoint moments (see the triggers
table) and natural moments to `/compact`. This complements the compaction hooks below;
it does not replace them.

Output: the path written, in one line. Shape reference: `templates/checkpoint-template.md`.

### handoff

Trigger: `brain handoff`, end of session, or switching models.

1. Start from `BRAIN/INDEX.md` for current state (regenerate it first if stale).
2. Read the most recent checkpoints plus any decisions and bugs touched this session.
3. Fill `templates/handoff-template.md`. Sort every claim into **Verified** (with
   evidence: a command and its result, a test count, `file:line`) or **Intended /
   unverified**. If you did not run it or read it this session, it is the second kind,
   however sure you feel — the receiving model must not take a plan for a fact. Add
   source, time of observation and open questions.
4. Save as `BRAIN/handoffs/YYYY-MM-DD-<from>-to-<to>.md` with frontmatter
   (`type: handoff`, `status: active`, `date`, `tags`).
5. Regenerate the index.

Quality bar: the receiving model must be productive within ~10 minutes without
re-discovering context. Use concrete paths and line numbers, and make the
"first 3 moves" section specific enough to act on immediately.

### consolidate

Trigger: `brain consolidate` or `brain organize`, or when hygiene reports stale checkpoints.

Turns raw checkpoints and sessions into durable entries **and retires the sources**. Both halves are required.

**Read `reference/consolidate.md` and follow it.** It is not loaded with this file.

### define

Trigger: `brain define <term>` or `brain glossary`, or a term was coined,
clarified, or redefined during the session.

1. Check whether `BRAIN/glossary/` already has an **active** entry for this term
   (search by title, not just filename — terms drift in phrasing).
2. **New term:** write `BRAIN/glossary/YYYY-MM-DD-<term-slug>.md` from
   `templates/entries/glossary-term.md`.
3. **Redefining an existing term:** do not edit the old entry in place. Write a
   new one with `supersedes: glossary/<old-file>.md`, and set
   `status: superseded` on the old entry. The record of how the term's meaning
   drifted is itself useful.
4. Regenerate the index.

Output: the path written (and, if a redefinition, what changed), in one line.

### remove

Trigger: something was deliberately removed and someone might put it back.

Records something deliberately taken out — why, what replaced it, when it could return — so nobody restores it by accident.

**Read `reference/remove.md` and follow it.** It is not loaded with this file.

### hygiene

Trigger: `brain hygiene`, before a handoff, or periodically.

Runs the deterministic health script and reports its findings as-is.

**Read `reference/hygiene.md` and follow it.** It is not loaded with this file.

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
| `templates/entries/decision.md` | Decisions: options considered (with costs), the choice, consequences |
| `templates/entries/bug-hard-case.md` | Hard bug write-ups during consolidation |
| `templates/entries/learning-pattern.md` | Learnings and patterns: root cause, rule, recognition signal |
| `templates/entries/glossary-term.md` | Domain term definitions |
| `templates/entries/removal.md` | Deliberately removed things: why, replacement, return condition |
| `templates/QUICK-REFERENCE.md` | Day-to-day cheat sheet |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/create_checkpoint.py` | Timestamped checkpoint with frontmatter; `--left-off`/`--next` fill the mandatory fields, `--strict` refuses without them |
| `scripts/build_index.py` | Regenerate `BRAIN/INDEX.md` |
| `scripts/brain_hygiene.py` | Deterministic health report (`--days`, `--strict`) |
| `scripts/precompact_checkpoint.py` | **Hook `PreCompact`** — writes the deterministic half of a checkpoint before compaction |
| `scripts/sessionstart_finish_checkpoint.py` | **Hook `SessionStart` (matcher `compact`)** — asks the model to finish it |
| `scripts/test_hooks.py` | **Proof the hooks work.** Exit 1 if anything fails |
| `scripts/test_index.py` | **Proof the index is complete.** Exit 1 if anything fails |
| `scripts/test_removed.py` | **Proof the removed zone shows and is enforced.** Exit 1 if anything fails |
| `scripts/test_validation.py` | **Proof the content checks bite** (empty checkpoints, diary-style learnings, duplicates, `--strict`). Exit 1 if anything fails |
| `scripts/test_frontmatter.py` | **Proof `confidence`/`scope`/`projects` work** and old entries are untouched. Exit 1 if anything fails |

### Internals

How the nested-collection indexing, the compaction hook pair and the global installer work —
and the lessons behind them — is in `reference/internals.md`. Read it only when changing those.

Learnings and patterns may carry `confidence` (tentative | confirmed), `scope` (project | global)
and `projects`; confirmed in 2+ projects makes an entry promotable to global — see
`docs/FRONTMATTER.md`.

Checkpoint, handoff and learning/pattern templates adapt ideas from the ECC library
(affaan-m/ECC, MIT) — see each template's header comment.

Entries carry a small optional frontmatter block (`type`, `status`, `tags`,
`links`, `supersedes`) — see `docs/FRONTMATTER.md`. Every tool degrades gracefully
for entries without it.

## Related Skills

- `brain` — Router / entry point (recommended daily interface)
- `brain-init` — One-time project setup
- `brain-memory` — Persistent learning (v1.1)
