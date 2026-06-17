"""ConsistencyAgent — sprawdza pary spójności między pytaniami.

Heurystyki deterministyczne (overlap słów dla 'opposite', empty-vs-filled dla 'complement').
"""
from __future__ import annotations
from framework import CONSISTENCY_PAIRS, ConsistencyPair
from framework.consistency_pairs import find_overlap
from schemas.session import ConflictHit


def _is_filled(text: str | None) -> bool:
    if not text:
        return False
    if text.startswith("WYMAGA"):
        return False
    return len(text.strip()) >= 5


def check_consistency(answers: dict[int, str]) -> list[ConflictHit]:
    """Zwraca konflikty wykryte w parach spójności."""
    conflicts: list[ConflictHit] = []
    for pair in CONSISTENCY_PAIRS:
        a = answers.get(pair.a_id, "")
        b = answers.get(pair.b_id, "")
        a_ok = _is_filled(a)
        b_ok = _is_filled(b)

        if pair.type == "opposite":
            # Konflikt: oba wypełnione I mają overlap znaczących słów
            if a_ok and b_ok:
                overlap = find_overlap(a, b)
                if overlap:
                    conflicts.append(ConflictHit(
                        pair_title=pair.title,
                        a_id=pair.a_id,
                        b_id=pair.b_id,
                        overlap=overlap,
                        note=pair.note,
                    ))

        elif pair.type == "complement":
            # Konflikt: tylko jedno wypełnione
            if a_ok != b_ok:
                conflicts.append(ConflictHit(
                    pair_title=pair.title,
                    a_id=pair.a_id,
                    b_id=pair.b_id,
                    overlap=[],
                    note=f"{pair.note} — jedna strona pary jest pusta",
                ))

    return conflicts
