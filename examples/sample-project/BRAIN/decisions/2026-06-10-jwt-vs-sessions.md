# Decision — JWT access/refresh tokens over server-side sessions

**Date:** 2026-06-10
**Status:** Accepted
**Context:** TaskFlow API auth — needs to support a web client and a future CLI

## Options considered

### A. Server-side sessions (cookie + session store)
- ✅ Trivial revocation (delete the session row)
- ✅ Simple mental model
- ❌ Requires a shared session store (Redis) — extra infra for a small service
- ❌ Awkward for the planned CLI client (no cookie jar)

### B. JWT access + refresh tokens  ← chosen
- ✅ Stateless — no session store needed for the access path
- ✅ Works cleanly for both web and CLI clients
- ❌ Revocation is harder — mitigated by a short 15-min access TTL
- ❌ Refresh tokens still need storage (small table, not per-request)

## Decision
Go with **B**. Short-lived access tokens (15 min) keep the revocation window
small without infra overhead. Refresh tokens (7 days) live in a single DB table
and support rotation later.

## Consequences
- Need refresh-token rotation before we expose this publicly (tracked)
- `authMiddleware` stays stateless and cheap (~0.4ms, see checkpoint 2026-06-10-1420)

## Related
- `checkpoints/2026-06-10-1420-auth-middleware-wired.md`
