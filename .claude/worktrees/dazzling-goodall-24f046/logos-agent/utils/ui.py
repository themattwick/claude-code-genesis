"""CLI helpery — kolory, prompts, formatowanie. Używa rich."""
from __future__ import annotations
from typing import Iterable
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.panel import Panel

console = Console()


def header(title: str, subtitle: str = "") -> None:
    bar = "═" * 60
    console.print()
    console.print(f"[bold cyan]{bar}[/bold cyan]")
    console.print(f"  [bold cyan]{title}[/bold cyan]" + (f"  [dim]{subtitle}[/dim]" if subtitle else ""))
    console.print(f"[bold cyan]{bar}[/bold cyan]")


def kv(label: str, value: str, color: str = "white") -> None:
    console.print(f"  [bold]{label}:[/bold] [{color}]{value}[/{color}]")


def ambiguity_bar(score: float, width: int = 12) -> str:
    """Renderuje pasek 0.0–1.0 → ████████░░░░"""
    filled = int(round(score * width))
    return "█" * filled + "░" * (width - filled)


def color_for_severity(sev: str) -> str:
    return {"high": "red", "medium": "yellow", "low": "blue"}.get(sev, "white")


def prompt_text(label: str, default: str = "") -> str:
    return Prompt.ask(f"[bold]{label}[/bold]", default=default)


def prompt_choice(label: str, choices: Iterable[str], default: str | None = None) -> str:
    return Prompt.ask(f"[bold]{label}[/bold]", choices=list(choices), default=default)


def print_question(qid: int, category: str, text: str) -> None:
    console.print(f"[dim][{category}][/dim] [bold]P{qid}:[/bold] {text}")


def print_finding(severity: str, where: str, issue: str, fix: str = "") -> None:
    color = color_for_severity(severity)
    sym = {"high": "✗", "medium": "⚠", "low": "ℹ"}.get(severity, "•")
    console.print(f"  [{color}]{sym} {severity.upper():6}[/{color}] [dim]{where}[/dim]  {issue}")
    if fix:
        console.print(f"           [dim italic]→ {fix}[/dim italic]")


def banner_panel(text: str, style: str = "cyan") -> None:
    console.print(Panel(Text(text, justify="center"), border_style=style))
