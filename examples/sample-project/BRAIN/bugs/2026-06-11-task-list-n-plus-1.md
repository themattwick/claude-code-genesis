---
type: bug
status: active
date: 2026-06-11
tags: [performance, orm]
links: [learnings/2026-06-12-orm-lazy-relations.md]
---

# N+1 query on GET /tasks (assignee lookup)

**Date:** 2026-06-11
**Discovered during:** Task filtering endpoint work
**Severity / Impact:** High — list latency grows linearly with result count

## Problem
`GET /tasks` returned tasks fine, but response time ballooned with larger result
sets. 50 tasks took ~340ms; 200 tasks took ~1.3s.

## Reproduction / Evidence
- File: `src/repositories/taskRepository.ts:88`
- The list query fetched tasks, then the serializer accessed `task.assignee`,
  which lazily fired one `SELECT * FROM users WHERE id = ?` per task.
- Query log showed 1 list query + N assignee queries (the classic N+1).

## Root Cause Analysis
The ORM relation `Task.assignee` is lazy by default. The serializer at
`src/serializers/taskSerializer.ts:21` touches it inside a `.map()`, so each
iteration triggers a round-trip.

## Proposed Fix
Eager-load the relation in the list path only:

```ts
// taskRepository.ts
const tasks = await db.task.findMany({
  where,
  include: { assignee: true },   // single JOIN instead of N lookups
  take: limit,
  skip: offset,
});
```

Keep the detail endpoint lazy — it only ever loads one task.

## Status
- [x] Investigated
- [x] Proposal written
- [x] Implemented
- [x] Test added (`tests/tasks.list.test.ts` asserts ≤2 queries)
- [x] Verified — 200 tasks now ~90ms

## Related artifacts
- `checkpoints/2026-06-11-0930-task-filtering-n-plus-1.md`
- `learnings/2026-06-12-orm-lazy-relations.md`
