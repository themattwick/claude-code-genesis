#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreCompact hook - rescues continuity before compaction takes the context away.

Registered in ~/.claude/settings.json as PreCompact. Reads JSON on stdin.

WHY. `brain-ops` lists "context is filling up / before compaction" as a moment that
calls for a checkpoint - but nothing was firing it. Nobody remembers in time for an
auto-compaction, because auto-compaction neither asks nor announces itself.

TWO LAYERS, DELIBERATELY SEPARATE:

  1. DETERMINISTIC - this script pulls from the transcript everything that does not
     need the model's memory to be written down: user requests, files touched,
     commands run, git state. It works ALWAYS, including mid-turn when nobody is
     asking the model for anything.

  2. JUDGEMENT - what cannot be computed: what was settled, what is open, what must
     not be undone. This script does NOT do that, and cannot.

WARNING: PreCompact STDOUT NEVER REACHES THE MODEL. Checked against Anthropic's
documentation, not assumed: only `SessionStart`, `UserPromptSubmit`,
`UserPromptExpansion` and `PostModelSwitch` inject context. PreCompact is not on that
list, so asking the model for anything from here would fail SILENTLY - the hook runs,
the message goes nowhere, the checkpoint stays empty and nobody finds out.

Layer 2 is therefore fired by a SECOND hook: `SessionStart` with matcher `compact`,
i.e. just AFTER compaction (`sessionstart_finish_checkpoint.py`). That is the
documented injection route, with the side benefit that the model gets the request
while a fresh summary is in front of it - not mid-interrupted-turn.

