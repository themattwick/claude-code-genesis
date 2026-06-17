"""ExportAgent — generuje 3 pliki wyjściowe:
1. <slug>-logos.md         — spec dla ludzi (pytania + odpowiedzi + adnotacje ryzyk)
2. <slug>-contract.json    — AI's Contract (ZachmanModel jako JSON)
3. <slug>-artifacts.md     — draft entities, rules, events, permissions

Czysto deterministyczny (Python templates) — bez LLM.
"""
from __future__ import annotations
from datetime import date
from pathlib import Path
from schemas.zachman import ZachmanModel
from schemas.session import SessionState
from framework import (
    ALL_QUESTIONS, CATEGORIES, question_by_id, category_by_id, detect_risky_words,
)
from config import OUTPUT_DIR


def _format_answer_with_risks(qid: int, answer: str) -> str:
    if not answer:
        return "_Pominięto_"
    out = answer.strip()
    risks = detect_risky_words(answer)
    if risks:
        words = ", ".join(f"`{r.word}`" for r in risks)
        out += f"\n\n> ⚠ **Ambiguity Tax:** {words} — rozważ doprecyzowanie."
    return out


def _render_logos_md(state: SessionState, model: ZachmanModel) -> str:
    lines: list[str] = []
    lines.append(f"# {state.system_name} — Specyfikacja Logos Agent")
    lines.append(f"Wygenerowano: {date.today().isoformat()} | "
                 f"Tryb: {state.mode} | Ambiguity Score: {model.ambiguity_score:.2f}")
    lines.append("")
    if state.description:
        lines.append("## Opis systemu")
        lines.append(state.description.strip())
        lines.append("")
    lines.append("---")
    lines.append("")

    # Pytania per kategoria
    answers = state.final_answers or state.reviewed
    for cat in CATEGORIES:
        cat_questions = [q for q in ALL_QUESTIONS
                         if q.category_id == cat.id and q.id in answers]
        if not cat_questions:
            continue
        lines.append(f"## {cat.name} — {cat.sub}")
        lines.append("")
        for q in cat_questions:
            ans = answers.get(q.id, "")
            lines.append(f"### P{q.id}: {q.text}")
            lines.append(_format_answer_with_risks(q.id, ans))
            lines.append("")

    # Zachman summary
    lines.append("---")
    lines.append("## Zachman Summary")
    lines.append("")
    lines.append("| Wymiar       | Wykryto |")
    lines.append("|--------------|---------|")
    lines.append(f"| Encje        | {len(model.entities)} ({', '.join(e.name for e in model.entities[:5])}) |")
    lines.append(f"| Aktorzy      | {len(model.actors)} ({', '.join(a.name for a in model.actors[:5])}) |")
    lines.append(f"| Reguły       | {len(model.rules)} |")
    lines.append(f"| Zdarzenia    | {len(model.events)} |")
    lines.append(f"| Integracje   | {len(model.integrations)} ({', '.join(i.system for i in model.integrations[:5])}) |")
    lines.append("")

    # Konflikty i ryzyka
    if state.conflicts:
        lines.append("## Wykryte konflikty spójności")
        for c in state.conflicts:
            lines.append(f"- **{c.pair_title}** (P{c.a_id} ↔ P{c.b_id})  ")
            if c.overlap:
                lines.append(f"  Nakładające się słowa: {', '.join(f'`{w}`' for w in c.overlap)}")
            lines.append(f"  _{c.note}_")
        lines.append("")

    if state.critique:
        lines.append("## Krytyka (CritiqueAgent)")
        for f in state.critique:
            sev = f.get("severity", "low").upper()
            lines.append(f"- **{sev}** `{f.get('where', '')}` — {f.get('issue', '')}  ")
            if f.get("fix"):
                lines.append(f"  → _{f['fix']}_")
        lines.append("")

    lines.append("---")
    lines.append("_Wygenerowano przez Logos Agent_")
    return "\n".join(lines)


def _render_artifacts_md(state: SessionState, model: ZachmanModel) -> str:
    lines = [f"# {state.system_name} — Draft Artifacts", ""]

    # Entity Model
    lines += ["## Entity Model", "", "| Encja | Stany | Relacje |", "|-------|-------|---------|"]
    for e in model.entities:
        states = ", ".join(e.states) if e.states else "_brak_"
        rels = "; ".join(e.relationships) if e.relationships else "_brak_"
        lines.append(f"| {e.name} | {states} | {rels} |")
    lines.append("")

    # Permission Matrix
    lines += ["## Permission Matrix", ""]
    if model.actors:
        lines += ["| Aktor | Może | Nie może |", "|-------|------|----------|"]
        for a in model.actors:
            can = "; ".join(a.can) if a.can else "_(brak listy)_"
            cannot = "; ".join(a.cannot) if a.cannot else "_(brak ograniczeń)_"
            lines.append(f"| **{a.name}** | {can} | {cannot} |")
    lines.append("")

    # Business Rules
    lines += ["## Business Rules (IF-THEN)", ""]
    for r in model.rules:
        lines.append(f"- **{r.id}**: IF `{r.condition}` THEN `{r.action}`")
        if r.rationale:
            lines.append(f"  - _Rationale: {r.rationale}_")
    lines.append("")

    # Event Catalog
    lines += ["## Event Catalog", "", "| Trigger | Action | Outcome |", "|---------|--------|---------|"]
    for ev in model.events:
        lines.append(f"| `{ev.trigger}` | {ev.action} | {ev.outcome} |")
    lines.append("")

    # Integration Map
    lines += ["## Integration Map", "", "| System | Direction | Protocol | Critical |",
              "|--------|-----------|----------|----------|"]
    for ig in model.integrations:
        crit = "🔴 TAK" if ig.critical else "🟢 nie"
        lines.append(f"| {ig.system} | {ig.direction} | {ig.protocol} | {crit} |")
    lines.append("")

    # Tech Constraints
    if model.tech_constraints:
        lines += ["## Tech Constraints", ""]
        for tc in model.tech_constraints:
            lines.append(f"- {tc}")
        lines.append("")

    # Scale
    if model.scale:
        s = model.scale
        lines += ["## Scale", ""]
        if s.concurrent_users:
            lines.append(f"- Concurrent users: **{s.concurrent_users}**")
        if s.response_time_ms:
            lines.append(f"- Response time: **{s.response_time_ms} ms**")
        if s.uptime_pct:
            lines.append(f"- Uptime: **{s.uptime_pct}%**")
        if s.data_volume_per_day:
            lines.append(f"- Data volume/day: **{s.data_volume_per_day}**")
        lines.append("")

    return "\n".join(lines)


def export_all(state: SessionState) -> dict[str, Path]:
    """Generuje 3 pliki, zwraca {kind: ścieżka}."""
    if not state.zachman_model:
        raise ValueError("Cannot export: ZachmanModel is None")
    model = ZachmanModel.model_validate(state.zachman_model)
    slug = state.slug()

    md_path = OUTPUT_DIR / f"{slug}-logos.md"
    json_path = OUTPUT_DIR / f"{slug}-contract.json"
    art_path = OUTPUT_DIR / f"{slug}-artifacts.md"

    md_path.write_text(_render_logos_md(state, model), encoding="utf-8")
    json_path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
    art_path.write_text(_render_artifacts_md(state, model), encoding="utf-8")

    return {"logos": md_path, "contract": json_path, "artifacts": art_path}
