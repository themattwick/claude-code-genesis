#!/usr/bin/env python3
"""Do the content checks and create_checkpoint.py --strict actually bite?

    python test_validation.py         # exit 1 if anything fails

Checks the EFFECT. Positive cases prove a good entry is left alone, negative cases
prove a bad one is caught - a validator that flags nothing passes every positive case.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _brain_common import collect_entries   # noqa: E402
from brain_hygiene import run_checks        # noqa: E402

TEMPLATES = Path(HERE).parent / "templates"


def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fm(typ, status="active", tags="[]", extra=""):
    return "---\ntype: %s\nstatus: %s\ndate: 2026-11-01\ntags: %s\n%s---\n\n" % (
        typ, status, tags, extra)


def result(state, name, detail=""):
    print("%-4s %-66s %s" % ("OK" if state else "FAIL", name, detail))
    return bool(state)


GOOD_CP = fm("checkpoint") + ("# Checkpoint - good\n\n## Summary\nauth halfway\n\n"
                              "## Left off\nsrc/a.py:3 - test fails\n\n"
                              "## Next steps\n1. fix test\n")


def main():
    ok = True
    tmp = Path(tempfile.mkdtemp(prefix="test-validation-"))
    try:
        brain = tmp / "BRAIN"
        cp = brain / "checkpoints"
        put(cp / "2026-11-01-good.md", GOOD_CP)
        put(cp / "2026-11-02-title-only.md", fm("checkpoint") + "# Checkpoint - nothing\n")
        put(cp / "2026-11-03-no-left-off.md", fm("checkpoint") + (
            "# Checkpoint - x\n\n## Summary\nstuff\n\n## Left off\n\n## Next steps\n1. a\n"))
        put(cp / "2026-11-04-legacy.md", fm("checkpoint") + (
            "# Checkpoint - old\n\n## Completed since last checkpoint\n- did the thing\n\n"
            "## Open questions / next steps\n- more\n"))
        put(cp / "2026-11-05-skeleton.md", fm("checkpoint", status="skeleton") + "# Hook\n")
        put(cp / "2026-11-06-archived.md", fm("checkpoint", status="archived") + "# Old\n")
        # Windows editors (Notepad, PowerShell 5 Out-File) save UTF-8 with a BOM
        put(cp / "2026-11-08-bom-archived.md", "﻿" + fm("checkpoint", status="archived") + "# Old\n")
        put(cp / "2026-11-07-template.md",
            (TEMPLATES / "checkpoint-template.md").read_text(encoding="utf-8"))

        L = brain / "learnings"
        put(L / "2026-11-01-good.md", fm("learning", tags="[cache, tenant]") + (
            "# Cache keys must include the tenant\n\n## Root cause\nshared key\n\n## Rule\n"
            "Next time I add a cache, I will key it by tenant.\n\n## Recognition signal\n"
            "Another tenant's data in a response.\n"))
        put(L / "2026-11-02-diary.md", fm("learning") + (
            "# Session log\n\nWe spent the afternoon on the cache and fixed it.\n"))
        put(L / "2026-11-03-no-signal.md", fm("learning") + (
            "# Retry storms\n\n## Rule\nNext time I add retries, I will add jitter.\n"))
        # duplicates
        put(L / "2026-11-04-dup-a.md", fm("learning", tags="[cache, tenant]") + (
            "# Cache keys must include the tenant id\n\n## Rule\nNext time x.\n\n"
            "## Recognition signal\ny\n"))
        put(L / "2026-11-05-unrelated.md", fm("learning", tags="[retry]") + (
            "# Backoff needs jitter\n\n## Rule\nNext time x.\n\n## Recognition signal\ny\n"))
        put(L / "2026-11-06-retired-dup.md", fm("learning", status="archived", tags="[cache, tenant]") + (
            "# Cache keys must include the tenant id\n"))

        entries = collect_entries(brain)
        findings = run_checks(brain, entries, 14)

        def has(check, name):
            return any(f.check == check and f.path.endswith(name) for f in findings)

        def any_for(name):
            return any(f.path.endswith(name) and f.check in
                       ("empty-checkpoint", "checkpoint-incomplete", "learning-incomplete")
                       for f in findings)

        ok &= result(not any_for("cp-good") and not any_for("checkpoints/2026-11-01-good.md"),
                     "A. complete checkpoint raises nothing")
        ok &= result(has("empty-checkpoint", "title-only.md"), "B. title-only checkpoint is flagged")
        ok &= result(has("checkpoint-incomplete", "no-left-off.md"),
                     "C. empty Left off is flagged")
        ok &= result(not any_for("legacy.md"), "D. legacy-heading checkpoint with content is left alone")
        ok &= result(not any_for("skeleton.md"), "E. status: skeleton (hook) is ignored")
        ok &= result(not has("invalid-field", "skeleton.md"),
                     "E2. status: skeleton (hook) is a valid status, not an unknown one")
        ok &= result(not has("missing-frontmatter", "bom-archived.md")
                     and not any_for("bom-archived.md"),
                     "F2. frontmatter after a UTF-8 BOM is read (archived stays archived)")
        ok &= result(not any_for("archived.md"), "F. archived title-only checkpoint is ignored")
        ok &= result(has("empty-checkpoint", "2026-11-07-template.md"),
                     "G. an unfilled copy of the template (with footer) is flagged")

        ok &= result(not any_for("learnings/2026-11-01-good.md"),
                     "H. learning with rule and signal raises nothing")
        ok &= result(has("learning-incomplete", "diary.md"), "H. diary-style learning is flagged")
        ok &= result(has("learning-incomplete", "no-signal.md")
                     and "recognition signal" in next(f.detail for f in findings
                                                      if f.path.endswith("no-signal.md")
                                                      and f.check == "learning-incomplete"),
                     "H. missing recognition signal is named")

        ok &= result(has("possible-duplicate", "dup-a.md"),
                     "I. near-identical titles + shared tags -> possible-duplicate")
        ok &= result(not has("possible-duplicate", "unrelated.md"),
                     "I. unrelated entry is not a duplicate")
        ok &= result(not has("possible-duplicate", "retired-dup.md"),
                     "I. a retired entry is not compared")

        # create_checkpoint.py end to end, run from a project directory
        proj = tmp / "proj"
        (proj / "BRAIN" / "checkpoints").mkdir(parents=True)
        script = os.path.join(HERE, "create_checkpoint.py")

        def run(*a):
            return subprocess.run([sys.executable, script, *a], cwd=proj,
                                  capture_output=True, text=True)

        written = lambda: list((proj / "BRAIN" / "checkpoints").glob("*.md"))
        r = run("bare", "--strict")
        ok &= result(r.returncode == 1 and not written(),
                     "J. --strict without fields: exit 1, nothing written", "exit=%d" % r.returncode)
        r = run("bare")
        ok &= result(r.returncode == 0 and len(written()) == 1 and "WARNING" in r.stderr,
                     "J. without --strict: warns and still writes")
        for f in written():
            f.unlink()
        r = run("full", "--strict", "--summary", "halfway", "--left-off", "a.py:1",
                "--next", "one", "--next", "two")
        files = written()
        body = files[0].read_text(encoding="utf-8") if files else ""
        ok &= result(r.returncode == 0 and "a.py:1" in body and "1. one\n2. two" in body,
                     "J. with fields: written, Left off and ordered Next steps present")
        f2 = run_checks(proj / "BRAIN", collect_entries(proj / "BRAIN"), 14)
        ok &= result(not [f for f in f2 if f.check in ("empty-checkpoint", "checkpoint-incomplete")],
                     "J. a checkpoint it wrote with fields passes hygiene")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%s" % ("ALL PASSED" if ok else "SOMETHING FAILED - see above"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
