# BRAIN Entry Frontmatter

Every BRAIN entry may carry a small YAML frontmatter block. It is **optional** —
entries without it still work (they're indexed by folder + filename) — but adding
it makes entries filterable, gives them a lifecycle, and powers `BRAIN/INDEX.md`.

## The standard

```yaml
---
type: decision          # checkpoint | session | decision | bug | learning | pattern | handoff
status: active          # active | superseded | archived
date: 2026-06-12        # ISO date (YYYY-MM-DD)
tags: [auth, jwt]       # free-form, lowercase
supersedes: 2026-05-01-old-auth.md     # optional — this entry replaces that one
links: [bugs/2026-06-11-n-plus-1.md]   # optional — related entries
---
```

## Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `type` | recommended | Entry category. Falls back to the folder name if omitted. |
| `status` | recommended | Lifecycle state. Defaults to `active`. `superseded`/`archived` move the entry to the "Retired" section of the index, out of the way of current knowledge. |
| `date` | recommended | ISO date. Falls back to the date parsed from the filename. |
| `tags` | optional | Lowercase keywords for filtering and (later) search. |
| `supersedes` | optional | Filename of the entry this one replaces. Pair with `status: superseded` on the old entry. |
| `links` | optional | Related entries, as `folder/filename.md` paths. The basis for the future backlink graph. |

## Lifecycle

Entries move through states rather than being deleted:

- **active** — current, trusted knowledge
- **superseded** — replaced by a newer entry (keep for history; see `supersedes`)
- **archived** — no longer relevant, kept for the record

`status` is how hot/cold separation works **without** moving files into new
folders — the flat directory structure stays portable, and the index does the
sorting.

## Migrating existing entries

You don't have to migrate everything at once. Run the index generator and it will
list entries still missing frontmatter under a "Needs frontmatter" section — a
ready-made TODO list. Add frontmatter as you touch each entry.

See [BRAIN.md](./BRAIN.md) for how this fits the overall architecture.
