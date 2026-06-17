"""Detekcja Ambiguity Tax — słów które ukrywają niesprecyzowane założenia."""
from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class RiskyWord:
    word: str
    why: str  # dlaczego to słowo jest ryzykowne


RISKY_WORDS: list[RiskyWord] = [
    # Fałszywe absoluty
    RiskyWord("zawsze",         "fałszywy absolut — co jeśli nie?"),
    RiskyWord("nigdy",          "fałszywy absolut — czy na pewno bez wyjątku?"),
    RiskyWord("wszyscy",        "fałszywy absolut — czy bez wyjątków?"),
    RiskyWord("nikt",           "fałszywy absolut — czy bez wyjątków?"),
    RiskyWord("wszystko",       "fałszywy absolut — co dokładnie?"),
    RiskyWord("nic",            "fałszywy absolut — czy na pewno?"),

    # Ukryta logika
    RiskyWord("automatycznie",  "ukryta logika — kto/co wyzwala tę akcję?"),
    RiskyWord("samo",           "ukryta logika — co to znaczy 'samo'?"),
    RiskyWord("system",         "kto w systemie? jaki komponent konkretnie?"),
    RiskyWord("aplikacja",      "która część aplikacji konkretnie?"),

    # Nieokreślone zależności
    RiskyWord("zależy",         "nieokreślona zależność — od czego dokładnie?"),
    RiskyWord("w razie potrzeby", "nieokreślony warunek — jaka potrzeba?"),
    RiskyWord("jeśli trzeba",   "nieokreślony warunek — kto decyduje?"),
    RiskyWord("opcjonalnie",    "kiedy wybór tej opcji?"),

    # Brak precyzji ilościowej
    RiskyWord("mniej więcej",   "brak precyzji — podaj konkretną wartość"),
    RiskyWord("około",          "brak precyzji — podaj konkretną wartość"),
    RiskyWord("kilka",          "brak precyzji — ile dokładnie?"),
    RiskyWord("kilkanaście",    "brak precyzji — ile dokładnie?"),
    RiskyWord("dużo",           "brak precyzji — ile to dużo?"),
    RiskyWord("mało",           "brak precyzji — ile to mało?"),
    RiskyWord("szybko",         "brak precyzji — ile milisekund?"),
    RiskyWord("wolno",          "brak precyzji — jaki czas akceptowalny?"),
    RiskyWord("często",         "brak precyzji — co ile?"),
    RiskyWord("rzadko",         "brak precyzji — co ile?"),

    # Ogólniki temporalne
    RiskyWord("zazwyczaj",      "ogólnik temporalny — kiedy nie 'zazwyczaj'?"),
    RiskyWord("zwykle",         "ogólnik temporalny — kiedy nie 'zwykle'?"),
    RiskyWord("czasami",        "ogólnik temporalny — w jakich warunkach?"),
    RiskyWord("od czasu do czasu", "ogólnik temporalny — co ile?"),
    RiskyWord("czasem",         "ogólnik temporalny — w jakich warunkach?"),

    # Ogólniki jakościowe
    RiskyWord("odpowiednio",    "ogólnik jakościowy — odpowiednio do czego?"),
    RiskyWord("właściwie",      "ogólnik jakościowy — właściwie czyli jak?"),
    RiskyWord("elastycznie",    "ogólnik jakościowy — co to znaczy elastycznie?"),
    RiskyWord("inteligentnie",  "ogólnik jakościowy — jaka konkretna logika?"),
    RiskyWord("optymalnie",     "ogólnik jakościowy — według jakiego kryterium?"),
    RiskyWord("łatwo",          "ogólnik jakościowy — łatwo dla kogo?"),
    RiskyWord("intuicyjnie",    "ogólnik jakościowy — według jakich heurystyk?"),
]

RISKY_BY_WORD = {r.word.lower(): r for r in RISKY_WORDS}


def detect_risky_words(text: str) -> list[RiskyWord]:
    """Zwraca unikalne dopasowania risky words w tekście (case-insensitive)."""
    if not text:
        return []
    found: dict[str, RiskyWord] = {}
    text_lower = text.lower()
    for risky in RISKY_WORDS:
        # word boundary: '\b' nie działa dobrze dla polskich znaków,
        # więc używamy lookarounds wykluczających litery
        pattern = r"(?<![a-ząćęłńóśźż])" + re.escape(risky.word.lower()) + r"(?![a-ząćęłńóśźż])"
        if re.search(pattern, text_lower):
            found[risky.word] = risky
    return list(found.values())
