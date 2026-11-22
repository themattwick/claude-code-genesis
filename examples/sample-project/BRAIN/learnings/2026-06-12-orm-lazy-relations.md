---
type: learning
status: active
date: 2026-06-12
tags: [orm, performance, testing]
confidence: confirmed
scope: project
projects: [taskflow]
links: [bugs/2026-06-11-task-list-n-plus-1.md, patterns/2026-06-13-query-count-ceiling.md]
---

# Learning — Lazy ORM relations are an N+1 trap in list endpoints

**Date:** 2026-06-12
**Extracted from:** `bugs/2026-06-11-task-list-n-plus-1.md`

## Insight
Any time a serializer or `.map()` touches a lazy relation inside a loop over a
list result, you've created an N+1. It's invisible in unit tests (which use 1-2
rows) and only shows up under realistic data volumes.

## Rule
Next time I add or change a list endpoint, I will eager-load every relation its
serializer touches and add a query-count ceiling test for it.

## Rule of thumb
- **List endpoints** → eager-load (`include` / `JOIN`) every relation the
  serializer touches.
- **Detail endpoints** → lazy is fine; you're loading one row.
- Add a test that asserts a **query-count ceiling** for list paths, not just the
  response shape. That's what catches the regression.

## Recognition signal
The number of queries grows with the number of rows returned: in TaskFlow, 50 tasks
produced 51 queries. The endpoint passes its unit tests and is only slow on realistic data.

## Where this applies in TaskFlow
- `GET /tasks` (fixed)
- `GET /projects` will have the same shape once it lists members — pre-empt it.
