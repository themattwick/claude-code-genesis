# brain-ops — Quick Reference

## Most common uses

**During long work (every 60-90 min):**
"Create a checkpoint for what I just did"

**Before switching to the other model:**
"Prepare a proper handoff for Claude/Grok tomorrow morning, including final report"

**After messy debugging or exploration:**
"Help me turn the last 2 hours of work into good decisions/ and bugs/ entries"

**At the end of a big session:**
"Generate a FINAL_*_REPORT + updated handoff based on all the checkpoints and memory entries"

**Health check:**
"Run a brain hygiene check on the current project"

## Good entry naming conventions
- `2026-05-27-overload-id-scheme.md`
- `2026-05-27-hard-cases-26-05.md`
- `2026-05-27-baseline-metrics.md`
- `2026-05-27-0430-night-phase-1-complete.md`

Always use ISO date + descriptive kebab-case.

## Recommended rhythm in long sessions
1. Start → read recent memory/ files
2. Every 60-90 min → create checkpoint via this skill
3. After big insight or decision → create proper entry in decisions/ or bugs/
4. Before ending session → ask this skill to prepare handoff + report

## Integration with brain-init
- Use `brain init` / `brain setup` (or call `brain-init`) once when starting a new serious project.
- Use `brain-ops` (via the `brain` router) continuously during all subsequent work on that project.

This skill is meant to be in your DAILY set for any project where continuity and cross-model knowledge transfer matter.
