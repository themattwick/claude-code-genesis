#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Do the compaction hooks do their job? Checks the EFFECT, not that they ran.

Run it after any path change, directory move, or settings edit:

    python test_hooks.py

It takes the commands from `~/.claude/settings.json`, so it exercises what will
actually fire - not a path hard-coded here. If the hooks are not registered there, it
says so plainly and exits 1 instead of pretending to pass.

WARNING: WHY "THE SCRIPT RAN" PROVES NOTHING. Both hooks always exit 0 by design - a
hook that breaks a session gets switched off after the first time. The exit code
therefore carries no information about success. This test looks at whether a file
appeared, WHERE it appeared, and what is inside it.

That caught three bugs a bare run did not show:
  - project lookup via os.getcwd(): a session in one project wrote its checkpoint
    into a completely different repository's BRAIN
  - minute-resolution filenames: two compactions inside the same minute overwrote
    each other silently, and an overwritten file looks exactly like a written one
  - sys.stdin.read() decoding with the system code page: a transcript path holding a
    non-ASCII character "did not exist", and the checkpoint came out EMPTY while the
    hook reported success

FOUR CASES, because only together do they prove anything:
  A. project WITH BRAIN/checkpoints  -> the checkpoint must appear exactly there
  B. project WITHOUT BRAIN/          -> NOTHING may appear, the hook must stay silent
  C. two calls in a row              -> TWO files, not one overwritten
  D. transcript path with non-ASCII  -> it must still be read

Case B matters most: the hooks are registered globally, so they fire in every project
on the machine.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

SETTINGS = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")

SUFFIX = "-before-compaction.md"
MARKER = "TO BE FILLED IN"

# We build the transcript ourselves rather than reaching for a real session. That way
# we know what to look for in the checkpoint - the test checks CONTENT, not the mere
# fact that a file was written. The request is deliberate nonsense so it cannot
# appear by accident.
REQUEST = "the marmalade turbine kontrifies a passementerie spindle"
FILE_IN_SESSION = "C:/does-not-exist/example.py"

# A directory name with characters outside ASCII, matching a real session path on a
# machine whose user name is not spelled in ASCII. Case D exists only for this.
NON_ASCII_DIR = "s\u0107ie\u017cka-M\u00fcller-Wi\u0119cek"


def hook_command(event):
    if not os.path.isfile(SETTINGS):
        return None
    data = json.load(io.open(SETTINGS, encoding="utf-8"))
    try:
        return data["hooks"][event][0]["hooks"][0]["command"]
    except (KeyError, IndexError, TypeError):
        return None


def build_transcript(path):
    rows = [
        {"type": "user", "message": {"content": REQUEST}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {"file_path": FILE_IN_SESSION}}]}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash",
             "input": {"description": "count the files", "command": "ls"}}]}},
    ]
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run(event, cwd, transcript):
    # ensure_ascii=False and input as BYTES - this is what Claude Code does. With the
    # default ensure_ascii=True, "\u0119" is pure ASCII, so every decoder reads it
    # correctly and the test passes even against a broken hook. Verified: with text
    # here instead of bytes, case D still reported OK after the bug was reinstated.
    payload = json.dumps({"cwd": cwd, "transcript_path": transcript,
                          "compaction_trigger": "auto", "source": "compact"},
                         ensure_ascii=False).encode("utf-8")
    p = subprocess.run(hook_command(event), shell=True, input=payload,
                       capture_output=True)
    return (p.returncode,
            p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


def skeletons(project):
    directory = os.path.join(project, "BRAIN", "checkpoints")
    if not os.path.isdir(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith(SUFFIX)]


def result(state, name, detail):
    print("%-4s %-55s %s" % ("OK" if state else "FAIL", name, detail))
    return bool(state)


def read_only_skeleton(project):
    names = skeletons(project)
    if not names:
        return ""
    return io.open(os.path.join(project, "BRAIN", "checkpoints", names[0]),
                   encoding="utf-8").read()


def main():
    for event in ("PreCompact", "SessionStart"):
        if not hook_command(event):
            print("FAIL hook %s is not registered in %s" % (event, SETTINGS))
            print("\nDID NOT PASS - there is nothing to test.")
            return 1

    ok = True
    tmp = tempfile.mkdtemp(prefix="test-hooks-")
    try:
        transcript = os.path.join(tmp, "session.jsonl")
        build_transcript(transcript)

        # A. project WITH a BRAIN directory
        a = os.path.join(tmp, "with-brain")
        os.makedirs(os.path.join(a, "BRAIN", "checkpoints"))
        code, out, err = run("PreCompact", a, transcript)
        ok &= result(code == 0, "A. project with BRAIN/ - does not break the session",
                     "exit %d" % code)
        names = skeletons(a)
        ok &= result(len(names) == 1, "A. checkpoint appeared IN THIS project",
                     ", ".join(names) or "no file")
        text = read_only_skeleton(a)
        ok &= result(REQUEST in text, "A. checkpoint carries the VERBATIM user request",
                     "looked for: %r" % REQUEST[:34])
        ok &= result(FILE_IN_SESSION in text, "A. checkpoint carries a file touched in "
                     "the session", FILE_IN_SESSION)
        ok &= result(MARKER in text, "A. checkpoint has the sections for the model",
                     "%d chars" % len(text))
        code, out, err = run("SessionStart", a, transcript)
        ok &= result(code == 0 and "brain-ops" in out,
                     "A. SessionStart asks for the brain-ops skill", "exit %d" % code)

        # B. project WITHOUT a BRAIN directory
        b = os.path.join(tmp, "without-brain")
        os.makedirs(os.path.join(b, "src"))
        code, out, err = run("PreCompact", b, transcript)
        ok &= result(code == 0, "B. project without BRAIN/ - does not break the session",
                     "exit %d" % code)
        ok &= result(os.listdir(b) == ["src"] and not os.listdir(os.path.join(b, "src")),
                     "B. project without BRAIN/ - wrote nothing", str(os.listdir(b)))
        code, out, err = run("SessionStart", b, transcript)
        ok &= result(code == 0 and out.strip() == "", "B. SessionStart stays silent",
                     "%d chars of output" % len(out))

        # D. transcript path holding characters outside ASCII.
        #
        # Cases A-C used an ASCII path and therefore DID NOT SEE that sys.stdin.read()
        # decodes the incoming JSON with the system code page: the path fell apart,
        # the file "did not exist", and the checkpoint came out EMPTY at exit code 0.
        # Only a real compaction exposed it. This case keeps it from coming back.
        d_dir = os.path.join(tmp, NON_ASCII_DIR)
        os.makedirs(d_dir)
        d_transcript = os.path.join(d_dir, "session.jsonl")
        build_transcript(d_transcript)
        d = os.path.join(tmp, "non-ascii-path")
        os.makedirs(os.path.join(d, "BRAIN", "checkpoints"))
        code, out, err = run("PreCompact", d, d_transcript)
        text = read_only_skeleton(d)
        ok &= result(REQUEST in text,
                     "D. transcript under a non-ASCII path WAS READ",
                     out.strip()[:110] or "no output")
        ok &= result("INCOMPLETE" not in text,
                     "D. no incomplete-deterministic-layer warning",
                     "%d chars" % len(text))

        # C. two calls in a row
        run("PreCompact", a, transcript)
        ok &= result(len(skeletons(a)) == 2,
                     "C. a second compaction does NOT overwrite the first",
                     "files: %d" % len(skeletons(a)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%s" % ("EVERYTHING PASSED" if ok else "SOMETHING FAILED - see above"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
