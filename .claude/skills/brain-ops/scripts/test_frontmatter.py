#!/usr/bin/env python3
"""Do `confidence` / `scope` / `projects` behave, and do old entries survive them?

    python test_frontmatter.py        # exit 1 if anything fails

Checks the EFFECT (what the index shows, what hygiene reports), not that the
scripts ran. Cases:

  A. an entry with none of the fields is unchanged: no finding, "—" confidence,
     project scope, and the old three-column table for non-trust types
  B. confirmed in 2 distinct projects -> promotable, shown as global (promoted),
     hygiene reports promotion-due
  C. confirmed in only 1 project -> NOT promotable; tentative in 3 -> NOT promotable
  D. duplicates and case do not inflate the project count
  E. invalid confidence / scope values are reported
  F. scope: global without confirmed -> global-unconfirmed
  G. an explicit `scope: global` entry is not reported as promotion-due
  H. `tentative` past the threshold -> tentative-stale; recent, confirmed or
     unstated confidence -> nothing (dates computed from today, not hardcoded)
"""
import os
import shutil
from datetime import datetime, timedelta
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _brain_common import collect_entries   # noqa: E402
from brain_hygiene import TENTATIVE_STALE_DAYS, run_checks  # noqa: E402
from build_index import render_index        # noqa: E402


def write(path, title, typ="learning", extra=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ntype: %s\nstatus: active\ndate: 2026-09-13\ntags: [t]\n%s---\n\n# %s\n"
                    % (typ, extra, title), encoding="utf-8")


def result(state, name, detail=""):
    print("%-4s %-62s %s" % ("OK" if state else "FAIL", name, detail))
    return bool(state)


def main():
    ok = True
    tmp = Path(tempfile.mkdtemp(prefix="test-frontmatter-"))
    try:
        brain = tmp / "BRAIN"
        (brain / "checkpoints").mkdir(parents=True)
        L = brain / "learnings"
        write(L / "2026-09-01-plain.md", "Plain")
        write(L / "2026-09-02-promo.md", "Promo",
              extra="confidence: confirmed\nprojects: [shop, api]\n")
        write(L / "2026-09-03-one.md", "OneProject",
              extra="confidence: confirmed\nprojects: [shop]\n")
        write(L / "2026-09-04-tent.md", "TentativeThree",
              extra="confidence: tentative\nprojects: [a, b, c]\n")
        write(L / "2026-09-05-dupes.md", "Dupes",
              extra="confidence: confirmed\nprojects: [Shop, shop, SHOP]\n")
        write(L / "2026-09-06-bad.md", "Bad",
              extra="confidence: maybe\nscope: universe\n")
        write(L / "2026-09-07-glob-unconf.md", "GlobalUnconfirmed",
              extra="confidence: tentative\nscope: global\n")
        write(L / "2026-09-08-glob.md", "GlobalOk",
              extra="confidence: confirmed\nscope: global\nprojects: [a, b]\n")
        write(brain / "decisions" / "2026-09-09-d.md", "Decision", typ="decision")

        entries = collect_entries(brain)
        by = {e["path"].split("/")[-1]: e for e in entries}
        findings = run_checks(brain, entries, 14)

        def found(check, name):
            return any(f.check == check and f.path.endswith(name) for f in findings)

        p = by["2026-09-01-plain.md"]
        ok &= result(p["confidence"] == "" and p["scope"] == "project"
                     and not p["promotable"], "A. entry without fields: unchanged defaults")
        trust_checks = ("invalid-field", "promotion-due", "global-unconfirmed")
        ok &= result(not any(f.path.endswith("plain.md") and f.check in trust_checks
                             for f in findings),
                     "A. ... and no trust-field finding is raised for it")

        ok &= result(by["2026-09-02-promo.md"]["promotable"]
                     and by["2026-09-02-promo.md"]["scope"] == "global",
                     "B. confirmed in 2 projects -> promotable, effective scope global")
        ok &= result(found("promotion-due", "promo.md"), "B. hygiene reports promotion-due")

        ok &= result(not by["2026-09-03-one.md"]["promotable"],
                     "C. confirmed in 1 project -> not promotable")
        ok &= result(not by["2026-09-04-tent.md"]["promotable"],
                     "C. tentative in 3 projects -> not promotable")
        ok &= result(not by["2026-09-05-dupes.md"]["promotable"]
                     and by["2026-09-05-dupes.md"]["projects"] == ["shop"],
                     "D. Shop/shop/SHOP counts as one project")

        ok &= result(found("invalid-field", "bad.md")
                     and sum(1 for f in findings if f.check == "invalid-field"
                             and f.path.endswith("bad.md")) == 2,
                     "E. bad confidence AND bad scope are both reported")
        ok &= result(found("global-unconfirmed", "glob-unconf.md"),
                     "F. scope: global without confirmed is reported")
        ok &= result(not found("promotion-due", "glob.md")
                     and not found("global-unconfirmed", "glob.md"),
                     "G. explicit global + confirmed raises nothing")

        old = (datetime.now() - timedelta(days=TENTATIVE_STALE_DAYS + 5)).strftime("%Y-%m-%d")
        new = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        T = tmp / "t" / "BRAIN"
        (T / "checkpoints").mkdir(parents=True)
        for name, date, conf in (("old-tent", old, "tentative"), ("new-tent", new, "tentative"),
                                 ("old-conf", old, "confirmed"), ("old-unset", old, None)):
            p = T / "learnings" / ("%s.md" % name)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("---\ntype: learning\nstatus: active\ndate: %s\ntags: []\n%s---\n\n# %s\n"
                         % (date, "confidence: %s\n" % conf if conf else "", name), encoding="utf-8")
        stale = {f.path.split("/")[-1] for f in run_checks(T, collect_entries(T), 14)
                 if f.check == "tentative-stale"}
        ok &= result(stale == {"old-tent.md"},
                     "H. only an old, explicitly tentative entry is tentative-stale", str(sorted(stale)))

        text = render_index(entries)
        ok &= result("| Date | Title | Confidence | Scope | Tags |" in text,
                     "index: learnings table has Confidence and Scope columns")
        ok &= result("global (promoted)" in text, "index: promoted entry is labelled")
        dec = text.split("### Decisions")[1]
        ok &= result("| Date | Title | Tags |" in dec.split("###")[0],
                     "A. non-trust types keep the old three-column table")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%s" % ("ALL PASSED" if ok else "SOMETHING FAILED - see above"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
