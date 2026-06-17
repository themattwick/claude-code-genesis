---
type: checkpoint
status: active
date: 2026-06-11
tags: [tasks, performance]
---

# Checkpoint — Task filtering endpoint + spotted an N+1

**Time:** 2026-06-11 09:30
**Focus:** `GET /tasks` with filters (status, assignee, due date)

## Completed since last checkpoint
- Implemented query builder for `GET /tasks?status=&assignee=&due_before=`
- Pagination via `limit`/`offset`, capped at 100 per page
- Integration tests cover the 3 filter combinations we actually use

## Key artifacts / numbers
- Found an N+1: each task triggered a separate query for its `assignee` — 50 tasks = 51 queries
- Full write-up in `bugs/2026-06-11-task-list-n-plus-1.md`

## Open questions / next steps
- Apply the JOIN fix from the bug entry, then re-run the load test
- Consider a composite index on `(status, due_date)` if filter latency stays high

## Memory entries touched
- `bugs/2026-06-11-task-list-n-plus-1.md`
