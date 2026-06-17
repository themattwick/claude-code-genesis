"""Pary spójności między pytaniami z różnych kategorii.

Każda para ma typ:
- 'opposite' — pytania logicznie przeciwstawne (dozwolone vs zakazane);
  konflikt = nakładające się znaczące słowa
- 'complement' — pytania komplementarne (kto + kiedy);
  problem = jedno odpowiedziane, drugie nie
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import re


PairType = Literal["opposite", "complement"]


@dataclass(frozen=True)
class ConsistencyPair:
    title: str
    a_id: int        # 1-based question id
    b_id: int
    type: PairType
    note: str        # opis dla człowieka


CONSISTENCY_PAIRS: list[ConsistencyPair] = [
    # ── opposite (CO) ────────────────────────────────────────────────────
    ConsistencyPair(
        "Zmiany dozwolone vs zakazane",
        a_id=8, b_id=9, type="opposite",
        note="Te same operacje nie mogą być jednocześnie dozwolone i zakazane",
    ),
    ConsistencyPair(
        "Informacje wymagane vs opcjonalne",
        a_id=5, b_id=6, type="opposite",
        note="Pole nie może być jednocześnie wymagane i opcjonalne",
    ),
    ConsistencyPair(
        "Co istnieje vs czego nie ma",
        a_id=3, b_id=4, type="opposite",
        note="Encja nie może być jednocześnie obecna i zabroniona",
    ),

    # ── opposite (GDZIE / KTO) ───────────────────────────────────────────
    ConsistencyPair(
        "Gdzie dane mogą trafiać vs gdzie nie mogą",
        a_id=13, b_id=14, type="opposite",
        note="Lokalizacje docelowe nie mogą się pokrywać",
    ),
    ConsistencyPair(
        "Kto ma dostęp vs kto nie ma",
        a_id=32, b_id=36, type="opposite",
        note="Aktor nie może jednocześnie widzieć i nie widzieć tych samych danych",
    ),
    ConsistencyPair(
        "Kto może działać vs komu nigdy nie wolno",
        a_id=33, b_id=40, type="opposite",
        note="Aktor nie może mieć permisji której nigdy nie ma mieć",
    ),

    # ── complement: KTO ↔ KIEDY ──────────────────────────────────────────
    ConsistencyPair(
        "Kto tworzy ↔ Kiedy coś jest tworzone",
        a_id=33, b_id=21, type="complement",
        note="Jeśli wiemy kto tworzy, musimy wiedzieć kiedy (i odwrotnie)",
    ),
    ConsistencyPair(
        "Kto aktualizuje ↔ Kiedy aktualizowane",
        a_id=34, b_id=22, type="complement",
        note="Jeśli wiemy kto aktualizuje, musimy wiedzieć kiedy",
    ),
    ConsistencyPair(
        "Kto usuwa ↔ Kiedy usuwane",
        a_id=35, b_id=23, type="complement",
        note="Operacja usuwania wymaga aktora i triggera czasowego",
    ),

    # ── complement: KTO ↔ DLACZEGO ───────────────────────────────────────
    ConsistencyPair(
        "Kto usuwa ↔ Dlaczego nieodwracalne",
        a_id=35, b_id=48, type="complement",
        note="Jeśli usuwanie istnieje, musi być uzasadnione dlaczego nieodwracalne",
    ),
    ConsistencyPair(
        "Kto zatwierdza ↔ Dlaczego potrzebne",
        a_id=37, b_id=44, type="complement",
        note="Workflow zatwierdzeń musi mieć uzasadnienie",
    ),
    ConsistencyPair(
        "Gdzie dostęp ograniczony ↔ Kto nie ma dostępu",
        a_id=17, b_id=36, type="complement",
        note="Ograniczenia geograficzne i ograniczenia per-aktor muszą się pokrywać semantycznie",
    ),

    # ── complement: KIEDY ↔ JAK ──────────────────────────────────────────
    ConsistencyPair(
        "Kiedy odpowiedź natychmiast ↔ Jak system reaguje",
        a_id=26, b_id=51, type="complement",
        note="Wymaganie natychmiastowości musi być spójne z mechanizmem reakcji",
    ),
    ConsistencyPair(
        "Kiedy retry ↔ Jak odzyskuje po awarii",
        a_id=28, b_id=56, type="complement",
        note="Strategia retry musi się łączyć z mechanizmem recovery",
    ),

    # ── complement: CO/CO_JESLI ──────────────────────────────────────────
    ConsistencyPair(
        "Czego nie może być ↔ Dlaczego blokowane",
        a_id=4, b_id=44, type="complement",
        note="Każdy zakaz musi mieć uzasadnienie",
    ),
    ConsistencyPair(
        "Jak obsługuje błędy ↔ Gdzie awarie",
        a_id=54, b_id=18, type="complement",
        note="Strategia error handlingu musi pokrywać wszystkie miejsca awarii",
    ),

    # ── complement: ILE ↔ CO_JESLI ───────────────────────────────────────
    ConsistencyPair(
        "Ile użytkowników jednocześnie ↔ Co jeśli przeciążony",
        a_id=61, b_id=74, type="complement",
        note="Limit obciążenia musi mieć zdefiniowane zachowanie po przekroczeniu",
    ),
    ConsistencyPair(
        "Czas odpowiedzi ↔ Co jeśli SLA niespełnione",
        a_id=62, b_id=79, type="complement",
        note="SLA musi mieć escalation path",
    ),

    # ── complement: INTEGRACJE ↔ CO_JESLI ────────────────────────────────
    ConsistencyPair(
        "Integracje krytyczne ↔ Co jeśli API niedostępne",
        a_id=100, b_id=71, type="complement",
        note="Każda krytyczna integracja musi mieć fallback/degraded mode",
    ),
    ConsistencyPair(
        "Outbound systemy ↔ Granice odpowiedzialności",
        a_id=92, b_id=99, type="complement",
        note="Każdy outbound musi mieć jasne granice odpowiedzialności",
    ),

    # ── complement: JAK_MIERZYC ↔ CO_JESLI ───────────────────────────────
    ConsistencyPair(
        "Alerty SEV-1 ↔ Co jeśli SLA niespełnione",
        a_id=84, b_id=79, type="complement",
        note="Alerty muszą się odpalić zgodnie ze ścieżką escalation SLA",
    ),
]


# ─────────────────────────────────────────────────────────────────────────
# Heurystyka: stop words (PL) — żeby nie liczyć "z", "i", "ale" jako overlap
# ─────────────────────────────────────────────────────────────────────────
STOP_WORDS = {
    "i", "oraz", "lub", "albo", "ale", "więc", "jednak", "też", "także",
    "to", "ta", "te", "ten", "tej", "tym", "ich", "jego", "jej",
    "z", "ze", "w", "we", "do", "na", "po", "od", "za", "pod", "nad",
    "być", "jest", "są", "może", "musi", "powinien", "powinna",
    "który", "która", "które", "którzy", "których", "któremu",
    "co", "kto", "gdzie", "kiedy", "jak", "dlaczego", "ile",
    "nie", "tak", "się", "by", "aby", "żeby",
    "system", "systemu", "systemy", "systemem",
    "dane", "danych", "danym", "danymi",
    "user", "users", "użytkownik", "użytkownika", "użytkownicy",
    "wszystko", "wszystkie", "każdy", "każda", "każde",
    "tylko", "również", "żaden", "żadna",
    "można", "trzeba", "należy", "wolno",
    "operacja", "operacje", "działanie", "działania",
    "informacja", "informacje",
}


def _tokenize_significant(text: str) -> set[str]:
    """Wyciąga znaczące słowa (>4 znaki, nie stop words)."""
    if not text:
        return set()
    words = re.findall(r"[a-ząćęłńóśźż]+", text.lower())
    return {w for w in words if len(w) > 4 and w not in STOP_WORDS}


def find_overlap(answer_a: str, answer_b: str) -> list[str]:
    """Zwraca słowa znaczące występujące w obu odpowiedziach."""
    a = _tokenize_significant(answer_a)
    b = _tokenize_significant(answer_b)
    return sorted(a & b)
