"""Checkpoint 2 — człowiek odpowiada na luki zidentyfikowane przez InterviewAgent."""
from __future__ import annotations
from rich.prompt import Prompt
from utils.ui import console, header
from schemas.session import GapQuestion


def answer_gaps(gap_questions: list[GapQuestion]) -> dict[int, str]:
    """Zwraca {gap_index: answer}. gap_index to indeks w liście, nie qid."""
    if not gap_questions:
        console.print("[green]Brak luk do uzupełnienia.[/green]")
        return {}

    header("CHECKPOINT 2 — Pytania uzupełniające",
           subtitle=f"({len(gap_questions)} pytań od InterviewAgent)")

    answers: dict[int, str] = {}
    for i, gap in enumerate(gap_questions):
        targets = ", ".join(f"P{t}" for t in gap.target_question_ids) if gap.target_question_ids else "—"
        console.print()
        console.print(f"[bold]({i + 1}/{len(gap_questions)})[/bold]  [dim]→ {targets}[/dim]")
        console.print(f"  {gap.question}")
        ans = Prompt.ask("  Twoja odpowiedź (Enter = pomiń)", default="")
        if ans:
            answers[i] = ans

    return answers
