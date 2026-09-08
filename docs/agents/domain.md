# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

This repo does **not** use a root `CONTEXT.md` or `docs/adr/`. It already has a
knowledge base — `BRAIN/` — and domain docs live there instead, using the same
entries-with-frontmatter model as everything else in it. See
[`../BRAIN.md`](../BRAIN.md) and [`../FRONTMATTER.md`](../FRONTMATTER.md) for
the full model; this file is the short version skills need.

## Before exploring, read these

- **`BRAIN/glossary/`** — one file per domain term, instead of a single `CONTEXT.md`.
  Read the **active** ones relevant to the topic (check each file's frontmatter for
  `status: active`; skip `superseded`/`archived`). `BRAIN/INDEX.md`'s "Glossary
  terms" section lists them all without opening every file.
- **`BRAIN/decisions/`** — this is where architectural decisions live, instead of
  `docs/adr/`. Read the active ones that touch the area you're about to work in.
  `BRAIN/INDEX.md`'s "Decisions" section lists them.

If `BRAIN/INDEX.md` looks stale or missing, regenerate it first:
`python .claude/skills/brain-ops/scripts/build_index.py .`

If any of these are empty, **proceed silently**. Don't flag their absence; don't
suggest creating them upfront. Terms and decisions get written when they're
actually resolved, via `brain define` / `brain consolidate` — see
`.claude/skills/brain-ops/SKILL.md`.

## File structure

```
BRAIN/
├── INDEX.md              ← generated overview of everything below
├── glossary/              ← domain terms (one file per term) — the CONTEXT.md equivalent
│   └── 2026-06-13-wayfinder.md
└── decisions/             ← architectural decisions — the docs/adr/ equivalent
    └── 2026-06-10-jwt-vs-sessions.md
```

Single-context only: this repo has no monorepo signals, so there is one
`BRAIN/` at the root, not a per-package split.

## A term or decision's meaning changes — supersede, don't edit in place

Both glossary terms and decisions follow BRAIN's lifecycle: a redefinition is a
**new file** with `supersedes: <old-file>`, and the old file gets
`status: superseded`. Never edit an old entry to reflect a new meaning — the
history of how it changed is worth keeping. `brain hygiene` flags it if a
superseded entry is still marked active, or if a `supersedes` link points at a
missing file.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal,
a hypothesis, a test name), use the term as defined in its **active**
`BRAIN/glossary/` entry. Don't drift to a synonym the entry explicitly avoids
(see its `Do not use` field).

If the concept you need isn't in the glossary yet, that's a signal: either
you're inventing language the project doesn't use (reconsider), or there's a
real gap — write it with `brain define <term>`.

## Flag decision conflicts

If your output contradicts an existing active decision in `BRAIN/decisions/`,
surface it explicitly rather than silently overriding:

> _Contradicts the JWT-vs-sessions decision (2026-06-10), but worth reopening because…_
