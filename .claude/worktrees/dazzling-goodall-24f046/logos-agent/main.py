"""Logos Agent — punkt wejścia CLI.

Użycie:
    python main.py --mode full
    python main.py --mode fast --name "MyApp"
    python main.py --example ecommerce
    python main.py --model ollama/mistral --example ecommerce
    python main.py --model gpt-4o --mode fast
    python main.py --resume "MyApp"
    python main.py --validate output/myapp-contract.json
    python main.py --list
"""
from __future__ import annotations
import argparse
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from schemas.session import SessionState
from utils.persist import load_session, save_session, list_sessions
from utils.ui import console, header, banner_panel, prompt_text, prompt_choice
from config import EXAMPLES_DIR, MIN_DESCRIPTION_TOKENS


def parse_args():
    p = argparse.ArgumentParser(description="Logos Agent — Spec-Driven Development pipeline")
    p.add_argument("--mode", choices=["fast", "full"], default="full",
                   help="fast=40 pytań/4 kategorie, full=100 pytań/10 kategorii")
    p.add_argument("--name", help="Nazwa systemu (pomija prompt)")
    p.add_argument("--example", help="Wczytaj opis z examples/<name>.txt")
    p.add_argument("--resume", help="Wznów sesję po nazwie/slug")
    p.add_argument("--validate", help="Waliduj istniejący contract.json (Pydantic)")
    p.add_argument("--list", action="store_true", help="Lista zapisanych sesji")
    p.add_argument(
        "--model", default=None,
        help=(
            "Model do użycia. Domyślnie: z config.MODELS (Gemini). "
            "Przykłady: gemini-2.5-pro, ollama/mistral, gpt-4o, "
            "claude-3-5-sonnet-20241022, groq/llama-3.1-70b-versatile"
        ),
    )
    return p.parse_args()


def read_example(name: str) -> tuple[str, str]:
    """Zwraca (system_name, description) z examples/<name>.txt."""
    path = EXAMPLES_DIR / f"{name}.txt"
    if not path.exists():
        console.print(f"[red]Brak przykładu: {path}[/red]")
        sys.exit(1)
    content = path.read_text(encoding="utf-8").strip()
    # Pierwsza linia = nazwa, reszta = opis
    lines = content.split("\n", 1)
    if len(lines) < 2:
        return name, content
    return lines[0].strip(), lines[1].strip()


def validate_contract(path: str) -> int:
    from schemas.zachman import ZachmanModel
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        model = ZachmanModel.model_validate(data)
        console.print(f"[green]✓ Walidacja OK[/green]: {path}")
        console.print(f"  System: {model.system}")
        console.print(f"  Ambiguity: {model.ambiguity_score:.2f}")
        console.print(f"  Encje: {len(model.entities)}, Aktorzy: {len(model.actors)}, "
                      f"Reguły: {len(model.rules)}, Zdarzenia: {len(model.events)}, "
                      f"Integracje: {len(model.integrations)}")
        return 0
    except Exception as e:
        console.print(f"[red]✗ Walidacja FAILED:[/red] {e}")
        return 1


def list_sessions_cmd():
    sessions = list_sessions()
    if not sessions:
        console.print("[dim]Brak zapisanych sesji.[/dim]")
        return
    console.print("[bold]Zapisane sesje:[/bold]")
    for slug, name in sessions:
        console.print(f"  · [cyan]{slug}[/cyan]  → {name}")


def collect_input(args) -> SessionState:
    """Zbiera nazwę i opis od użytkownika lub z --example/--name."""
    if args.example:
        name, description = read_example(args.example)
        console.print(f"[dim]Wczytano przykład: {args.example}[/dim]")
        console.print(f"  Nazwa: [bold]{name}[/bold]")
        console.print(f"  Opis: {description[:120]}...")
    else:
        name = args.name or prompt_text("Nazwa systemu")
        console.print()
        console.print("[bold]Krótki opis systemu (2-5 zdań).[/bold]")
        console.print("[dim]Im konkretniej tym lepiej. Domena, główne encje, kluczowe reguły.[/dim]")
        description = prompt_text("Opis")

        word_count = len(description.split())
        if word_count < MIN_DESCRIPTION_TOKENS:
            console.print(f"[yellow]⚠ Opis ma tylko {word_count} słów (zalecane >{MIN_DESCRIPTION_TOKENS}).[/yellow]")
            console.print("[yellow]ContextAgent może poprosić o doprecyzowanie w CP0.[/yellow]")

    return SessionState(
        system_name=name,
        description=description,
        mode=args.mode,
        phase="context",
    )


def main():
    load_dotenv()
    args = parse_args()

    # Specjalne tryby
    if args.list:
        list_sessions_cmd()
        return
    if args.validate:
        sys.exit(validate_contract(args.validate))

    # Inicjalizacja backendu
    from agents.backends import get_backend
    from agents._runner import set_backend

    try:
        backend = get_backend(model=args.model)
        model_info = args.model or "Gemini (z config.MODELS)"
        banner_panel(
            "  L O G O S   A G E N T  \n"
            "Spec-Driven Development pipeline\n"
            f"[cyan]Model: {model_info}[/cyan]",
            style="cyan",
        )
    except Exception as e:
        console.print(f"[red]✗ Backend initialization failed:[/red] {e}")
        sys.exit(1)

    set_backend(backend)

    # Resume vs nowa sesja
    if args.resume:
        state = load_session(args.resume)
        if state is None:
            console.print(f"[red]Nie znaleziono sesji: {args.resume}[/red]")
            console.print("[dim]Użyj --list aby zobaczyć dostępne sesje.[/dim]")
            sys.exit(1)
        console.print(f"[green]✓ Wznawiam sesję:[/green] [bold]{state.system_name}[/bold]  "
                      f"[dim](faza: {state.phase}, tryb: {state.mode})[/dim]")
    else:
        state = collect_input(args)
        save_session(state)
        console.print(f"[dim]Sesja zapisana w output/.session/{state.slug()}.json[/dim]")

    from pipeline import run_pipeline
    asyncio.run(run_pipeline(state))


if __name__ == "__main__":
    main()
