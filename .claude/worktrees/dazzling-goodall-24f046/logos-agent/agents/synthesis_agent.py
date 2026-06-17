"""SynthesisAgent — konwertuje 100 Q&A → ZachmanModel JSON."""
from __future__ import annotations
from datetime import date
import json
from framework import question_by_id
from schemas.zachman import ZachmanModel, Entity, Actor, Rule, Event, Integration, Scale
from agents._runner import run_agent_json


_INSTRUCTION = """Jesteś analitykiem systemów. Otrzymujesz odpowiedzi na pytania specyfikacyjne i musisz wypełnić poniższy szablon JSON.

ZASADY:
- Wypełnij DOKŁADNIE ten szablon — nie zmieniaj nazw pól, nie dodawaj nowych.
- entities: każda encja musi mieć niepustą listę states.
- actors: każdy aktor musi mieć niepuste can lub cannot.
- rules: każda reguła musi mieć konkretny condition i action (nie ogólniki).
- integrations: direction to dokładnie "inbound", "outbound" lub "bidirectional".
- ambiguity_score: liczba 0.0-1.0 (procent ogólnych odpowiedzi).
- Odpowiedz WYŁĄCZNIE JSON bez żadnego tekstu przed ani po.

SZABLON DO WYPEŁNIENIA:
{
  "system": "NAZWA_SYSTEMU",
  "generated": "YYYY-MM-DD",
  "ambiguity_score": 0.0,
  "entities": [
    {"name": "ENCJA", "states": ["stan1", "stan2"], "relationships": ["relacja"], "fields": ["pole1"]}
  ],
  "actors": [
    {"name": "AKTOR", "can": ["akcja1"], "cannot": ["niedozwolona1"]}
  ],
  "rules": [
    {"id": "R1", "condition": "konkretny_warunek", "action": "konkretna_akcja", "rationale": "dlaczego"}
  ],
  "events": [
    {"trigger": "zdarzenie", "action": "akcja", "outcome": "rezultat"}
  ],
  "integrations": [
    {"system": "NazwaSystemu", "direction": "inbound", "protocol": "REST", "critical": true}
  ],
  "tech_constraints": ["technologia1", "ograniczenie2"],
  "scale": {"concurrent_users": null, "response_time_ms": null, "uptime_pct": null, "data_volume_per_day": null}
}
"""


def _format_answers(answers: dict[int, str]) -> str:
    lines = []
    for qid in sorted(answers.keys()):
        ans = answers.get(qid, "")
        if not ans or ans.startswith("WYMAGA"):
            continue
        q = question_by_id(qid)
        lines.append(f"[{q.category_id} | tag:{q.zachman_tag}] P{qid}: {q.text}\n  → {ans}")
    return "\n\n".join(lines)


def _fallback_model(system_name: str, answers: dict[int, str]) -> ZachmanModel:
    """Minimalny ZachmanModel z surowych Q&A gdy LLM nie da poprawnego JSON."""
    today = date.today().isoformat()
    # Zbierz najważniejsze odpowiedzi jako tech_constraints
    constraints = []
    for qid in sorted(answers.keys()):
        ans = answers.get(qid, "")
        if ans and not ans.startswith("WYMAGA") and len(ans.split()) >= 5:
            constraints.append(f"P{qid}: {ans[:120]}")
    return ZachmanModel(
        system=system_name,
        generated=today,
        ambiguity_score=0.5,
        entities=[Entity(name="(fallback — synteza nieudana)", states=["nieznany"])],
        actors=[],
        rules=[],
        events=[],
        integrations=[],
        tech_constraints=constraints[:30],
        scale=Scale(),
    )


async def synthesize(system_name: str, answers: dict[int, str]) -> ZachmanModel:
    prompt = f"""System: {system_name}
Data: {date.today().isoformat()}

Odpowiedzi na pytania specyfikacyjne (pomiń puste i WYMAGA UZUPEŁNIENIA):

{_format_answers(answers)}

Wypełnij podany szablon JSON danymi z powyższych odpowiedzi. Nie zmieniaj nazw pól. Odpowiedz TYLKO JSON."""

    try:
        return await run_agent_json(
            agent_name="synthesis_agent",
            system_prompt=_INSTRUCTION,
            user_prompt=prompt,
            schema=ZachmanModel,
        )
    except Exception:
        return _fallback_model(system_name, answers)
