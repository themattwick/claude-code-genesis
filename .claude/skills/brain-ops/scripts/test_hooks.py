#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Czy hooki kompaktowania robia to, co maja robic. Sprawdza SKUTEK, nie uruchomienie.

Uruchom po kazdej zmianie sciezek, przeniesieniu katalogu albo edycji ustawien:

    python test_hooks.py

Bierze polecenia z `~/.claude/settings.json`, czyli sprawdza to, co naprawde sie
odpali — nie sciezke wpisana tutaj. Gdy hookow tam nie ma, mowi to wprost i konczy
kodem 1, zamiast udawac, ze przeszlo.

⚠️ DLACZEGO NIE WYSTARCZY "SKRYPT SIE URUCHOMIL". Oba hooki z zalozenia koncza sie
kodem 0 zawsze — hook, ktory psuje sesje, zostaje wylaczony po pierwszym razie.
Kod wyjscia nie niesie wiec zadnej informacji o powodzeniu. Ten test patrzy, czy
plik powstal, GDZIE powstal i co jest w srodku.

Zlapal tak dwie usterki, ktorych uruchomienie hooka nie pokazywalo (2026-09-13):
  - szukanie projektu przez os.getcwd(): sesja jednego projektu zapisywala
    checkpoint do BRAIN zupelnie innego repozytorium
  - nazwa pliku z dokladnoscia do minuty: dwa kompaktowania w tej samej minucie
    nadpisywaly sie po cichu, a nadpisany plik wyglada jak zapisany

TRZY PRZYPADKI, bo dopiero razem cos dowodza:
  A. projekt Z katalogiem BRAIN/checkpoints -> checkpoint MA powstac wlasnie tam
  B. projekt BEZ katalogu BRAIN            -> NIC nie ma powstac, hook ma milczec
  C. dwa wywolania pod rzad                -> DWA pliki, nie jeden nadpisany

Przypadek B jest najwazniejszy: hooki wisza globalnie, wiec odpalaja sie w kazdym
projekcie na tej maszynie.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

USTAWIENIA = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")

# Transkrypt budujemy sami, zamiast siegac po prawdziwa sesje. Dzieki temu wiadomo,
# czego szukac w checkpoincie — test sprawdza TRESC, nie sam fakt zapisu.
POLECENIE = "zolwica kontryfikuje pasmanteryjny wrzeciennik"
PLIK_W_SESJI = "C:/nieistniejacy/przyklad.py"


def polecenie_hooka(ev):
    if not os.path.isfile(USTAWIENIA):
        return None
    d = json.load(io.open(USTAWIENIA, encoding="utf-8"))
    try:
        return d["hooks"][ev][0]["hooks"][0]["command"]
    except (KeyError, IndexError, TypeError):
        return None


def zbuduj_transkrypt(sciezka):
    wiersze = [
        {"type": "user", "message": {"content": POLECENIE}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {"file_path": PLIK_W_SESJI}}]}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash",
             "input": {"description": "policz pliki", "command": "ls"}}]}},
    ]
    with io.open(sciezka, "w", encoding="utf-8", newline="\n") as f:
        for w in wiersze:
            f.write(json.dumps(w, ensure_ascii=False) + "\n")


def odpal(ev, cwd, transkrypt):
    we = json.dumps({"cwd": cwd, "transcript_path": transkrypt,
                     "compaction_trigger": "auto", "source": "compact"})
    p = subprocess.run(polecenie_hooka(ev), shell=True, input=we, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def szkielety(projekt):
    k = os.path.join(projekt, "BRAIN", "checkpoints")
    if not os.path.isdir(k):
        return []
    return sorted(f for f in os.listdir(k) if f.endswith("-przed-kompaktem.md"))


def wynik(stan, nazwa, opis):
    print("%-4s %-54s %s" % ("OK" if stan else "BLAD", nazwa, opis))
    return stan


def main():
    for ev in ("PreCompact", "SessionStart"):
        if not polecenie_hooka(ev):
            print("BLAD hook %s nie jest zarejestrowany w %s" % (ev, USTAWIENIA))
            print("\nNIE PRZESZLO — nie ma czego testowac.")
            return 1

    ok = True
    tmp = tempfile.mkdtemp(prefix="test-hookow-")
    try:
        transkrypt = os.path.join(tmp, "sesja.jsonl")
        zbuduj_transkrypt(transkrypt)

        # A. projekt Z katalogiem BRAIN
        a = os.path.join(tmp, "z-brainem")
        os.makedirs(os.path.join(a, "BRAIN", "checkpoints"))
        kod, out, err = odpal("PreCompact", a, transkrypt)
        ok &= wynik(kod == 0, "A. projekt z BRAIN/ — nie przerywa sesji", "kod %d" % kod)
        pliki = szkielety(a)
        ok &= wynik(len(pliki) == 1, "A. checkpoint powstal W TYM projekcie",
                    ", ".join(pliki) or "brak pliku")
        tresc = ""
        if pliki:
            tresc = io.open(os.path.join(a, "BRAIN", "checkpoints", pliki[0]),
                            encoding="utf-8").read()
        ok &= wynik(POLECENIE in tresc, "A. checkpoint niesie DOSLOWNE polecenie uzytkownika",
                    "szukane: %r" % POLECENIE[:34])
        ok &= wynik(PLIK_W_SESJI in tresc, "A. checkpoint niesie plik dotkniety w sesji",
                    PLIK_W_SESJI)
        ok &= wynik("DO UZUPELNIENIA" in tresc, "A. checkpoint ma sekcje dla modelu",
                    "%d znakow" % len(tresc))
        kod, out, err = odpal("SessionStart", a, transkrypt)
        ok &= wynik(kod == 0 and "brain-ops" in out,
                    "A. SessionStart kaze wywolac skill brain-ops", "kod %d" % kod)

        # B. projekt BEZ katalogu BRAIN
        b = os.path.join(tmp, "bez-braina")
        os.makedirs(os.path.join(b, "src"))
        kod, out, err = odpal("PreCompact", b, transkrypt)
        ok &= wynik(kod == 0, "B. projekt bez BRAIN/ — nie przerywa sesji", "kod %d" % kod)
        ok &= wynik(os.listdir(b) == ["src"] and not os.listdir(os.path.join(b, "src")),
                    "B. projekt bez BRAIN/ — nic nie zapisal", str(os.listdir(b)))
        kod, out, err = odpal("SessionStart", b, transkrypt)
        ok &= wynik(kod == 0 and out.strip() == "", "B. SessionStart milczy",
                    "%d znakow na wyjsciu" % len(out))

        # C. dwa wywolania pod rzad
        odpal("PreCompact", a, transkrypt)
        ok &= wynik(len(szkielety(a)) == 2, "C. drugie kompaktowanie NIE nadpisuje pierwszego",
                    "plikow: %d" % len(szkielety(a)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%s" % ("WSZYSTKO PRZESZLO" if ok else "COS PADLO — patrz wyzej"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
