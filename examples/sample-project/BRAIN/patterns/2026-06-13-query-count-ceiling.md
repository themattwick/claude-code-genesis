---
type: pattern
status: active
date: 2026-06-13
tags: [testing, performance, orm]
links: [bugs/2026-06-11-task-list-n-plus-1.md, learnings/2026-06-12-orm-lazy-relations.md]
---

# Pattern — Assert a query-count ceiling on list endpoints

Every list endpoint test asserts a maximum number of DB queries. Catches N+1
regressions that response-shape assertions miss entirely.
