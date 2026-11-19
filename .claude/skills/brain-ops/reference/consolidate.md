# consolidate — full procedure

_Loaded on demand from `SKILL.md`. Run it only for `brain consolidate` / `brain organize`._

Trigger: `brain consolidate` or `brain organize`, or when hygiene reports stale
checkpoints.

This is the step that keeps `BRAIN/` from drowning: it turns raw material into
durable knowledge **and retires the source**. Both halves are required.

## 1. Build the source list — and show it before writing anything

Step 2 is the part that looks like the job, so step 1 tends to get done in passing.
Guard against that by making step 1 produce something you can be checked against.
**Do not start step 2 until this table exists in your reply:**

| Source (path) | Age | What it says (one line) | Becomes | Same root cause already in BRAIN? |
|---|---|---|---|---|

- Sources: active checkpoints and sessions older than ~14 days, or everything since the
  last consolidation. Open and read each one; the "what it says" column cannot be
  filled from a filename.
- "Becomes": `decision`, `bug`, `learning`, `pattern`, or `nothing — superseded by
  <path>`. A source that yields nothing durable is still retired in step 3.
- Last column: search `learnings/`, `patterns/` and `bugs/` for an active entry with the
  same root cause (grep the title words and tags). Same cause, different symptom →
  add a line to *Examples* of the existing entry instead of writing a new one. Write the
  path found, or `none — searched <terms>`. An empty cell is not allowed.

## 2. Synthesize

Write durable entries under `decisions/`, `bugs/`, `learnings/` or `patterns/`. Give each
frontmatter with `tags` and `links:` back to its sources.

- learnings and patterns: `../templates/entries/learning-pattern.md` — 4–8 sentences, a
  title that names the pattern rather than the event, and the three required parts: root
  cause, a portable rule ("Next time [situation], I will [action]"), a recognition signal.
- decisions: `../templates/entries/decision.md` — every real alternative with its cost,
  plus the consequences.
- bugs: `../templates/entries/bug-hard-case.md`.

## 3. Retire the sources

Set `status: archived` on every checkpoint or session you consolidated. Never delete —
history stays, it just leaves the active set.

## 4. Supersede, where an entry replaces another

If a new entry replaces an existing durable one, set `supersedes: <old-file>` on the new
entry and `status: superseded` on the old one.

## 5. Regenerate the index, then verify

Run `brain index`, then `brain hygiene` — it should report no lifecycle inconsistencies,
no `empty-checkpoint`, and no `learning-incomplete` for what you just wrote.

**Output:** what was created and what was retired, with counts and paths.
