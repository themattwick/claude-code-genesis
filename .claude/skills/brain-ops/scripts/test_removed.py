#!/usr/bin/env python3
"""Does the "deliberately removed" zone show up, and is it enforced?

    python test_removed.py            # exit 1 if anything fails

  A. a removal entry appears in INDEX under "Deliberately removed", with its four fields
  B. it is NOT also listed again under Active knowledge
  C. a removal with a missing field is reported as removal-incomplete
  D. a removal whose field is an unfilled TODO placeholder is reported
  E. `return_if: never` is a valid answer
  F. a list value (`removed: [a, b]`) and a `|` in a value do not break the index
  G. a retired removal (status: archived) leaves the zone and is not re-checked
  H. a file in removed/ without a `type` falls back to type "removal"
  I. an unfilled copy of the removal template is flagged
  J. a removed path that exists again is reported (HIGH); one that is gone is not
  K. concepts, paths outside the project, and archived removals are not checked
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _brain_common import collect_entries   # noqa: E402
from brain_hygiene import run_checks        # noqa: E402
from build_index import render_index        # noqa: E402

TEMPLATE = Path(HERE).parent / "templates" / "entries" / "removal.md"


def removal(path, title, status="active", **fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---", "type: removal", "status: %s" % status, "date: 2026-11-10", "tags: []"]
    lines += ["%s: %s" % (k, v) for k, v in fields.items()]
    lines += ["---", "", "# %s" % title, "", "## Why it was removed", "Measured.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def result(state, name, detail=""):
    print("%-4s %-66s %s" % ("OK" if state else "FAIL", name, detail))
    return bool(state)


FULL = dict(removed="legacy-sync.py", reason="raced with the watcher",
            replacement="watcher.py", return_if="never")


def main():
    ok = True
    tmp = Path(tempfile.mkdtemp(prefix="test-removed-"))
    try:
        brain = tmp / "BRAIN"
        (brain / "checkpoints").mkdir(parents=True)
        R = brain / "removed"
        removal(R / "2026-11-10-full.md", "Legacy sync", **FULL)
        removal(R / "2026-11-11-no-reason.md", "No reason",
                removed="x", replacement="y", return_if="never")
        removal(R / "2026-11-12-todo.md", "Todo",
                removed="x", reason="TODO why", replacement="y", return_if="z")
        removal(R / "2026-11-13-never.md", "Never returns",
                removed="old-api", reason="insecure", replacement="v2", return_if="never")
        removal(R / "2026-11-14-weird.md", "Weird",
                removed="[a.py, b.py]", reason="pipe | in text", replacement="c", return_if="d")
        removal(R / "2026-11-15-archived.md", "Restored", status="archived", removed="x")
        (R / "2026-11-16-notype.md").write_text("# No type\n", encoding="utf-8")
        (R / "2026-11-17-template.md").write_text(
            TEMPLATE.read_text(encoding="utf-8").replace("YYYY-MM-DD", "2026-11-17"),
            encoding="utf-8")

        entries = collect_entries(brain)
        findings = run_checks(brain, entries, 14)
        text = render_index(entries)

        def flagged(name):
            return any(f.check == "removal-incomplete" and f.path.endswith(name)
                       for f in findings)

        zone = text.split("Deliberately removed")[1].split("## Active knowledge")[0]
        ok &= result("legacy-sync.py" in zone and "raced with the watcher" in zone
                     and "watcher.py" in zone and "never" in zone,
                     "A. zone shows removed / reason / replacement / return_if")
        ok &= result("Legacy sync" not in text.split("## Active knowledge")[1],
                     "B. a removal is not listed twice")
        ok &= result(flagged("no-reason.md") and "reason" in next(
            f.detail for f in findings if f.path.endswith("no-reason.md")
            and f.check == "removal-incomplete"), "C. missing reason is flagged and named")
        ok &= result(flagged("todo.md"), "D. TODO placeholder counts as missing")
        ok &= result(not flagged("never.md") and not flagged("full.md"),
                     "E. complete entries, incl. return_if: never, raise nothing")
        ok &= result("a.py, b.py" in zone and "pipe \\| in text" in zone,
                     "F. list value joined, pipe escaped - index still builds")
        ok &= result("Restored" not in zone and not flagged("archived.md"),
                     "G. archived removal leaves the zone and is not re-checked")
        nt = next(e for e in entries if e["path"].endswith("notype.md"))
        ok &= result(nt["type"] == "removal", "H. removed/ without a type falls back to removal",
                     nt["type"])
        ok &= result(flagged("2026-11-17-template.md"),
                     "I. unfilled copy of the removal template is flagged")

        # J/K. resurrection, in a fresh base so the cases above stay independent
        proj = tmp / "proj"
        R2 = proj / "BRAIN" / "removed"
        (proj / "BRAIN" / "checkpoints").mkdir(parents=True)
        (proj / "src").mkdir()
        (proj / "src" / "old_sync.py").write_text("back again\n", encoding="utf-8")
        (tmp / "outside.txt").write_text("not ours\n", encoding="utf-8")
        base = dict(reason="r", replacement="x", return_if="never")
        removal(R2 / "2026-11-20-back.md", "Back", removed="src/old_sync.py", **base)
        removal(R2 / "2026-11-20-gone.md", "Gone", removed="src/deleted.py", **base)
        removal(R2 / "2026-11-20-concept.md", "Concept", removed="the v1 sync approach", **base)
        removal(R2 / "2026-11-20-escape.md", "Escape", removed="../outside.txt", **base)
        removal(R2 / "2026-11-20-list.md", "List", removed="[src/deleted.py, src/old_sync.py]", **base)
        removal(R2 / "2026-11-20-arch.md", "Arch", status="archived", removed="src/old_sync.py", **base)
        f2 = run_checks(proj / "BRAIN", collect_entries(proj / "BRAIN"), 14)
        res = {f.path.split("/")[-1] for f in f2 if f.check == "removal-resurrected"}
        ok &= result("2026-11-20-back.md" in res
                     and all(f.severity == "HIGH" for f in f2 if f.check == "removal-resurrected"),
                     "J. removed path that exists again -> HIGH removal-resurrected")
        ok &= result("2026-11-20-gone.md" not in res, "J. removed path that is gone -> nothing")
        ok &= result("2026-11-20-list.md" in res, "J. one live path inside a list is caught")
        # A concept never exists on disk, so the end-to-end result cannot tell whether
        # it was treated as a path. Check the classifier itself.
        from brain_hygiene import _path_like
        ok &= result(not _path_like("the v1 sync approach") and not _path_like("legacy sync")
                     and _path_like("src/old_sync.py") and _path_like("install.ps1"),
                     "K. a concept is not treated as a path; a file or path is")
        ok &= result("2026-11-20-escape.md" not in res, "K. a path outside the project is ignored")
        ok &= result("2026-11-20-arch.md" not in res, "K. an archived removal is not checked")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%s" % ("ALL PASSED" if ok else "SOMETHING FAILED - see above"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
