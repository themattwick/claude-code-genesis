"""RiskAgent — skanuje odpowiedzi pod kątem Ambiguity Tax (risky words).

Czysto deterministyczny — używa słownika z framework/risky_words.py.
Brak wywołań LLM = darmowy i szybki.
"""
from __future__ import annotations
from framework import detect_risky_words
from schemas.session import RiskHit


def scan_risks(answers: dict[int, str]) -> list[RiskHit]:
    """Zwraca listę trafień risky words per pytanie."""
    hits: list[RiskHit] = []
    for qid, answer in answers.items():
        if not answer:
            continue
        for risky in detect_risky_words(answer):
            hits.append(RiskHit(question_id=qid, word=risky.word, why=risky.why))
    return hits


def compute_ambiguity_score(answers: dict[int, str]) -> float:
    """Procent odpowiedzi zawierających przynajmniej jedno risky word."""
    if not answers:
        return 0.0
    risky_count = sum(
        1 for ans in answers.values()
        if ans and detect_risky_words(ans)
    )
    return risky_count / len(answers)