WARNING: IT NEVER INTERRUPTS COMPACTION. Every error is caught, the exit code is
always 0. A hook that breaks a session gets switched off after the first time and
then saves nothing ever again.
"""
import io
import json
import os
import subprocess
import sys
from datetime import datetime

# The Windows console is not UTF-8 by default, and this hook's output goes to
# Claude Code. Without this, non-ASCII characters come out as mojibake.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def read_stdin():
    """WARNING: NOT sys.stdin.read().

    Claude Code hands over JSON in UTF-8, but on Windows sys.stdin decodes it with
    the system code page (cp1250/cp1252). A path holding any non-ASCII character then
    falls apart silently: a surname spelled with an umlaut or an ogonek turns into
    mojibake, os.path.isfile() says it is not there, and the hook reports an empty
    transcript instead of an encoding error.

    Caught on a REAL compaction, not in a test: the checkpoint came out with 0 files
    and 0 user requests while the transcript was sitting right there. The test suite
    missed it because it built its own transcript under an ASCII path - and, worse,
    because it serialised its stdin with ensure_ascii=True, so the bytes it sent were
    pure ASCII and any decoder read them correctly. See test_hooks.py, case D.
    """
    try:
        return sys.stdin.buffer.read().decode("utf-8", "replace")
    except Exception:
        try:
            return sys.stdin.read()
        except Exception:
            return ""


MAX_REQUESTS = 40          # keep the last N user requests
MAX_REQUEST_CHARS = 220
MAX_FILES = 60

SUFFIX = "-before-compaction.md"
MARKER = "TO BE FILLED IN"


def safely(f, fallback):
    try:
        return f()
    except Exception:
        return fallback


def find_brain(cwd):
    """Only the project the hook handed us. NEVER os.getcwd().

    WARNING: the hook is registered GLOBALLY and fires in every project on the
    machine. The process working directory is not the session's project - it is
    wherever the shell happens to stand. With os.getcwd() in this lookup chain, a
    session in project A wrote its checkpoint into project B's BRAIN/. Caught by
    test case B.

    No BRAIN/ here means DO NOTHING. That is the correct outcome, not a reason to
    look somewhere else.
    """
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), cwd):
        if not candidate:
            continue
        path = os.path.join(candidate, "BRAIN", "checkpoints")
        if os.path.isdir(path):
            return path
    return None


def read_transcript(path):
    """Extract the computable facts. Interpret nothing.

    The fifth element of the result is the REASON FOR EMPTINESS. The first version
    returned empty lists silently when the transcript was missing - and the resulting
    checkpoint looked exactly like a checkpoint from a session where nothing happened.
    A continuity control that fails silently is worse than no control at all, because
    it looks like it is working.
    """
    requests, files, commands, agents = [], [], [], []
    if not path:
        return requests, files, commands, agents, "the hook passed no transcript path"
    if not os.path.exists(path):
        return requests, files, commands, agents, "transcript does not exist: %s" % path
    lines = 0
    for line in io.open(path, encoding="utf-8", errors="replace"):
        lines += 1
        try:
            entry = json.loads(line)
        except Exception:
            continue
        content = entry.get("message", {}).get("content")
        if entry.get("type") == "user" and isinstance(content, str):
            text = content.strip()
            # System messages and reminders are not requests from a human.
            if text and not text.startswith("<") and "system-reminder" not in text[:200]:
                requests.append(text.replace("\n", " ")[:MAX_REQUEST_CHARS])
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name, args = block.get("name"), block.get("input") or {}
                if name in ("Write", "Edit", "NotebookEdit"):
                    p = args.get("file_path")
                    if p and p not in files:
                        files.append(p)
                elif name == "Bash":
                    label = args.get("description") or (args.get("command") or "")[:80]
                    if label:
                        commands.append(label)
                elif name == "Agent":
                    agents.append("%s: %s" % (args.get("subagent_type", "?"),
                                              args.get("description", "")))
    reason = "" if (requests or files or commands) else (
        "the transcript has %d lines but holds neither requests nor tool calls" % lines)
    return requests, files, commands, agents, reason


def git(directory, *args):
    return subprocess.run(["git"] + list(args), cwd=directory, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=10).stdout.strip()


def main():
    raw = safely(read_stdin, "")
    data = safely(lambda: json.loads(raw), {}) or {}
    cwd = data.get("cwd")       # no os.getcwd() - see find_brain()
    # The docs use both names for this field - take whichever is present.
    trigger = data.get("compaction_trigger") or data.get("trigger") or "unknown"
    transcript = data.get("transcript_path")

    directory = find_brain(cwd)
    if not directory:
        # No BRAIN/ is not an error - not every project has one.
        print("PreCompact: no BRAIN/checkpoints directory, skipping.")
        return 0

    requests, files, commands, agents, reason = safely(
        lambda: read_transcript(transcript),
        ([], [], [], [], "failed to read the transcript"))

    project = os.path.dirname(os.path.dirname(directory))
    head = safely(lambda: git(project, "log", "--oneline", "-1"), "")
    branch = safely(lambda: git(project, "branch", "--show-current"), "")
    dirty = safely(lambda: git(project, "status", "--short"), "")
    recent = safely(lambda: git(project, "log", "--oneline", "--since=12.hours"), "")

    now = datetime.now()
    # WARNING: NEVER OVERWRITE AN EXISTING CHECKPOINT. A minute-resolution name lost
    # the second compaction within the same minute; seconds narrowed the window but
    # did not close it - two calls in a row fit inside one second. An overwritten
    # checkpoint looks exactly like a written one, so the loss is invisible. The
    # counter closes it for good. Caught by test case C.
    #
    # The counter goes BEFORE the suffix, not after it: this script and the
    # SessionStart hook both recognise skeletons by the suffix. With the counter at
    # the end, the file fell out of both filters - written, and invisible.
    stamp = now.strftime("%Y-%m-%d-%H%M%S")
    path = os.path.join(directory, stamp + SUFFIX)
    n = 2
    while os.path.exists(path):
        path = os.path.join(directory, "%s-%d%s" % (stamp, n, SUFFIX))
        n += 1

    out = []
    out.append("---\ntype: checkpoint\nstatus: skeleton\ndate: %s\n"
               "tags: [checkpoint, before-compaction, automatic]\n---\n"
               % now.strftime("%Y-%m-%d"))
    out.append("# Checkpoint before compaction - %s\n" % now.strftime("%Y-%m-%d %H:%M"))
    out.append("> Deterministic layer written automatically by the `PreCompact` hook "
               "(trigger: **%s**). Sections marked **%s** need judgement and are "
               "filled in by the model or a human; if they are still empty, "
               "compaction got there first.\n" % (trigger, MARKER))

    if reason:
        out.append("\n> **WARNING - the deterministic layer is INCOMPLETE.** %s\n"
                   "> Empty sections below do NOT mean nothing happened.\n" % reason)

    out.append("\n## Repository state\n")
    out.append("- branch: `%s`\n- last commit: `%s`\n" % (branch or "?", head or "?"))
    if recent:
        out.append("- commits in the last 12 h:\n")
        for line in recent.splitlines():
            out.append("  - `%s`\n" % line)
    out.append("- uncommitted: %s\n"
               % ("none" if not dirty else "\n" + "\n".join(
                   "  - `%s`" % l for l in dirty.splitlines()[:MAX_FILES]) + "\n"))

    if requests:
        out.append("\n## What the user asked for (verbatim, last %d)\n\n"
                   % min(len(requests), MAX_REQUESTS))
        for text in requests[-MAX_REQUESTS:]:
            out.append("- %s\n" % text)

    if files:
        out.append("\n## Files created and changed in this session\n\n")
        for p in files[:MAX_FILES]:
            out.append("- `%s`\n" % p)
        if len(files) > MAX_FILES:
            out.append("- ... and %d more\n" % (len(files) - MAX_FILES))

    if agents:
        out.append("\n## Agents launched\n\n")
        for a in agents:
            out.append("- %s\n" % a)

    if commands:
        out.append("\n## What was run (last 25)\n\n")
        for c in commands[-25:]:
            out.append("- %s\n" % c)

    out.append("\n---\n\n## %s - what was settled\n\n"
               "_What was decided and on what evidence. Numbers, not prose._\n\n" % MARKER)
    out.append("## %s - still open\n\n"
               "_What was left unfinished, and what the next step is._\n\n" % MARKER)
    out.append("## %s - what must not be undone\n\n"
               "_Decisions and measurements the next session could reverse by "
               "accident._\n\n" % MARKER)
    out.append("## Source\n\nSession transcript: `%s`\n" % (transcript or "unknown"))

    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(out))

    # This print goes to the log, NOT to the model (see the module docstring). It is
    # here so you can check the hook ran at all - not to ask for anything.
    print("PreCompact: wrote checkpoint skeleton %s (trigger %s, %d files, "
          "%d user requests)%s"
          % (path, trigger, len(files), len(requests),
             ("  WARNING: " + reason) if reason else ""))
    print(json.dumps({"continue": True}))
    return 0


try:
    sys.exit(main())
except Exception as e:                      # a hook NEVER breaks the session
    sys.stderr.write("PreCompact checkpoint: %s\n" % e)
    sys.exit(0)
