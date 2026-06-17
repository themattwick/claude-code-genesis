"""InterviewAgent — analizuje luki i generuje celowane pytania do człowieka."""
from __future__ import annotations
import json
import re
from config import MAX_INTERVIEW_QUESTIONS
from framework import question_by_id
from schemas.session import GapQuestion
from agents._runner import run_agent


_INSTRUCTION = f"""Jesteś analitykiem specyfikacji. Otrzymujesz listę odpowiedzi na 100 pytań
specyfikacyjnych. Twoje zadanie: wykryć luki i ZADAĆ celowane pytania uzupełniające.

Lukę identyfikujesz gdy odpowiedź:
- zawiera "WYMAGA UZUPEŁNIENIA"
- jest pusta lub bardzo krótka (<10 słów)
- zawiera ogólniki: "automatycznie", "zazwyczaj", "elastycznie", "około"
- jest sprzeczna lub niejasna

Generuj pytania:
- Konkretne (jedno wymaganie per pytanie)
- Po polsku, tonem rozmowy ("Czy klient...?", "Jaki próg...?")
- Powiąż z numerami pytań z głównej listy (target_question_ids)
- Maksymalnie {MAX_INTERVIEW_QUESTIONS} pytań

Odpowiedz **wyłącznie** w formacie JSON:
{{
  "gaps": [
    {{
      "question": "Czy klient może anulować zamówienie po opłaceniu?",
      "target_question_ids": [9, 35]
    }}
  ]
}}

Bez markdown, czysty JSON.
"""


def _parse_gaps_json(text: str) -> dict:
    """Parsuje JSON z odpowiedzi modelu — z fallbackiem regex dla non-Gemini."""
    if not text or not text.strip():
        return {"gaps": []}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {"gaps": []}
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {"gaps": []}


def _format_answers_for_prompt(answers: dict[int, str]) -> str:
    lines = []
    for qid in sorted(answers.keys()):
        q = question_by_id(qid)
        lines.append(f"P{qid} [{q.category_id}]: {q.text}\n  → {answers[qid] or '(brak)'}")
    return "\n\n".join(lines)


async def find_gaps(answers: dict[int, str]) -> list[GapQuestion]:
    """Główne wywołanie po Checkpoint 1."""
    prompt = f"""Odpowiedzi na pytania specyfikacyjne:

{_format_answers_for_prompt(answers)}

Wykryj luki i zadaj pytania uzupełniające."""

    text = await run_agent(
        agent_name="interview_agent",
        system_prompt=_INSTRUCTION,
        user_prompt=prompt,
    )
    data = _parse_gaps_json(text)
    return [GapQuestion(**g) for g in data.get("gaps", [])][:MAX_INTERVIEW_QUESTIONS]


async def find_focused_gaps(
    critique: list[dict],
    risks: list[dict],
    answers: dict[int, str],
) -> list[GapQuestion]:
    """Dla pętli redukcji niejednoznaczności w CP3 — pytania o konkretne findings."""
    prompt = f"""Odpowiedzi:
{_format_answers_for_prompt(answers)}

Krytyka modelu (CritiqueAgent):
{json.dumps(critique, ensure_ascii=False, indent=2)}

Ryzyka (RiskAgent):
{json.dumps(risks, ensure_ascii=False, indent=2)}

Wygeneruj WĄSKĄ listę pytań (max 10) ukierunkowanych TYLKO na rozwiązanie tych konkretnych
problemów. Nie zadawaj pytań o tematy poza krytyką i ryzykami."""

    text = await run_agent(
        agent_name="interview_agent_focused",
        system_prompt=_INSTRUCTION,
        user_prompt=prompt,
    )
    data = _parse_gaps_json(text)
    return [GapQuestion(**g) for g in data.get("gaps", [])][:10]
