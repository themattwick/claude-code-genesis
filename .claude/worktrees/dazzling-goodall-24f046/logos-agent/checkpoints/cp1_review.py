"""Checkpoint 1 — batch review draftów per kategoria.

Przepływ:
- Iteracja po kategoriach (tylko tych obecnych w drafts)
- Dla każdej kategorii pokazuje wszystkie pytania + drafty
- Komendy: a (akceptuj kategorię), e <nr> (edytuj), s <nr> (pomiń), n (następna), q (zapisz i wyjdź)
"""
from __future__ import annotations
from rich.prompt import Prompt
from utils.ui import console, header, kv
from framework import CATEGORIES, ALL_QUESTIONS, question_by_id, detect_risky_words


def _print_category_overview(cat_id: str, drafts: dict[int, str], reviewed: dict[int, str]):
    cat = next(c for c in CATEGORIES if c.id == cat_id)
    cat_qs = [q for q in ALL_QUESTIONS if q.category_id == cat_id and q.id in drafts]

    color = cat.color_hex
    console.print()
    console.print(f"[bold]── {cat.name} — {cat.sub} ──[/bold]")
    console.print()

    for q in cat_qs:
        ans = reviewed.get(q.id, drafts.get(q.id, ""))
        is_reviewed = q.id in reviewed
        marker = "[green]✓[/green]" if is_reviewed else "[dim]·[/dim]"

        console.print(f"  {marker} [bold]P{q.id}:[/bold] {q.text}")
        if ans.startswith("WYMAGA"):
            console.print(f"     [yellow italic]{ans}[/yellow italic]")
        else:
            risks = detect_risky_words(ans)
            risk_label = ""
            if risks:
                words = ", ".join(r.word for r in risks)
                risk_label = f"  [yellow]⚠ {words}[/yellow]"
            console.print(f"     [dim]→[/dim] {ans}{risk_label}")
        console.print()


def review_drafts(drafts: dict[int, str]) -> dict[int, str]:
    """Główna pętla CP1. Zwraca {qid: zatwierdzona_odpowiedź}."""
    reviewed: dict[int, str] = {}
    drafted_cats = [c for c in CATEGORIES if any(
        q.category_id == c.id and q.id in drafts for q in ALL_QUESTIONS
    )]

    header("CHECKPOINT 1 — Przegląd draftów",
           subtitle=f"({len(drafts)} pytań w {len(drafted_cats)} kategoriach)")

    cat_idx = 0
    while cat_idx < len(drafted_cats):
        cat = drafted_cats[cat_idx]
        cat_qs = [q for q in ALL_QUESTIONS if q.category_id == cat.id and q.id in drafts]

        _print_category_overview(cat.id, drafts, reviewed)

        cmd = Prompt.ask(
            f"[bold cyan]{cat.name}[/bold cyan]: "
            "[a]kceptuj wszystkie · [e <nr>] edytuj · [s <nr>] pomiń · [n]astępna · [q] zapisz i wyjdź",
            default="a",
        ).strip().lower()

        if cmd == "a":
            for q in cat_qs:
                reviewed.setdefault(q.id, drafts[q.id])
            cat_idx += 1
        elif cmd == "n":
            for q in cat_qs:
                reviewed.setdefault(q.id, drafts[q.id])
            cat_idx += 1
        elif cmd == "q":
            for q in cat_qs:
                reviewed.setdefault(q.id, drafts[q.id])
            console.print("[dim]Zapisano stan, wyjście...[/dim]")
            return reviewed
        elif cmd.startswith("e "):
            try:
                qid = int(cmd[2:].strip())
                if qid in drafts and any(q.id == qid for q in cat_qs):
                    q = question_by_id(qid)
                    console.print(f"\n[bold]P{qid}:[/bold] {q.text}")
                    console.print(f"[dim]Aktualnie:[/dim] {drafts[qid]}")
                    new_ans = Prompt.ask("Nowa odpowiedź (Enter = bez zmian)", default=drafts[qid])
                    reviewed[qid] = new_ans
                else:
                    console.print(f"[red]Pytanie P{qid} nie należy do kategorii {cat.name}[/red]")
            except ValueError:
                console.print("[red]Nieprawidłowy numer pytania[/red]")
        elif cmd.startswith("s "):
            try:
                qid = int(cmd[2:].strip())
                if qid in drafts and any(q.id == qid for q in cat_qs):
                    reviewed[qid] = ""  # pominięte
                    console.print(f"[dim]P{qid} pominięte[/dim]")
                else:
                    console.print(f"[red]Pytanie P{qid} nie należy do kategorii {cat.name}[/red]")
            except ValueError:
                console.print("[red]Nieprawidłowy numer pytania[/red]")
        else:
            console.print("[red]Nieznana komenda. Użyj: a / e <nr> / s <nr> / n / q[/red]")

    # Domknij pominięte (jeśli któreś pytania nie miały decyzji)
    for qid, draft in drafts.items():
        reviewed.setdefault(qid, draft)

    return reviewed
