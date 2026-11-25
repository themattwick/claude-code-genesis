# remove — full procedure

_Loaded on demand from `SKILL.md`._


Trigger: something was deliberately taken out, and someone might later put it back.

1. Check `BRAIN/removed/` for an existing active entry about the same thing.
2. Write `BRAIN/removed/YYYY-MM-DD-<slug>.md` from `../templates/entries/removal.md`. All four
   frontmatter fields are required: `removed`, `reason`, `replacement`, `return_if`
   (`return_if: never` is a valid answer; an empty one is not).
3. Regenerate the index — the entry then appears under *Deliberately removed — do not
   restore* at the top of `INDEX.md`.
4. If the thing is later restored, retire the entry (`status: archived`) and record why in a
   `decisions/` entry. Never delete it.

Output: the path written, in one line.
