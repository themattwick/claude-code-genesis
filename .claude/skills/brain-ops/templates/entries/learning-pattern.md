---
type: learning
status: active
date: YYYY-MM-DD
tags: []
confidence: tentative
scope: project
projects: []
---

# [Name the PATTERN, not the event — e.g. "Cache keys must include the tenant", not "Tuesday's outage"]

<!-- Set `type: pattern` instead of `learning` once the rule has paid off repeatedly. -->
<!-- confidence: `tentative` until the rule has held up; then `confirmed`. List each project
     where it was confirmed under `projects`. Confirmed in 2+ projects → set `scope: global`
     (`brain hygiene` reports it as "promotion-due"). -->
<!-- Adapted from the growth-log skill in ECC (affaan-m/ECC), MIT. -->

**Length:** 4–8 sentences in total. If it needs more, it is two entries or a `bugs/` write-up.

## Root cause
[The underlying cause, not the symptom. One or two sentences.]

## Rule
Next time [situation], I will [action].

## Recognition signal
[How you can tell this pattern is at work again — an error message, a metric, a code smell.
Concrete enough to grep for or notice at a glance.]

## Examples
- YYYY-MM-DD — [one line: where it happened, link to `bugs/` or `decisions/` if any]

---
**Before writing — search for a duplicate.** Look in `learnings/` and `patterns/` for an
entry with the **same root cause**. Same cause, different symptom → add a line under
**Examples** of the existing entry; do not create a new one. Only a new root cause earns
a new file.

**Learning or pattern?** A `learning` is one root cause seen once or twice. When the same
rule has paid off repeatedly, promote it to `type: pattern` (edit in place — the rule did
not change, only the evidence grew).
