# hygiene — full procedure

_Loaded on demand from `SKILL.md`._


Trigger: `brain hygiene`, before a handoff, or periodically.

1. Run `python .claude/skills/brain-ops/scripts/brain_hygiene.py <project-root>`
   (optional `--days N` to change the staleness threshold).
2. Present the report as-is.
3. Offer fixes in the order it suggests: HIGH findings first (broken links,
   lifecycle inconsistencies), then consolidate stale checkpoints, then reindex.

Do not hand-improvise the checks — the script is their definition, so the same
knowledge base always yields the same findings.

Content checks, on active entries only (retired ones are history; a hook-written
`status: skeleton` checkpoint is waiting for the model and is skipped):

- `empty-checkpoint` — nothing under any heading. Only a title.
- `checkpoint-incomplete` — `Left off` or `Next steps` present but empty.
- `learning-incomplete` — a learning/pattern without a rule or a recognition signal.
- `removal-incomplete` — a `removed/` entry missing any of its four fields.
- `possible-duplicate` — a **heuristic** over titles and tags. It suggests; a real
  duplicate is the same root cause, and the fix is an example added to the older entry.

Checkpoints written before the mandatory-field schema are judged only on whether they
say anything at all. With `--strict`, any finding exits 1.
