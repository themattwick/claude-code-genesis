# Checkpoint — Auth middleware wired into the request pipeline

**Time:** 2026-06-10 14:20
**Focus:** JWT auth for the TaskFlow API

## Completed since last checkpoint
- Added `authMiddleware` in `src/middleware/auth.ts`, validates `Authorization: Bearer <jwt>`
- Wired it into the router before all `/tasks/*` routes (`src/router.ts:34`)
- Public routes (`/health`, `/auth/login`) explicitly bypass it via an allowlist
- 6 unit tests passing (`tests/auth.test.ts`)

## Key artifacts / numbers
- Token TTL set to 15 min access + 7 day refresh (see `decisions/2026-06-10-jwt-vs-sessions.md`)
- Middleware adds ~0.4ms p50 overhead per request (acceptable)

## Open questions / next steps
- Refresh-token rotation not implemented yet — tracked, not blocking
- Need to decide where to store the refresh token (httpOnly cookie vs body)

## Memory entries touched
- `decisions/2026-06-10-jwt-vs-sessions.md`
