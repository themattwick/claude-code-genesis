# Files — templates, scripts, frontmatter notes

_Lookup tables for brain-ops. Read when you need a template or script by name; the
operations in `SKILL.md` already name the ones they use._

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

Checkpoint, handoff and learning/pattern templates adapt ideas from the ECC library
(affaan-m/ECC, MIT) — see each template's header comment.

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

How nested-collection indexing, the compaction hook pair and the global installer work
is in `internals.md`.

## Frontmatter

Entries carry a small optional frontmatter block (`type`, `status`, `tags`, `links`,
`supersedes`). Every tool degrades gracefully for entries without it.

Learnings and patterns may also carry `confidence` (tentative | confirmed), `scope`
(project | global) and `projects`; confirmed in 2+ projects makes an entry promotable to
global. Full reference: `docs/FRONTMATTER.md`.
