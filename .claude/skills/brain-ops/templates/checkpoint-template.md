---
type: checkpoint
status: active
date: YYYY-MM-DD
tags: []
---

# Checkpoint — [Short Title]

<!-- Mandatory-field schema adapted from the ck skill in ECC (affaan-m/ECC), MIT. -->

**Time:** YYYY-MM-DD HH:MM  
**Session / Operation:** [e.g. Auth refactor - Phase 2]  
**Trigger:** [task done | phase change | failed attempt | before risky step | before compaction | topic switch | time]

## Summary
[At most 10 words. What state is the work in?]

## Left off  <!-- mandatory -->
[One concrete place: a file, a function, or an error. `src/auth/session.py:88`, not "the auth code".]

## Next steps  <!-- mandatory, in order -->
1. [first thing to do on return]
2.

## Decisions
| What | Why |
|---|---|
| [choice made] | [the reason — what was the alternative, what tipped it] |

## Blockers
- [what is stopping progress and who/what can unblock it — or "none"]

## Numbers / artifacts
- [tests passing/failing, measured values, files created]

## Memory entries created in this block
- `BRAIN/decisions/....md`

---
**Instructions for the model using this template:**
- `Left off` and `Next steps` must never be empty. A checkpoint that is only a title is
  worse than none — it looks like continuity and carries none.
- Keep it short and factual (5-10 minutes to write). Real file paths and line numbers.
- A failed attempt is worth a checkpoint: write what was tried and why it failed under
  `Decisions`, so it is not retried.
- This is primarily for continuity, not for the final report.
