"""Konfiguracja: modele, limity, ścieżki, backend."""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
SESSION_DIR = OUTPUT_DIR / ".session"
LOGS_DIR = ROOT / "logs"
EXAMPLES_DIR = ROOT / "examples"

OUTPUT_DIR.mkdir(exist_ok=True)
SESSION_DIR.mkdir(exist_ok=True, parents=True)
LOGS_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────
# Modele per agent (domyślnie Gemini; nadpisywane przez --model flag)
# Flash dla równoległych/tanich; Pro dla głębokiego reasoning + structured.
#
# Gdy użytkownik poda --model ollama/mistral lub --model gpt-4o,
# wszystkie agenty używają podanego modelu (override MODELS dict).
# ─────────────────────────────────────────────────────────────────────────
MODELS = {
    "default":     "gemini-2.5-flash",   # fallback gdy brak wpisu per agent
    "context":     "gemini-2.5-flash",
    "category":    "gemini-2.5-flash",
    "interview":   "gemini-2.5-flash",
    "synthesis":   "gemini-2.5-pro",     # KLUCZOWY: structured output
    "critique":    "gemini-2.5-pro",
    "risk":        "gemini-2.5-flash",
    "consistency": "gemini-2.5-flash",
    "export":      "gemini-2.5-flash",
}


# ─────────────────────────────────────────────────────────────────────────
# Limity
# ─────────────────────────────────────────────────────────────────────────
MAX_AMBIGUITY_ITERATIONS = 2     # ile razy można wrócić z CP3 do interview
MAX_INTERVIEW_QUESTIONS = 15
MIN_DESCRIPTION_TOKENS = 30      # bramka jakości w CP0 (przybliżone słowa)

# Cele jakościowe
TARGET_AMBIGUITY_SCORE = 0.30    # poniżej = dobrze opisany system
