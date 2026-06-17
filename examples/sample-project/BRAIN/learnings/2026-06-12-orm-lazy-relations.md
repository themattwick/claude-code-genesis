# Learning — Lazy ORM relations are an N+1 trap in list endpoints

**Date:** 2026-06-12
**Extracted from:** `bugs/2026-06-11-task-list-n-plus-1.md`

## Insight
Any time a serializer or `.map()` touches a lazy relation inside a loop over a
list result, you've created an N+1. It's invisible in unit tests (which use 1-2
rows) and only shows up under realistic data volumes.

## Rule of thumb
- **List endpoints** → eager-load (`include` / `JOIN`) every relation the
  serializer touches.
- **Detail endpoints** → lazy is fine; you're loading one row.
- Add a test that asserts a **query-count ceiling** for list paths, not just the
  response shape. That's what catches the regression.

## Where this applies in TaskFlow
- `GET /tasks` (fixed)
- `GET /projects` will have the same shape once it lists members — pre-empt it.
