"""Orkiestracja pipeline z save/resume po każdej fazie."""
from __future__ import annotations
import asyncio
from rich.progress import Progress, SpinnerColumn, TextColumn

from schemas.session import SessionState
from utils.persist import save_session
from utils.ui import console, header
from config import MAX_AMBIGUITY_ITERATIONS

from agents.context_agent import extract_context
from agents.category_agent import generate_all_drafts
from agents.interview_agent import find_gaps, find_focused_gaps
from agents.synthesis_agent import synthesize
from agents.critique_agent import critique
from agents.risk_agent import scan_risks, compute_ambiguity_score
from agents.consistency_agent import check_consistency
from agents.export_agent import export_all

from checkpoints.cp0_quality import quality_gate
from checkpoints.cp1_review import review_drafts
from checkpoints.cp2_interview import answer_gaps
from checkpoints.cp3_validation import validate_final


def _spinner(label: str):
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ), label


async def run_pipeline(state: SessionState) -> None:
    """Główna pętla — uruchamia od state.phase do końca, zapisuje po każdej fazie."""

    # ── Phase: context ──────────────────────────────────────────────────
    if state.phase == "context":
        header("Faza 1 — Ekstrakcja kontekstu Zachman")
        with console.status("[cyan]ContextAgent analizuje opis...[/cyan]"):
            ctx = await extract_context(state.description)
        state.zachman_context = ctx

        if not ctx.get("quality_ok", True):
            enriched = quality_gate(ctx, state.description)
            if enriched != state.description:
                state.description = enriched
                # Re-run context z wzbogaconym opisem
                with console.status("[cyan]ContextAgent ponownie analizuje...[/cyan]"):
                    state.zachman_context = await extract_context(state.description)

        state.phase = "drafts"
        save_session(state)

    # ── Phase: drafts ───────────────────────────────────────────────────
    if state.phase == "drafts":
        header(f"Faza 2 — Drafty ({state.mode})",
               subtitle=f"{'40 pytań w 4 kategoriach' if state.mode == 'fast' else '100 pytań w 10 kategoriach'}")
        with console.status("[cyan]CategoryAgents pracują równolegle...[/cyan]"):
            drafts = await generate_all_drafts(
                state.description,
                state.zachman_context or {},
                state.mode,
            )
        state.drafts = drafts
        console.print(f"  [green]✓[/green] Wygenerowano {len(drafts)} draftów")
        state.phase = "cp1"
        save_session(state)

    # ── Phase: cp1 ──────────────────────────────────────────────────────
    if state.phase == "cp1":
        state.reviewed = review_drafts(state.drafts)
        state.phase = "interview"
        save_session(state)

    # ── Phase: interview ────────────────────────────────────────────────
    if state.phase == "interview":
        header("Faza 3 — Identyfikacja luk")
        with console.status("[cyan]InterviewAgent szuka luk...[/cyan]"):
            gaps = await find_gaps(state.reviewed)
        state.gap_questions = gaps
        console.print(f"  [green]✓[/green] Wykryto {len(gaps)} luk")
        state.phase = "cp2"
        save_session(state)

    # ── Phase: cp2 ──────────────────────────────────────────────────────
    if state.phase == "cp2":
        state.gap_answers = answer_gaps(state.gap_questions)
        # Merge: reviewed → final, doklejając gap_answers przez target_question_ids
        merged = dict(state.reviewed)
        for gap_idx, ans in state.gap_answers.items():
            if gap_idx >= len(state.gap_questions):
                continue
            gap = state.gap_questions[gap_idx]
            for tqid in gap.target_question_ids:
                existing = merged.get(tqid, "")
                # Doklej do istniejącej odpowiedzi (lub zastąp jeśli była WYMAGA)
                if not existing or existing.startswith("WYMAGA"):
                    merged[tqid] = ans
                else:
                    merged[tqid] = f"{existing}\n{ans}"
        state.final_answers = merged
        state.phase = "synthesis"
        save_session(state)

    # ── Phase: synthesis ────────────────────────────────────────────────
    if state.phase == "synthesis":
        header("Faza 4 — Synteza ZachmanModel")
        with console.status("[cyan]SynthesisAgent buduje strukturalny model...[/cyan]"):
            try:
                zm = await synthesize(state.system_name, state.final_answers)
                state.zachman_model = zm.model_dump()
                console.print(f"  [green]✓[/green] Model: "
                              f"{len(zm.entities)} encji · {len(zm.actors)} aktorów · "
                              f"{len(zm.rules)} reguł · {len(zm.events)} zdarzeń · "
                              f"{len(zm.integrations)} integracji")
            except Exception as e:
                console.print(f"  [yellow]⚠ SynthesisAgent failed (fallback):[/yellow] {e}")
        state.phase = "critique"
        save_session(state)

    # ── Phase: critique ─────────────────────────────────────────────────
    if state.phase == "critique":
        header("Faza 5 — Krytyka + Ryzyka + Spójność")
        from schemas.zachman import ZachmanModel
        zm = ZachmanModel.model_validate(state.zachman_model)

        # CritiqueAgent (LLM) + RiskAgent (det.) + ConsistencyAgent (det.) równolegle
        with console.status("[cyan]Analizuję model...[/cyan]"):
            critique_task = asyncio.create_task(critique(zm))
            risks = scan_risks(state.final_answers)
            conflicts = check_consistency(state.final_answers)
            critique_findings = await critique_task

        state.critique = [f.model_dump() for f in critique_findings]
        state.risks = risks
        state.conflicts = conflicts

        # Aktualizuj ambiguity_score na podstawie risk scan
        ambig = compute_ambiguity_score(state.final_answers)
        if state.zachman_model:
            state.zachman_model["ambiguity_score"] = ambig

        console.print(f"  [green]✓[/green] {len(critique_findings)} findings · "
                      f"{len(risks)} ryzyk · {len(conflicts)} konfliktów")
        state.phase = "cp3"
        save_session(state)

    # ── Phase: cp3 ──────────────────────────────────────────────────────
    if state.phase == "cp3":
        action = validate_final(state)
        if action == "re_interview" and state.iteration < MAX_AMBIGUITY_ITERATIONS:
            state.iteration += 1
            console.print(f"\n[cyan]Pętla redukcji niejednoznaczności (iteracja {state.iteration})...[/cyan]")
            with console.status("[cyan]Generuję pytania ukierunkowane na findings...[/cyan]"):
                gaps = await find_focused_gaps(state.critique, [r.model_dump() for r in state.risks], state.final_answers)
            state.gap_questions = gaps
            state.phase = "cp2"  # pętla
            save_session(state)
            return await run_pipeline(state)

        state.phase = "export"
        save_session(state)

    # ── Phase: export ───────────────────────────────────────────────────
    if state.phase == "export":
        header("Faza 6 — Eksport")
        paths = export_all(state)
        for kind, path in paths.items():
            console.print(f"  [green]✓[/green] {kind:10}  [dim]{path}[/dim]")
        state.phase = "done"
        save_session(state)

    # ── Phase: done ─────────────────────────────────────────────────────
    if state.phase == "done":
        console.print()
        console.print("[bold green]═══ Specyfikacja gotowa ═══[/bold green]")
        console.print(f"  System: [bold]{state.system_name}[/bold]")
        console.print(f"  Ambiguity Score: [bold]{(state.zachman_model or {}).get('ambiguity_score', 0):.2f}[/bold]")
        console.print()
