#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart hook (matcher: compact) - asks for the checkpoint to be finished.

The second half of the mechanism; the first is `precompact_checkpoint.py`.

THE SPLIT AND WHY IT EXISTS. `PreCompact` writes the skeleton, but its stdout does
NOT reach the model - only `SessionStart`, `UserPromptSubmit`, `UserPromptExpansion`
and `PostModelSwitch` inject context (Anthropic documentation). So the request to
finish the job goes out from here: `SessionStart` with matcher `compact` fires right
after compaction, and its stdout is the documented injection route.

A side effect turned out to be an advantage: the model gets the request while a fresh
session summary is in front of it, so it can write the findings better than it would
have mid-interrupted-turn.

WARNING: IT STAYS SILENT WHEN THERE IS NOTHING TO DO. If no skeleton is waiting, the
hook prints nothing. A message on every session start would be noise, and noise is
the surest way to make a control stop being read.

WARNING: IT NEVER INTERRUPTS SESSION START. The exit code is always 0.
"""
import io
import json
import os
import sys
import time

# The Windows console is not UTF-8 by default, and this hook's output goes to
# Claude Code. Without this, non-ASCII characters come out as mojibake.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def read_stdin():
    """WARNING: NOT sys.stdin.read() - see the twin docstring in
    `precompact_checkpoint.py`. On Windows sys.stdin decodes with the system code
    page, so any non-ASCII character in a path handed over by Claude Code turns into
    mojibake and the file "does not exist"."""
    try:
        return sys.stdin.buffer.read().decode("utf-8", "replace")
    except Exception:
        try:
            return sys.stdin.read()
        except Exception:
            return ""


MARKER = "TO BE FILLED IN"
SUFFIX = "-before-compaction.md"
MAX_AGE_DAYS = 3


def safely(f, fallback):
    try:
        return f()
    except Exception:
        return fallback


def find_directory(cwd):
    """Only the project the hook handed us. NEVER os.getcwd() - see the twin comment
    in `precompact_checkpoint.py`. The hook is registered globally, so the process
    working directory can point at a completely different repository than the
    session's."""
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), cwd):
        if not candidate:
            continue
        path = os.path.join(candidate, "BRAIN", "checkpoints")
        if os.path.isdir(path):
            return path
    return None


def unfinished(directory):
    """Skeletons that still have empty sections. Empty means: after the section
    heading there is nothing but the italic hint, or the next heading."""
    found = []
    now = time.time()
    for name in sorted(os.listdir(directory), reverse=True):
        if not name.endswith(SUFFIX):
            continue
        path = os.path.join(directory, name)
        if now - os.path.getmtime(path) > MAX_AGE_DAYS * 86400:
            continue
        text = safely(lambda: io.open(path, encoding="utf-8").read(), "")
        if MARKER not in text:
            continue
        empty = 0
        for chunk in text.split("## " + MARKER)[1:]:
            body = chunk.split("\n## ")[0]
            lines = [l.strip() for l in body.splitlines()[1:] if l.strip()]
            real = [l for l in lines if not (l.startswith("_") and l.endswith("_"))]
            if not real:
                empty += 1
        if empty:
            found.append((path, empty))
    return found


def main():
    raw = safely(read_stdin, "")
    data = safely(lambda: json.loads(raw), {}) or {}
    directory = find_directory(data.get("cwd"))
    if not directory:
        return 0

    waiting = safely(lambda: unfinished(directory), [])
    if not waiting:
        return 0            # silence when there is nothing to do

    path, empty = waiting[0]
    print(
        "UNFINISHED PRE-COMPACTION CHECKPOINT.\n"
        "The `PreCompact` hook wrote a skeleton: %s\n"
        "The deterministic layer is already in it - verbatim user requests, files "
        "touched in the session, commands run, and the repository state.\n"
        "%d sections marked `%s` are left, and the script cannot compute them: "
        "what was settled, what is open, what must not be undone.\n\n"
        "Fill them in NOW, before starting new work - you have a fresh session "
        "summary in front of you and in an hour you will not. Write numbers and "
        "paths, not prose: the checkpoint serves a session that will remember "
        "nothing. Do not guess what the summary does not contain - write that it is "
        "unknown.\n"
        "INVOKE THE `brain-ops` SKILL NOW (with the Skill tool) and finish the "
        "checkpoint by its procedure - a hook does not run a skill and cannot, "
        "because it is a shell command, not a conversational turn. The script did "
        "the deterministic layer only; the rest needs judgement, which means the "
        "model.\n"
        "Finally, rebuild BRAIN/INDEX.md."
        % (path, empty, MARKER))
    return 0


try:
    sys.exit(main())
except Exception as e:
    sys.stderr.write("SessionStart checkpoint: %s\n" % e)
    sys.exit(0)
