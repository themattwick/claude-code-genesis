---
type: pattern
status: active
date: 2026-06-13
tags: [testing, performance, orm]
confidence: tentative
scope: project
projects: [taskflow]
links: [bugs/2026-06-11-task-list-n-plus-1.md, learnings/2026-06-12-orm-lazy-relations.md]
---

# Pattern — Assert a query-count ceiling on list endpoints

Every list endpoint test asserts a maximum number of DB queries. Catches N+1
regressions that response-shape assertions miss entirely.

## Rule
Next time I write a test for a list endpoint, I will assert a maximum query count, not
only the response shape.

## Recognition signal
A list endpoint's tests check only the response body, or its query count rises with
the row count (50 tasks produced 51 queries before the fix).
