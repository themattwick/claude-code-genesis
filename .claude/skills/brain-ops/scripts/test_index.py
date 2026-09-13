#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does the index actually contain every entry? Checks the EFFECT, not the run.

    python test_index.py

WARNING: WHY "IT RAN" PROVES NOTHING. build_index.py prints a count and exits 0
whether or not the count is right. It printed "64 entries indexed" on a base
holding 134 of them, and nothing looked wrong: the number was plausible, the
file was written, the exit code was 0. The omission was only visible to someone
who counted the files by hand.

So this test counts the files itself and compares. The cases:

  A. every .md under a known folder is indexed, at ANY depth
  B. a nested collection renders as its own subsection, not as loose rows
  C. `path` stays exactly "<folder>/<name>" for a top-level entry
     (backwards compatibility: brain_hygiene.py uses it as an identity key)
  D. a directory name containing a dot survives grouping
  E. SKIP_FILES are skipped at every depth, not only at the top
"""
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _brain_common import collect_entries  # noqa: E402
from build_index import render_index       # noqa: E402


def write(path, title, extra=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ntype: spec\nstatus: active\ndate: 2026-09-13\n"
                    "tags: [proba]\n%s---\n\n# %s\n" % (extra, title),
                    encoding="utf-8")


def result(state, name, detail):
    print("%-4s %-56s %s" % ("OK" if state else "FAIL", name, detail))
    return bool(state)


def main():
    ok = True
    tmp = Path(tempfile.mkdtemp(prefix="test-index-"))
    try:
        brain = tmp / "BRAIN"
        (brain / "checkpoints").mkdir(parents=True)

        write(brain / "specs" / "2026-09-01-luzny.md", "Luźny spec")
        write(brain / "specs" / "mapa" / "map.md", "Mapa")
        write(brain / "specs" / "mapa" / "issues" / "01-pierwszy.md", "Pierwszy ticket")
        write(brain / "specs" / "mapa" / "issues" / "02-drugi.md", "Drugi ticket")
        write(brain / "specs" / "wersja.1.2" / "notatka.md", "Notatka z kropka")
        write(brain / "decisions" / "2026-09-02-decyzja.md", "Decyzja")
        # Must be skipped wherever it sits.
        write(brain / "specs" / "mapa" / "README.md", "Nie indeksowac")

        entries = collect_entries(brain)
        na_dysku = [p for p in brain.rglob("*.md")
                    if p.name not in ("INDEX.md", "README.md", "QUICK-REFERENCE.md")]

        ok &= result(len(entries) == len(na_dysku),
                     "A. kazdy plik zindeksowany, niezaleznie od glebokosci",
                     "na dysku %d, w indeksie %d" % (len(na_dysku), len(entries)))

        sciezki = {e["path"] for e in entries}
        ok &= result("specs/mapa/issues/01-pierwszy.md" in sciezki,
                     "A. ticket dwa poziomy w glab jest widoczny",
                     "sciezek: %d" % len(sciezki))
        ok &= result("specs/mapa/README.md" not in sciezki,
                     "E. README pominiety takze w podkatalogu", "")

        luzny = [e for e in entries if e["path"] == "specs/2026-09-01-luzny.md"]
        ok &= result(luzny and luzny[0]["group"] == "",
                     "C. wpis pierwszego poziomu: path bez zmian, group pusta",
                     luzny[0]["path"] if luzny else "brak wpisu")

        kropka = [e for e in entries if "wersja.1.2" in e["path"]]
        ok &= result(kropka and kropka[0]["group"] == "wersja.1.2",
                     "D. katalog z kropka w nazwie przetrwal grupowanie",
                     kropka[0]["group"] if kropka else "brak wpisu")

        # F. a directory marked as material is skipped, including everything
        # below it. Without the marker these files ARE indexed - so the case
        # proves the marker does the work, not the folder layout.
        material = brain / "specs" / "mapa" / "prototyp"
        write(material / "probka.md", "Probka bundla", extra="")
        write(material / "glebiej" / "jeszcze-probka.md", "Glebiej")
        przed = len(collect_entries(brain))
        (material / ".not-brain-entries").write_text(
            "Material, nie wpisy BRAIN.\n", encoding="utf-8")
        po = collect_entries(brain)
        ok &= result(przed == len(po) + 2,
                     "F. znacznik pomija katalog I wszystko ponizej niego",
                     "bez znacznika %d, ze znacznikiem %d" % (przed, len(po)))
        ok &= result(not any("prototyp" in e["path"] for e in po),
                     "F. zaden plik z oznaczonego katalogu nie przeszedl", "")
        entries = po

        tekst = render_index(entries)
        ok &= result("#### `mapa/` (3)" in tekst,
                     "B. kolekcja zagniezdzona ma wlasna sekcje z licznikiem",
                     "map.md + 2 tickety")
        ok &= result("Luźny spec" in tekst and "Pierwszy ticket" in tekst,
                     "B. i luzny wpis, i ticket sa w wyniku", "")
        # A collection must not also appear among the loose rows.
        przed = tekst.split("#### `mapa/`")[0]
        ok &= result("Pierwszy ticket" not in przed,
                     "B. ticket NIE dubluje sie w tabeli luznych wpisow", "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%s" % ("WSZYSTKO PRZESZLO" if ok else "COS PADLO - patrz wyzej"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
