# Internals — nested collections, compaction hooks, installing

_Background for maintaining brain-ops. Not needed to run any operation._

### Nested collections, and material that is not an entry

Entries are collected **recursively**, so a folder holding a nested collection — a
wayfinder map with its tickets, a spec with its research notes — is indexed like any
other. Each collection renders as its own subsection rather than as loose rows, so a
map with twenty tickets stays readable instead of flooding the table for its type.

⚠️ **The first version globbed one level deep.** A nested collection was indexed as
**zero** entries and nothing said so. Measured on a real base: 136 files, 64 indexed,
72 invisible — and the printed count looked plausible, so the gap survived every run
since the first. An index that silently omits half a folder is worse than no index.

Not everything under `BRAIN/` is an entry, though. Sample output, prototypes and
imported documents live there as **evidence attached to an entry**. Drop a
`.not-brain-entries` file in such a directory and every tool skips it, and everything
below it:

```
BRAIN/specs/my-map/prototype/WYNIK.md          <- an entry: the conclusion
BRAIN/specs/my-map/prototype/bundle/           <- material
BRAIN/specs/my-map/prototype/bundle/.not-brain-entries
```

**Why a marker and not a name pattern or a type allowlist.** A pattern like
`prototype*` stops working the day someone names a directory differently, and skipping
unknown *types* would also silence the case the check exists for — a real entry with a
typo in its type. A marker is visible when you open the directory and says what it
means. Measured: 47 prototype files written in a different format produced **50 MEDIUM
false positives**; with markers the same base reports 4 findings, all genuine.

⚠️ **Keep entries and material at different levels.** Where a conclusion file sat
beside the sample it described, the marker could not separate them — the material had
to move into its own subdirectory first.

### The compaction hook pair

The capture trigger *"context is filling up / before compaction"* above had nothing
firing it. Auto-compaction does not announce itself, so nobody remembers in time.
Two hooks cover it, in **two layers that are deliberately separate**:

| Layer | Who produces it | Reliable |
|---|---|---|
| skeleton: verbatim user requests, files touched, commands run, git state | the `PreCompact` script | **always** |
| judgement: what was settled, what is open, what must not be undone | the model, after compaction | best effort |

⚠️ **A hook cannot invoke a skill, and cannot make the model write anything.** It is a
shell command, not a conversational turn. So layer 2 is a *request*, injected by the
second hook — and layer 1 is built to be worth having on its own when that request is
ignored.

⚠️ **`PreCompact` stdout never reaches the model.** Only `SessionStart`,
`UserPromptSubmit`, `UserPromptExpansion` and `PostModelSwitch` inject context. Asking
the model for anything from `PreCompact` fails *silently*: the hook runs, exits 0, and
the message goes nowhere. Hence `SessionStart` with matcher `compact`, which fires right
*after* compaction — with the side benefit that the model then has a fresh summary in
front of it.

⚠️ **Neither script may call `os.getcwd()`.** The hooks are registered globally, so they
fire in every project on the machine, and the process working directory is wherever the
shell happens to stand — not the session's project. With `os.getcwd()` in the lookup
chain, a session in project A wrote its checkpoint into project B's `BRAIN/`. The only
admissible sources are `CLAUDE_PROJECT_DIR` and the `cwd` handed in on stdin. No `BRAIN/`
there means **do nothing** — that is the correct outcome, not a reason to look elsewhere.

Both hooks exit 0 whatever happens: one that breaks a session gets switched off after the
first time and then saves nothing ever again. `SessionStart` stays **silent** when no
skeleton is waiting, because noise is the surest way to make a control stop being read.

**Because both always exit 0, the exit code proves nothing.** `test_hooks.py` checks the
effect instead: whether a file appeared, *which project* it appeared in, what it contains,
and that a second compaction does not overwrite the first. It found two bugs that way.

It missed a third, and how it missed it is worth keeping. On a real compaction the
checkpoint came out with **0 files and 0 user requests** while the transcript sat right
there: `sys.stdin.read()` decodes with the system code page on Windows, so a session
path holding any non-ASCII character turned into mojibake and the file "did not exist".

The test could not see it for two reasons, and **both had to be fixed**:

- it built its own transcript under an **ASCII path**, and
- `json.dumps` defaults to `ensure_ascii=True`, so the bytes it fed to the hook were
  pure ASCII — every decoder reads those correctly, and the case passed even with the
  bug deliberately reinstated.

⚠️ **A test that has never failed proves nothing.** Case D was only trusted after the
bug was put back and it actually went red. Do the same to any case you add here.

### Installing them

`install-global.ps1` at the root of this repo links every `brain*` skill into
`~/.claude/skills` as a junction and registers both hooks. Linking, not copying: one copy
of the skill, in this git working tree, available in every project, updated everywhere by
`git pull`.

⚠️ **The hooks hold absolute paths into this clone.** Move or rename the clone and they
break — while still firing and still exiting 0, so nothing appears to fail. Re-run the
installer after any move, then `test_hooks.py`.
