"""Checkpoint 3 — finalna walidacja. Pokazuje Ambiguity Score, ryzyka, krytykę.

Zwraca jedną z 3 akcji: APPROVE, RE_INTERVIEW, EDIT.
"""
from __future__ import annotations
from typing import Literal
from rich.prompt import Prompt
from utils.ui import console, header, ambiguity_bar, color_for_severity
from schemas.session import SessionState
from config import TARGET_AMBIGUITY_SCORE, MAX_AMBIGUITY_ITERATIONS


ValidationAction = Literal["approve", "re_interview", "edit"]


def _print_summary(state: SessionState):
    score = 0.0
    if state.zachman_model:
        score = state.zachman_model.get("ambiguity_score", 0.0)

    bar = ambiguity_bar(score)
    quality = "[green]dobry[/green]" if score < TARGET_AMBIGUITY_SCORE else \
              "[yellow]umiarkowany[/yellow]" if score < 0.5 else \
              "[red]wysoki[/red]"
    console.print(f"  [bold]Ambiguity Score:[/bold]  {score:.2f}  {bar}  ({quality})")
    console.print()

    # Critique
    if state.critique:
        console.print(f"  [bold]── Krytyka modelu ({len(state.critique)} findings) ──[/bold]")
        sev_count = {"high": 0, "medium": 0, "low": 0}
        for f in state.critique:
            sev_count[f.get("severity", "low")] = sev_count.get(f.get("severity", "low"), 0) + 1
        if sev_count["high"]:
            console.print(f"   [red]✗ HIGH:    {sev_count['high']}[/red]")
        if sev_count["medium"]:
            console.print(f"   [yellow]⚠ MEDIUM:  {sev_count['medium']}[/yellow]")
        if sev_count["low"]:
            console.print(f"   [blue]ℹ LOW:     {sev_count['low']}[/blue]")
        console.print()
        # Top 5 findings
        for f in state.critique[:5]:
            sev = f.get("severity", "low")
            color = color_for_severity(sev)
            sym = {"high": "✗", "medium": "⚠", "low": "ℹ"}.get(sev, "•")
            console.print(f"   [{color}]{sym} {sev.upper():6}[/{color}] "
                          f"[dim]{f.get('where', '')}[/dim]  {f.get('issue', '')}")
        if len(state.critique) > 5:
            console.print(f"   [dim]... ({len(state.critique) - 5} więcej, patrz [v])[/dim]")
        console.print()

    # Ryzyka
    if state.risks:
        words = {}
        for r in state.risks:
            words.setdefault(r.word, []).append(r.question_id)
        console.print(f"  [bold]── Ryzyka ({len(state.risks)} trafień, {len(words)} unikalnych słów) ──[/bold]")
        for word, qids in sorted(words.items(), key=lambda x: -len(x[1]))[:8]:
            qs = ", ".join(f"P{q}" for q in qids[:5])
            extra = "" if len(qids) <= 5 else f" +{len(qids) - 5}"
            console.print(f"   [yellow]·[/yellow] [bold]{word}[/bold]  [dim]{qs}{extra}[/dim]")
        console.print()

    # Konflikty
    if state.conflicts:
        console.print(f"  [bold]── Konflikty spójności ({len(state.conflicts)}) ──[/bold]")
        for c in state.conflicts[:5]:
            extra = ""
            if c.overlap:
                extra = f"  [dim]nakładające się: {', '.join(c.overlap[:3])}[/dim]"
            console.print(f"   [magenta]·[/magenta] {c.pair_title}  "
                          f"[dim](P{c.a_id} ↔ P{c.b_id})[/dim]{extra}")
        console.print()

    # Zachman summary
    if state.zachman_model:
        m = state.zachman_model
        console.print(f"  [bold]── ZachmanModel ──[/bold]")
        console.print(
            f"   {len(m.get('entities', []))} encji  · "
            f"{len(m.get('actors', []))} aktorów  · "
            f"{len(m.get('rules', []))} reguł  · "
            f"{len(m.get('events', []))} zdarzeń  · "
            f"{len(m.get('integrations', []))} integracji"
        )
        console.print()


def _print_full_report(state: SessionState):
    console.print()
    console.print("[bold]═══ Pełny raport krytyki ═══[/bold]")
    for f in state.critique:
        sev = f.get("severity", "low")
        color = color_for_severity(sev)
        sym = {"high": "✗", "medium": "⚠", "low": "ℹ"}.get(sev, "•")
        console.print(f"\n[{color}]{sym} {sev.upper()}[/{color}]  [dim]{f.get('where', '')}[/dim]")
        console.print(f"  Issue: {f.get('issue', '')}")
        if f.get("fix"):
            console.print(f"  Fix:   [italic]{f['fix']}[/italic]")
    console.print()


def validate_final(state: SessionState) -> ValidationAction:
    iter_label = f"iteracja {state.iteration + 1}/{MAX_AMBIGUITY_ITERATIONS + 1}"
    header("CHECKPOINT 3 — Walidacja finalna", subtitle=iter_label)

    while True:
        _print_summary(state)

        can_re_interview = state.iteration < MAX_AMBIGUITY_ITERATIONS
        re_label = f"[r] re-interview ({MAX_AMBIGUITY_ITERATIONS - state.iteration} pozostało)" \
                   if can_re_interview else "[r] re-interview (limit wyczerpany)"

        cmd = Prompt.ask(
            f"\n[bold]Akcja:[/bold] [a]kceptuj i eksportuj · {re_label} · [v] pełny raport",
            choices=(["a", "r", "v"] if can_re_interview else ["a", "v"]),
            default="a",
        ).strip().lower()

        if cmd == "a":
            return "approve"
        if cmd == "r" and can_re_interview:
            return "re_interview"
        if cmd == "v":
            _print_full_report(state)
            continue
