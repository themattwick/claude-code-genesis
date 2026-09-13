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
| An external fact worth remembering (repo location, API/vendor note) | `reference/` entry | write |
| A spec/worksheet exists but isn't a settled decision yet | `specs/` entry | write |
| A task or phase just completed | checkpoint | write |
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
| `templates/entries/glossary-term.md` | Domain term definitions |
| `templates/QUICK-REFERENCE.md` | Day-to-day cheat sheet |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/create_checkpoint.py` | Timestamped checkpoint with frontmatter |
| `scripts/build_index.py` | Regenerate `BRAIN/INDEX.md` |
| `scripts/brain_hygiene.py` | Deterministic health report (`--days`, `--strict`) |
| `scripts/precompact_checkpoint.py` | **Hook `PreCompact`** — writes the deterministic half of a checkpoint before compaction |
| `scripts/sessionstart_finish_checkpoint.py` | **Hook `SessionStart` (matcher `compact`)** — asks the model to finish it |
| `scripts/test_hooks.py` | **Proof the hooks work.** Exit 1 if anything fails |

### The compaction hook pair

The capture trigger *"context is filling up / before compaction"* above had nothing
firing it. Auto-compaction does not announce itself, so nobody remembers in time.
Two hooks cover it, in **two layers that are deliberately separate**:

| Layer | Who produces it | Reliable |
|---|---|---|
| skeleton: verbatim user requests, files touched, commands run, git state | the `PreCompact` script | **always** |
| judgement: what was settled, what is open, what must not be undone | the model, after compaction | best effort |

⚠️ **A hook cannot invoke a skill, and cannot make the model write anything.** It is a
shell command, not a conversational turn. So layer 2 is a *request*, injected by the
second hook — and layer 1 is built to be worth having on its own when that request is
ignored.

⚠️ **`PreCompact` stdout never reaches the model.** Only `SessionStart`,
`UserPromptSubmit`, `UserPromptExpansion` and `PostModelSwitch` inject context. Asking
the model for anything from `PreCompact` fails *silently*: the hook runs, exits 0, and
the message goes nowhere. Hence `SessionStart` with matcher `compact`, which fires right
*after* compaction — with the side benefit that the model then has a fresh summary in
front of it.

⚠️ **Neither script may call `os.getcwd()`.** The hooks are registered globally, so they
fire in every project on the machine, and the process working directory is wherever the
shell happens to stand — not the session's project. With `os.getcwd()` in the lookup
chain, a session in project A wrote its checkpoint into project B's `BRAIN/`. The only
admissible sources are `CLAUDE_PROJECT_DIR` and the `cwd` handed in on stdin. No `BRAIN/`
there means **do nothing** — that is the correct outcome, not a reason to look elsewhere.

Both hooks exit 0 whatever happens: one that breaks a session gets switched off after the
first time and then saves nothing ever again. `SessionStart` stays **silent** when no
skeleton is waiting, because noise is the surest way to make a control stop being read.

**Because both always exit 0, the exit code proves nothing.** `test_hooks.py` checks the
effect instead: whether a file appeared, *which project* it appeared in, what it contains,
and that a second compaction does not overwrite the first. It found two bugs that way.

It missed a third, and how it missed it is worth keeping. On a real compaction the
checkpoint came out with **0 files and 0 user requests** while the transcript sat right
there: `sys.stdin.read()` decodes with the system code page on Windows, so a session
path holding any non-ASCII character turned into mojibake and the file "did not exist".

The test could not see it for two reasons, and **both had to be fixed**:

- it built its own transcript under an **ASCII path**, and
- `json.dumps` defaults to `ensure_ascii=True`, so the bytes it fed to the hook were
  pure ASCII — every decoder reads those correctly, and the case passed even with the
  bug deliberately reinstated.

⚠️ **A test that has never failed proves nothing.** Case D was only trusted after the
bug was put back and it actually went red. Do the same to any case you add here.

### Installing them

`install-global.ps1` at the root of this repo links every `brain*` skill into
`~/.claude/skills` as a junction and registers both hooks. Linking, not copying: one copy
of the skill, in this git working tree, available in every project, updated everywhere by
`git pull`.

⚠️ **The hooks hold absolute paths into this clone.** Move or rename the clone and they
break — while still firing and still exiting 0, so nothing appears to fail. Re-run the
installer after any move, then `test_hooks.py`.

Entries carry a small optional frontmatter block (`type`, `status`, `tags`,
`links`, `supersedes`) — see `docs/FRONTMATTER.md`. Every tool degrades gracefully
for entries without it.

## Related Skills

- `brain` — Router / entry point (recommended daily interface)
- `brain-init` — One-time project setup
- `brain-memory` — Persistent learning (v1.1)
