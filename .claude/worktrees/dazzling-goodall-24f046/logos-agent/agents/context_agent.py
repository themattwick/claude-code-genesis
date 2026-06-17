"""ContextAgent — wstępna ekstrakcja Zachman z opisu + bramka jakości."""
from __future__ import annotations
import json
from agents._runner import run_agent_json
from schemas.zachman import ZachmanModel


_INSTRUCTION = """Jesteś analitykiem systemów. Otrzymujesz krótki opis systemu od użytkownika.

Twoje zadanie:
1. Wyodrębnij wstępną hipotezę Zachman (7 wymiarów) z opisu — TYLKO to co napisane,
   nie dopisuj fantazji. Jeśli czegoś brak — zostaw pustą listę.
2. Oceń czy opis jest wystarczająco konkretny (>= 30 słów, zawiera domenę i cel).

Odpowiedz **wyłącznie** w formacie JSON:
{
  "quality_ok": true|false,
  "reason": "krótkie uzasadnienie oceny",
  "clarifying_questions": ["pyt 1", "pyt 2"],   // gdy quality_ok=false, max 3
  "hypothesis": {
    "domain": "np. e-commerce, fintech, healthcare",
    "entities": ["nazwy encji wykryte w opisie"],
    "actors": ["aktorzy wymienieni w opisie"],
    "rules": ["reguły/ograniczenia wymienione w opisie"],
    "events": ["zdarzenia wymienione w opisie"],
    "integrations": ["systemy zewnętrzne wymienione w opisie"],
    "tech": ["technologie wymienione w opisie"]
  }
}

Zasady:
- Cała odpowiedź po polsku
- Bez markdown, bez ```json``` — czysty JSON
- Jeśli opis ma < 30 słów lub jest abstrakcyjny ("system AI", "platforma") → quality_ok=false
"""


async def extract_context(description: str) -> dict:
    """Zwraca dict {quality_ok, reason, clarifying_questions, hypothesis}."""
    # Używamy run_agent_json, ale to zwraca Pydantic model — tu chcemy dict
    # Dlatego najpierw run_agent (text), potem manualny json.loads()
    from agents._runner import run_agent
    text = await run_agent(
        agent_name="context_agent",
        system_prompt=_INSTRUCTION,
        user_prompt=f"Opis systemu:\n\n{description}"
    )
    return json.loads(text)
