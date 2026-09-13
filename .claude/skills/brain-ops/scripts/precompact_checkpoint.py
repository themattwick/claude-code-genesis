#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hook PreCompact — ratuje ciaglosc, zanim kompaktowanie zabierze kontekst.

Rejestrowany w ~/.claude/settings.json jako PreCompact. Czyta JSON ze stdin.

PO CO. `brain-ops` wymienia "context is filling up / before compaction" jako moment,
w ktorym nalezy zapisac checkpoint — ale nic tego nie wyzwalalo. Przy autokompakcie
nikt o tym nie pamieta, bo autokompakt nie pyta o zgode i nie zapowiada sie.

DWIE WARSTWY, CELOWO ROZDZIELONE:

  1. DETERMINISTYCZNA — ten skrypt sam wyciaga z transkryptu to, czego model nie
     musi pamietac, zeby to zapisac: polecenia uzytkownika, dotkniete pliki,
     uruchomione komendy, stan gita. Dziala ZAWSZE, tez gdy model jest w polowie
     tury i nikt go o nic nie pyta.

  2. OSADOWA — uzupelnienie tego, czego wyliczyc sie nie da: co ustalono, co zostalo
     otwarte, czego nie wolno cofnac. Tego ten skrypt NIE robi i nie moze.

⚠️ STDOUT Z PreCompact NIE DOCIERA DO MODELU. Sprawdzone w dokumentacji Anthropic,
nie zalozone: kontekst wstrzykuja wylacznie `SessionStart`, `UserPromptSubmit`,
`UserPromptExpansion` i `PostModelSwitch`. PreCompact nie jest na tej liscie, wiec
proba poproszenia stad modelu o cokolwiek bylaby cicha porazka — hook by sie wykonal,
komunikat poszedlby w pustke, a checkpoint zostalby pusty i nikt by sie nie dowiedzial.

Dlatego warstwe 2 wyzwala DRUGI hook: `SessionStart` z matcherem `compact`, czyli
juz PO kompaktowaniu (`sessionstart_dokoncz_checkpoint.py`). To jest udokumentowana
droga wstrzykniecia kontekstu i ma te przewage, ze model dostaje polecenie, gdy ma
swieze streszczenie przed soba — a nie w polowie przerwanej tury.

