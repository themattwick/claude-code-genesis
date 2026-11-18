---
type: handoff
status: active
date: YYYY-MM-DD
tags: []
---

# HANDOFF — [From Model] to [To Model] — [Date]

<!-- Verified/intended split adapted from the unified-memory skill in ECC (affaan-m/ECC), MIT. -->

**Operation / Theme:**  
**Date & Time of handoff:**  
**Prepared by:** [Grok / Claude]  
**Source:** [where this state comes from — checkpoints, a session, a repo at commit abc1234]  
**Observed at:** [YYYY-MM-DD HH:MM — facts below were true then, not necessarily now]

## Read this first (recommended order)
1. Latest file in `BRAIN/handoffs/` (or equivalent session summary)
2. `BRAIN/decisions/` — most important architectural choices
3. `BRAIN/bugs/` — hard cases + concrete proposals
4. `BRAIN/checkpoints/` — recent progress rhythm
5. Key code / test files changed

## Verified (with evidence)
Only what was actually checked. Every line carries its proof.
- [claim] — evidence: [command and result | test count | `file:line`]

## Intended / unverified
Plans, assumptions, things believed but not checked. The receiving model must treat
these as hypotheses and verify before building on them.
- [claim] — why unverified: [not run | from memory | other model's report]

## Current Status
- What is working
- What is blocked / known gaps
- Baseline numbers / metrics captured

## Your first 3 moves (priority order)
1. 
2. 
3. 

## Open questions
- [question] — who can answer it

## Important context for the other model
- [Any special instructions, naming conventions, project-specific rules, memory discipline, etc.]

## Artifacts ready for you
- Tests to run
- Reports to read
- Decisions waiting for review/approval

---
**Goal of this document:** The receiving model should be able to continue productive work within 10 minutes without having to re-discover context.

**The rule that makes it work:** if you did not run it or read it this session, it goes under
*Intended / unverified*, however sure you feel. A plan stated as a fact is how the next model
inherits your mistake.
