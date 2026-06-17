"""CategoryAgent — proponuje drafty 10 odpowiedzi dla jednej kategorii."""
from __future__ import annotations
import asyncio
import json
from framework import Category, ALL_QUESTIONS, questions_for_mode, category_by_id
from framework.questions import Question
from agents._runner import run_agent


def _build_instruction(cat: Category, questions: list[Question]) -> str:
    examples = "\n".join(
        f'  P{q.id}: "{q.text}"\n  Przykład dobrej odpowiedzi: "{q.example}"'
        for q in questions
    )
    return f"""Jesteś ekspertem ds. specyfikacji systemów. Twoje zadanie: zaproponować
DRAFT odpowiedzi na pytania kategorii **{cat.name} — {cat.sub}** dla opisanego systemu.

Cel kategorii: {cat.desc}

Zasady:
- Każda odpowiedź MA BYĆ KONKRETNA: liczby, nazwy, warunki, progi.
- Unikaj słów: "automatycznie", "zazwyczaj", "elastycznie", "około", "kilka" — to ukryte założenia.
- Jeśli na podstawie opisu i kontekstu nie można odpowiedzieć — napisz dokładnie:
  "WYMAGA UZUPEŁNIENIA: [co konkretnie potrzebne]"
- Odpowiedź 2–4 zdania, po polsku.

Pytania do odpowiedzenia (z przykładami dobrych odpowiedzi):

{examples}

Odpowiedz **wyłącznie** w formacie JSON:
{{
  "answers": {{
{json_keys_template(questions)}
  }}
}}

Bez markdown, bez ```json```, tylko czysty JSON. Klucze to numery pytań jako stringi.
"""


def json_keys_template(questions: list[Question]) -> str:
    return ",\n".join(f'    "{q.id}": "draft odpowiedzi na P{q.id}"' for q in questions)


async def generate_drafts_for_category(
    cat_id: str,
    description: str,
    zachman_context: dict,
    mode: str = "full",
) -> dict[int, str]:
    """Generuje drafty dla jednej kategorii. Zwraca {qid: answer}."""
    cat = category_by_id(cat_id)
    qs = [q for q in questions_for_mode(mode) if q.category_id == cat_id]
    if not qs:
        return {}

    instruction = _build_instruction(cat, qs)

    prompt = f"""Opis systemu:
{description}

Wstępna hipoteza Zachman (z ContextAgent):
{json.dumps(zachman_context, ensure_ascii=False, indent=2)}

Wygeneruj drafty dla kategorii {cat.name}."""

    text = await run_agent(
        agent_name=f"category_{cat_id}",
        system_prompt=instruction,
        user_prompt=prompt,
    )
    parsed = json.loads(text)
    answers = parsed.get("answers", {})
    # Klucze JSON są stringami → konwertuj na int
    return {int(k): v for k, v in answers.items()}


async def generate_all_drafts(
    description: str,
    zachman_context: dict,
    mode: str = "full",
) -> dict[int, str]:
    """Uruchamia wszystkie kategorie równolegle."""
    qs = questions_for_mode(mode)
    cat_ids = list({q.category_id for q in qs})

    results = await asyncio.gather(
        *[generate_drafts_for_category(cid, description, zachman_context, mode)
          for cid in cat_ids],
        return_exceptions=True,
    )

    merged: dict[int, str] = {}
    for r in results:
        if isinstance(r, Exception):
            # Loguj ale nie przerywaj — pojedyncza kategoria może paść
            from utils.ui import console
            console.print(f"[red]✗ Kategoria padła:[/red] {r}")
            continue
        merged.update(r)
    return merged
