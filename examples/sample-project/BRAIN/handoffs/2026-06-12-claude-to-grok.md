# HANDOFF — Claude → Grok — 2026-06-12

**Operation / Theme:** TaskFlow API — auth done, list perf fixed, refresh rotation next
**Date & Time of handoff:** 2026-06-12 18:05
**Prepared by:** Claude

## Read this first (recommended order)
1. This handoff (you're here)
2. `decisions/2026-06-10-jwt-vs-sessions.md` — why auth is JWT-based
3. `bugs/2026-06-11-task-list-n-plus-1.md` — the perf fix we just shipped
4. `learnings/2026-06-12-orm-lazy-relations.md` — the generalized rule
5. Recent checkpoints in `checkpoints/` for the day-by-day rhythm

## Current Status
**Working:**
- JWT auth middleware on all `/tasks/*` routes, 6 tests green
- `GET /tasks` with filters + pagination, N+1 fixed (200 tasks ~90ms)

**Blocked / known gaps:**
- Refresh-token **rotation** not implemented — this is the next priority
- No decision yet on refresh-token storage location (httpOnly cookie vs body)

**Baseline numbers captured:**
- Auth middleware overhead ~0.4ms p50
- `GET /tasks` 200 rows ~90ms after the JOIN fix

## Your first 3 moves (priority order)
1. Implement refresh-token rotation in `src/services/authService.ts`. On each
   refresh, invalidate the old token and issue a new pair. Add a `tokenVersion`
   or a `revoked_at` column — your call, but write the reasoning into
   `decisions/`.
2. Resolve the storage question. My lean: **httpOnly + SameSite=Lax cookie** for
   the web client, with the CLI using the body. Capture it as a decision either
   way.
3. Pre-empt the `GET /projects` N+1 before it ships — same shape as the tasks
   bug. See the learning entry.

## Important context for the other model
- **Memory discipline:** every 60-90 min, `brain checkpoint`. Turn any hard
  problem into a `bugs/` entry with file paths + line numbers — that's what made
  this handoff fast to write.
- Naming convention: ISO date + kebab-case (`2026-06-12-short-slug.md`).
- Tests assert **query-count ceilings** for list endpoints — keep that pattern.

## Artifacts ready for you
- Tests to run: `npm test` (12 passing) — start here to confirm a clean baseline
- Decisions waiting for review: none open; you'll be *creating* two (rotation
  strategy + token storage)

---
**Goal of this document:** You should be able to continue productive work within
~10 minutes without re-discovering context. If anything here is stale, fix it and
note it in your first checkpoint.
