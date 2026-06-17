"""Runner backend-agnostyczny — obsługuje Google i Ollama.

Punkt wejścia dla agentów:
    await run_agent(agent_name, system_prompt, user_prompt) -> str
    await run_agent_json(agent_name, system_prompt, user_prompt, schema) -> T

Backend jest wybierany globalnie w main.py przez set_backend().
"""
from __future__ import annotations
from typing import TypeVar
from pydantic import BaseModel

from agents.backends import Backend

T = TypeVar("T", bound=BaseModel)

# Globalny backend — ustawiony w main.py
_backend: Backend | None = None


def set_backend(backend: Backend) -> None:
    """Ustawia globalny backend (Google lub Local)."""
    global _backend
    _backend = backend


async def run_agent(agent_name: str, system_prompt: str, user_prompt: str) -> str:
    """Uruchamia agent na wybranym backendie, zwraca text."""
    if _backend is None:
        raise RuntimeError("Backend not set. Call set_backend() first.")
    return await _backend.run_text(agent_name, system_prompt, user_prompt)


async def run_agent_json(
    agent_name: str, system_prompt: str, user_prompt: str, schema: type[T]
) -> T:
    """Uruchamia agent na wybranym backendie, zwraca Pydantic object."""
    if _backend is None:
        raise RuntimeError("Backend not set. Call set_backend() first.")
    return await _backend.run_json(agent_name, system_prompt, user_prompt, schema)
