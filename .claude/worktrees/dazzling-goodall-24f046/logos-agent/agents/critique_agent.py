"""CritiqueAgent — krytykuje ZachmanModel: szuka sprzeczności, luk, ogólników."""
from __future__ import annotations
from schemas.zachman import ZachmanModel, CritiqueFinding
from agents._runner import run_agent_json


_INSTRUCTION = """Jesteś senior architektem dokonującym przeglądu specyfikacji systemu.
Otrzymujesz ZachmanModel JSON. Wskaż konkretne problemy — bez ogólników w samej krytyce.

Severity:
- HIGH: blokuje implementację (sprzeczna reguła, encja bez stanów, aktor bez can/cannot,
  reguła z warunkiem-ogólnikiem typu "zazwyczaj"/"zwykle")
- MEDIUM: wpływa na jakość (integracja bez SLA, event bez outcome, brak rationale dla nieodwracalnej akcji)
- LOW: kosmetyka (nazewnictwo, brak rationale dla typowej reguły)

Każde finding zawiera:
- severity
- where: dokładna lokalizacja, np. "rules.R3", "actors[2].cannot", "entities.Zamówienie.states"
- issue: co jest nie tak (1 zdanie)
- fix: konkretna sugestia naprawy (1-2 zdania)

Maksymalnie 15 findings. Priorytet: HIGH > MEDIUM > LOW.

Zwróć JSON: {"findings": [...]}
"""

_AMBIGUOUS_TERMS = {
    "zazwyczaj", "zwykle", "automatycznie", "około", "mniej więcej",
    "elastycznie", "w razie potrzeby", "odpowiednio", "intuicyjnie",
}


def _heuristic_findings(model: ZachmanModel) -> list[CritiqueFinding]:
    """Deterministyczne reguły — bez LLM."""
    out: list[CritiqueFinding] = []

    # Encje bez stanów
    for e in model.entities:
        if not e.states:
            out.append(CritiqueFinding(
                severity="high",
                where=f"entities.{e.name}.states",
                issue=f"Encja '{e.name}' nie ma zdefiniowanych stanów",
                fix="Dodaj listę stanów (np. ['utworzony', 'aktywny', 'zamknięty'])",
            ))

    # Aktorzy bez uprawnień
    for i, a in enumerate(model.actors):
        if not a.can and not a.cannot:
            out.append(CritiqueFinding(
                severity="high",
                where=f"actors[{i}].{a.name}",
                issue=f"Aktor '{a.name}' nie ma żadnego can/cannot",
                fix="Określ co może i czego nie może wykonywać",
            ))

    # Reguły-ogólniki
    for r in model.rules:
        cond_lower = r.condition.lower()
        for term in _AMBIGUOUS_TERMS:
            if term in cond_lower:
                out.append(CritiqueFinding(
                    severity="high",
                    where=f"rules.{r.id}",
                    issue=f"Warunek reguły {r.id} zawiera ogólnik: '{term}'",
                    fix=f"Zastąp '{term}' konkretnym progiem liczbowym lub warunkiem boolowskim",
                ))
                break

    # Integracje bez protocol
    for i, ig in enumerate(model.integrations):
        if not ig.protocol:
            out.append(CritiqueFinding(
                severity="medium",
                where=f"integrations[{i}].{ig.system}",
                issue=f"Integracja {ig.system} bez protokołu",
                fix="Określ protokół: REST, webhook, gRPC, SMTP, SFTP, ...",
            ))

    # Zdarzenia bez outcome
    for i, ev in enumerate(model.events):
        if not ev.outcome:
            out.append(CritiqueFinding(
                severity="medium",
                where=f"events[{i}].{ev.trigger}",
                issue=f"Zdarzenie '{ev.trigger}' bez outcome",
                fix="Określ obserwowalny rezultat akcji (np. 'email_wysłany', 'status_zaktualizowany')",
            ))

    # Reguły bez rationale (LOW)
    for r in model.rules:
        if not r.rationale:
            out.append(CritiqueFinding(
                severity="low",
                where=f"rules.{r.id}.rationale",
                issue=f"Reguła {r.id} bez uzasadnienia (rationale)",
                fix="Dodaj 1-zdaniowe uzasadnienie biznesowe",
            ))

    return out


async def critique(model: ZachmanModel) -> list[CritiqueFinding]:
    """Łączy heurystyki + LLM analysis."""
    heuristic = _heuristic_findings(model)

    # LLM dla głębszych sprzeczności
    prompt = f"""Przejrzyj ten ZachmanModel i wskaż problemy które nie są oczywistymi
brakami struktury (te już znalazłem heurystykami). Skup się na:
- sprzecznych regułach
- aktorach z konfliktowymi can/cannot
- relacjach między encjami niespójnych z regułami
- brakujących encjach implikowanych przez reguły

ZachmanModel:
{model.model_dump_json(indent=2)}

Zwróć JSON {{"findings": [...]}}"""
    try:
        # run_agent_json wymaga schematu — tworzymy na lotu
        from pydantic import BaseModel
        class CritiqueReport(BaseModel):
            findings: list[CritiqueFinding] = []

        report = await run_agent_json(
            agent_name="critique_agent",
            system_prompt=_INSTRUCTION,
            user_prompt=prompt,
            schema=CritiqueReport,
        )
        llm_findings = report.findings
    except Exception as e:
        from utils.ui import console
        console.print(f"[yellow]⚠ CritiqueAgent LLM failed: {e}[/yellow]")
        llm_findings = []

    # Łącz, sortuj: high → medium → low
    sev_order = {"high": 0, "medium": 1, "low": 2}
    all_findings = heuristic + llm_findings
    all_findings.sort(key=lambda f: sev_order.get(f.severity, 3))
    return all_findings[:15]