⚠️ NIGDY NIE PRZERYWA KOMPAKTOWANIA. Kazdy blad jest lapany, kod wyjscia zawsze 0.
Hook, ktory psuje sesje, zostanie wylaczony po pierwszym razie i nie uratuje juz nic.
"""
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime

# Konsola Windows domyslnie nie jest UTF-8, a wyjscie hooka trafia do Claude Code.
# Bez tego polskie znaki wychodza jako krzaki — sprawdzone, nie zalozone.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MAKS_POLECEN = 40          # ostatnie N polecen uzytkownika
MAKS_ZNAKOW_POLECENIA = 220
MAKS_PLIKOW = 60


def bezpiecznie(f, domyslne):
    try:
        return f()
    except Exception:
        return domyslne


def znajdz_brain(cwd):
    """Tylko projekt, ktory hook nam podal. NIGDY os.getcwd().

    ⚠️ Hook jest zarejestrowany GLOBALNIE i odpala sie w kazdym projekcie. Katalog
    roboczy procesu to nie jest projekt sesji — to katalog, w ktorym akurat stoi
    powloka. Z os.getcwd() w liscie sesja obcego projektu zapisywala sie do BRAIN
    zupelnie innego repozytorium. Zlapane testem 2026-09-13, przypadek B.
    """
    kand = [os.environ.get("CLAUDE_PROJECT_DIR"), cwd]
    for k in kand:
        if not k:
            continue
        p = os.path.join(k, "BRAIN", "checkpoints")
        if os.path.isdir(p):
            return p
    return None


def czytaj_transkrypt(sciezka):
    """Wyciaga fakty, ktore da sie wyliczyc. Nie interpretuje niczego.

    Piaty element wyniku to POWOD PUSTKI. Pierwsza wersja zwracala po cichu puste
    listy, gdy transkryptu nie bylo — i checkpoint wygladal wtedy dokladnie tak samo
    jak checkpoint z pustej sesji. Cicha awaria kontroli ciaglosci jest gorsza niz
    brak kontroli, bo wyglada na dzialajaca.
    """
    polecenia, pliki, komendy, agenci = [], [], [], []
    if not sciezka:
        return polecenia, pliki, komendy, agenci, "hook nie podal sciezki transkryptu"
    if not os.path.exists(sciezka):
        return polecenia, pliki, komendy, agenci, "transkrypt nie istnieje: %s" % sciezka
    wierszy = 0
    for lin in io.open(sciezka, encoding="utf-8", errors="replace"):
        wierszy += 1
        try:
            o = json.loads(lin)
        except Exception:
            continue
        tresc = o.get("message", {}).get("content")
        if o.get("type") == "user" and isinstance(tresc, str):
            t = tresc.strip()
            # Wiadomosci systemowe i przypomnienia nie sa poleceniami czlowieka.
            if t and not t.startswith("<") and "system-reminder" not in t[:200]:
                polecenia.append(t.replace("\n", " ")[:MAKS_ZNAKOW_POLECENIA])
        if isinstance(tresc, list):
            for b in tresc:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                nazwa, we = b.get("name"), b.get("input") or {}
                if nazwa in ("Write", "Edit", "NotebookEdit"):
                    p = we.get("file_path")
                    if p and p not in pliki:
                        pliki.append(p)
                elif nazwa == "Bash":
                    opis = we.get("description") or (we.get("command") or "")[:80]
                    if opis:
                        komendy.append(opis)
                elif nazwa == "Agent":
                    agenci.append("%s: %s" % (we.get("subagent_type", "?"),
                                              we.get("description", "")))
    powod = "" if (polecenia or pliki or komendy) else (
        "transkrypt ma %d wierszy, ale nie znaleziono w nim ani polecen, ani narzedzi"
        % wierszy)
    return polecenia, pliki, komendy, agenci, powod


def git(katalog, *arg):
    return subprocess.run(["git"] + list(arg), cwd=katalog, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=10).stdout.strip()


def main():
    surowe = bezpiecznie(lambda: sys.stdin.read(), "")
    dane = bezpiecznie(lambda: json.loads(surowe), {}) or {}
    cwd = dane.get("cwd")       # bez os.getcwd() — patrz znajdz_brain()
    # Dokumentacja uzywa obu nazw dla tego samego pola — bierzemy ktorekolwiek jest.
    wyzwalacz = dane.get("compaction_trigger") or dane.get("trigger") or "nieznany"
    transkrypt = dane.get("transcript_path")

    kat = znajdz_brain(cwd)
    if not kat:
        # Brak BRAIN/ to nie blad — nie kazdy projekt go ma.
        print("PreCompact: brak katalogu BRAIN/checkpoints, pomijam.")
        return 0

    polecenia, pliki, komendy, agenci, powod = bezpiecznie(
        lambda: czytaj_transkrypt(transkrypt), ([], [], [], [], "blad czytania transkryptu"))

    projekt = os.path.dirname(os.path.dirname(kat))
    head = bezpiecznie(lambda: git(projekt, "log", "--oneline", "-1"), "")
    galaz = bezpiecznie(lambda: git(projekt, "branch", "--show-current"), "")
    brudne = bezpiecznie(lambda: git(projekt, "status", "--short"), "")
    od_commita = bezpiecznie(
        lambda: git(projekt, "log", "--oneline", "--since=12.hours"), "")

    teraz = datetime.now()
    # ⚠️ NIGDY NIE NADPISUJ ISTNIEJACEGO CHECKPOINTU. Nazwa z dokladnoscia do minuty
    # gubila drugie kompaktowanie w tej samej minucie; sekundy zwezily okno, ale go nie
    # zamknely — dwa wywolania pod rzad mieszcza sie w jednej sekundzie. Nadpisany
    # checkpoint wyglada dokladnie tak samo jak zapisany, wiec strata jest niewidoczna.
    # Licznik zamyka to na dobre. Zlapane testem, przypadek C.
    # Licznik idzie PRZED koncowka, nie po niej: i ten skrypt, i hook SessionStart
    # rozpoznaja szkielety po koncowce "-przed-kompaktem.md". Nazwa z licznikiem na
    # koncu wypadala z obu filtrow, czyli plik powstawal i byl niewidoczny.
    stempel = teraz.strftime("%Y-%m-%d-%H%M%S")
    sciezka = os.path.join(kat, stempel + "-przed-kompaktem.md")
    n = 2
    while os.path.exists(sciezka):
        sciezka = os.path.join(kat, "%s-%d-przed-kompaktem.md" % (stempel, n))
        n += 1

    czesci = []
    czesci.append("---\ntype: checkpoint\nstatus: szkielet\ndate: %s\n"
                  "tags: [checkpoint, przed-kompaktem, automat]\n---\n"
                  % teraz.strftime("%Y-%m-%d"))
    czesci.append("# Checkpoint przed kompaktowaniem — %s\n"
                  % teraz.strftime("%Y-%m-%d %H:%M"))
    czesci.append("> Warstwa deterministyczna zapisana automatycznie przez hook "
                  "`PreCompact` (wyzwalacz: **%s**). Sekcje oznaczone **DO UZUPELNIENIA** "
                  "wymagaja sadu i wypelnia je model albo czlowiek; jesli zostaly puste, "
                  "znaczy to, ze kompaktowanie zdazylo pierwsze.\n" % wyzwalacz)

    if powod:
        czesci.append("\n> **UWAGA — warstwa deterministyczna jest NIEPELNA.** %s\n"
                      "> Puste sekcje ponizej NIE znacza, ze nic sie nie dzialo.\n" % powod)

    czesci.append("\n## Stan repozytorium\n")
    czesci.append("- galaz: `%s`\n- ostatni commit: `%s`\n" % (galaz or "?", head or "?"))
    if od_commita:
        czesci.append("- commity z ostatnich 12 h:\n")
        for l in od_commita.splitlines():
            czesci.append("  - `%s`\n" % l)
    czesci.append("- niezacommitowane: %s\n"
                  % ("brak" if not brudne else "\n" + "\n".join(
                      "  - `%s`" % l for l in brudne.splitlines()[:MAKS_PLIKOW]) + "\n"))

    if polecenia:
        czesci.append("\n## O co prosil uzytkownik (dosłownie, ostatnie %d)\n\n"
                      % min(len(polecenia), MAKS_POLECEN))
        for t in polecenia[-MAKS_POLECEN:]:
            czesci.append("- %s\n" % t)

    if pliki:
        czesci.append("\n## Pliki tworzone i zmieniane w sesji\n\n")
        for p in pliki[:MAKS_PLIKOW]:
            czesci.append("- `%s`\n" % p)
        if len(pliki) > MAKS_PLIKOW:
            czesci.append("- ... oraz %d dalszych\n" % (len(pliki) - MAKS_PLIKOW))

    if agenci:
        czesci.append("\n## Uruchomieni agenci\n\n")
        for a in agenci:
            czesci.append("- %s\n" % a)

    if komendy:
        czesci.append("\n## Co uruchomiono (ostatnie 25)\n\n")
        for k in komendy[-25:]:
            czesci.append("- %s\n" % k)

    czesci.append("\n---\n\n## DO UZUPELNIENIA — ustalenia\n\n"
                  "_Co zostalo rozstrzygniete i na jakiej podstawie. Liczby, nie proza._\n\n")
    czesci.append("## DO UZUPELNIENIA — otwarte\n\n"
                  "_Co zostalo niedokonczone i co jest nastepnym krokiem._\n\n")
    czesci.append("## DO UZUPELNIENIA — czego nie wolno cofnac\n\n"
                  "_Decyzje i pomiary, ktore nastepna sesja moglaby niechcacy odwrocic._\n\n")
    czesci.append("## Zrodlo\n\nTranskrypt sesji: `%s`\n" % (transkrypt or "nieznany"))

    with io.open(sciezka, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(czesci))

    # Ten wydruk trafia do logu, NIE do modelu (patrz naglowek). Jest po to, zeby
    # dalo sie sprawdzic, ze hook w ogole sie wykonal — nie po to, zeby cos zlecic.
    print("PreCompact: zapisano szkielet checkpointu %s (wyzwalacz %s, %d plikow, "
          "%d polecen uzytkownika)%s"
          % (sciezka, wyzwalacz, len(pliki), len(polecenia),
             ("  UWAGA: " + powod) if powod else ""))
    print(json.dumps({"continue": True}))
    return 0


try:
    sys.exit(main())
except Exception as e:                      # hook NIGDY nie psuje sesji
    sys.stderr.write("PreCompact checkpoint: %s\n" % e)
    sys.exit(0)
