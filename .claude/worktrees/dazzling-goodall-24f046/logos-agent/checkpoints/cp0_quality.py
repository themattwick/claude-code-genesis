"""Checkpoint 0 — bramka jakości opisu.

Jeśli ContextAgent ocenił quality_ok=False, prosi człowieka o doprecyzowanie.
"""
from __future__ import annotations
from utils.ui import console, header, prompt_text


def quality_gate(context: dict, original_description: str) -> str:
    """Zwraca uzupełniony opis (oryginał + odpowiedzi na clarifying_questions).

    Jeśli quality_ok=True — zwraca oryginał bez zmian.
    """
    if context.get("quality_ok", True):
        return original_description

    header("CHECKPOINT 0 — Doprecyzowanie opisu")
    console.print(f"  [yellow]ContextAgent: opis wymaga doprecyzowania[/yellow]")
    console.print(f"  [dim]{context.get('reason', '')}[/dim]")
    console.print()

    questions = context.get("clarifying_questions", [])
    if not questions:
        return original_description

    answers: list[str] = []
    for i, q in enumerate(questions, 1):
        console.print(f"[bold]({i}/{len(questions)})[/bold] {q}")
        ans = prompt_text("Twoja odpowiedź", default="")
        if ans:
            answers.append(f"{q}\n  → {ans}")
        console.print()

    if not answers:
        return original_description

    enriched = original_description + "\n\nDoprecyzowanie:\n" + "\n\n".join(answers)
    return enriched
