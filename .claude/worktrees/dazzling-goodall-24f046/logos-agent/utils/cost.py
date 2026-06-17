"""Bardzo zgrubne oszacowanie kosztu tokenów per faza.

Cele: dać użytkownikowi wstępny pogląd przed odpaleniem fazy,
       nie ścisła księgowość.
"""
from __future__ import annotations

# Przybliżone ceny per 1M tokenów (USD) — Gemini 2.5 (kwiecień 2026, mogą być nieaktualne)
PRICING = {
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.5-pro":   {"input": 1.25,  "output": 5.00},
}

# 1 token ≈ 4 znaki dla łaciny/polskiego
def tok(s: str) -> int:
    return max(1, len(s) // 4)


def estimate_phase(model: str, in_tokens: int, out_tokens: int) -> float:
    """Zwraca koszt w USD dla podanej liczby tokenów."""
    p = PRICING.get(model, PRICING["gemini-2.5-flash"])
    return (in_tokens / 1_000_000) * p["input"] + (out_tokens / 1_000_000) * p["output"]


def fmt_usd(usd: float) -> str:
    if usd < 0.01:
        return f"<$0.01"
    return f"${usd:.3f}"
