#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hook SessionStart (matcher: compact) — kaze dokonczyc checkpoint po kompaktowaniu.

Druga polowa mechanizmu; pierwsza to `precompact_checkpoint.py`.

PODZIAL PRACY I JEGO POWOD. `PreCompact` zapisuje szkielet, ale jego stdout NIE
dociera do modelu — kontekst wstrzykuja wylacznie `SessionStart`, `UserPromptSubmit`,
`UserPromptExpansion` i `PostModelSwitch` (dokumentacja Anthropic). Dlatego polecenie
uzupelnienia idzie stad: `SessionStart` z matcherem `compact` uruchamia sie zaraz PO
kompaktowaniu, a jego stdout jest udokumentowana droga wstrzykniecia kontekstu.

Efekt uboczny okazal sie zaleta: model dostaje polecenie, gdy ma przed soba swieze
streszczenie sesji — czyli moze napisac ustalenia lepiej, niz gdyby pisal je w polowie
przerwanej tury.

⚠️ MILCZY, GDY NIE MA CO ROBIC. Jesli zaden szkielet nie czeka na uzupelnienie, hook
nie wypisuje nic. Komunikat przy kazdym starcie sesji bylby szumem, a szum jest
jedynym pewnym sposobem, zeby kontrola przestala byc czytana.

⚠️ NIGDY NIE PRZERYWA STARTU SESJI. Kod wyjscia zawsze 0.
"""
import io
import json
import os
import sys

# Konsola Windows domyslnie nie jest UTF-8, a wyjscie hooka trafia do Claude Code.
# Bez tego polskie znaki wychodza jako krzaki — sprawdzone, nie zalozone.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ZNACZNIK = "DO UZUPELNIENIA"
MAKS_WIEK_DNI = 3


def bezpiecznie(f, domyslne):
    try:
        return f()
    except Exception:
        return domyslne


def znajdz_katalog(cwd):
    """Tylko projekt, ktory hook nam podal. NIGDY os.getcwd() — patrz blizniaczy
    komentarz w `precompact_checkpoint.py`. Hook wisi globalnie, wiec katalog
    roboczy procesu potrafi wskazywac zupelnie inne repozytorium niz sesja."""
    for k in (os.environ.get("CLAUDE_PROJECT_DIR"), cwd):
        if not k:
            continue
        p = os.path.join(k, "BRAIN", "checkpoints")
        if os.path.isdir(p):
            return p
    return None


def niedokonczone(kat):
    """Szkielety, ktore wciaz maja puste sekcje. Pusta znaczy: po naglowku sekcji
    jest juz tylko kursywa-podpowiedz albo nastepny naglowek."""
    import time
    out = []
    teraz = time.time()
    for f in sorted(os.listdir(kat), reverse=True):
        if not f.endswith("-przed-kompaktem.md"):
            continue
        p = os.path.join(kat, f)
        if teraz - os.path.getmtime(p) > MAKS_WIEK_DNI * 86400:
            continue
        t = bezpiecznie(lambda: io.open(p, encoding="utf-8").read(), "")
        if ZNACZNIK not in t:
            continue
        puste = 0
        for kawalek in t.split("## " + ZNACZNIK)[1:]:
            tresc = kawalek.split("\n## ")[0]
            linie = [l.strip() for l in tresc.splitlines()[1:] if l.strip()]
            istotne = [l for l in linie if not (l.startswith("_") and l.endswith("_"))]
            if not istotne:
                puste += 1
        if puste:
            out.append((p, puste))
    return out


def main():
    surowe = bezpiecznie(lambda: sys.stdin.read(), "")
    dane = bezpiecznie(lambda: json.loads(surowe), {}) or {}
    kat = znajdz_katalog(dane.get("cwd"))
    if not kat:
        return 0

    czekajace = bezpiecznie(lambda: niedokonczone(kat), [])
    if not czekajace:
        return 0            # cisza, gdy nie ma co robic

    p, puste = czekajace[0]
    print(
        "ZALEGLY CHECKPOINT PRZED KOMPAKTOWANIEM.\n"
        "Hook `PreCompact` zapisal szkielet: %s\n"
        "Warstwa deterministyczna jest juz w nim — dosłowne polecenia uzytkownika, "
        "pliki dotkniete w sesji, uruchomione komendy i stan repozytorium.\n"
        "Zostalo %d sekcji oznaczonych `%s`, ktorych skrypt wyliczyc nie moze: "
        "ustalenia, sprawy otwarte, czego nie wolno cofnac.\n\n"
        "Uzupelnij je TERAZ, zanim zaczniesz nowa prace — masz przed soba swieze "
        "streszczenie sesji, a za godzine juz go nie bedzie. Pisz liczbami i sciezkami, "
        "nie proza: checkpoint sluzy sesji, ktora nie bedzie pamietac niczego. "
        "Nie zgaduj tego, czego w streszczeniu nie ma — napisz, ze nie wiadomo.\n"
        "WYWOLAJ TERAZ SKILL `brain-ops` (narzedziem Skill) i dokoncz checkpoint "
        "jego procedura — hook sam skilla nie uruchamia i uruchomic nie moze, "
        "bo jest poleceniem powloki, a nie tura rozmowy. Skrypt zrobil wylacznie "
        "warstwe deterministyczna; reszta wymaga sadu, czyli modelu.\n"
        "Na koncu przebuduj BRAIN/INDEX.md."
        % (p, puste, ZNACZNIK))
    return 0


try:
    sys.exit(main())
except Exception as e:
    sys.stderr.write("SessionStart checkpoint: %s\n" % e)
    sys.exit(0)
