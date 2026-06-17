"""Backend — jeden runner dla wszystkich modeli (Google ADK + LiteLlm).

LiteLlm obsługuje setki modeli bez zmian w kodzie agentów:
    gemini-2.5-pro        → natywny Gemini (response_schema gwarantowane)
    ollama/mistral        → Ollama lokalnie
    gpt-4o                → OpenAI
    claude-3-5-sonnet-... → Anthropic
    groq/llama-3.1-70b   → Groq
    huggingface/...       → HuggingFace

Użycie:
    backend = get_backend()                   # Gemini (z config.MODELS)
    backend = get_backend("ollama/mistral")   # Ollama via LiteLlm
    backend = get_backend("gpt-4o")           # OpenAI via LiteLlm
"""
from __future__ import annotations
import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar
from pydantic import BaseModel
from config import LOGS_DIR, MODELS

T = TypeVar("T", bound=BaseModel)

# Per-run log directory
RUN_ID = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
RUN_LOG_DIR = LOGS_DIR / RUN_ID
RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)


def _log(agent_name: str, input_text: str, output_text: str) -> None:
    """Loguje input/output do logs/<run_id>/<agent>.jsonl."""
    log_file = RUN_LOG_DIR / f"{agent_name}.jsonl"
    entry = {
        "ts": datetime.now().isoformat(),
        "agent": agent_name,
        "input": input_text[:500],
        "output": output_text[:500],
    }
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class Backend(ABC):
    """Interfejs backendu — implementuje LogosBackend."""

    @abstractmethod
    async def run_text(self, agent_name: str, system_prompt: str, user_prompt: str) -> str:
        """Uruchamia prompt na LLM, zwraca tekst."""
        pass

    @abstractmethod
    async def run_json(
        self, agent_name: str, system_prompt: str, user_prompt: str, schema: type[T]
    ) -> T:
        """Uruchamia prompt na LLM, parsuje JSON, waliduje Pydantic schema."""
        pass


class LogosBackend(Backend):
    """Jeden backend: Gemini natywnie, reszta przez LiteLlm.

    Model resolution priority:
        model_override > config.MODELS[agent_name] > config.MODELS["default"]

    Gemini:  response_schema → gwarantowany poprawny JSON.
    LiteLlm: prompt engineering + regex fallback (best-effort JSON).
    """

    def __init__(self, model_override: str | None = None):
        try:
            from google.adk.agents import LlmAgent
            from google.adk.runners import InMemoryRunner
            from google.adk.models.lite_llm import LiteLlm
            from google.genai import types
            self._LlmAgent = LlmAgent
            self._InMemoryRunner = InMemoryRunner
            self._LiteLlm = LiteLlm
            self._types = types
        except ImportError:
            raise ImportError(
                "Logos Agent wymaga: pip install google-adk google-generativeai"
            )
        self.model_override = model_override

    def _resolve_model(self, agent_name: str):
        """Zwraca Gemini string lub LiteLlm(model=...) wrapper."""
        model_str = (
            self.model_override
            or MODELS.get(agent_name)
            or MODELS.get("default", "gemini-2.5-flash")
        )
        if model_str.startswith("gemini"):
            return model_str                          # Natywny Gemini
        return self._LiteLlm(model=model_str)         # Dowolny inny model

    async def _execute(self, agent, user_prompt: str) -> str:
        """Uruchamia agenta przez InMemoryRunner, zwraca tekst finalnej odpowiedzi."""
        runner = self._InMemoryRunner(agent=agent, app_name="logos")
        user_id = "logos-user"
        session = await runner.session_service.create_session(
            app_name="logos", user_id=user_id
        )
        content = self._types.Content(
            role="user", parts=[self._types.Part(text=user_prompt)]
        )
        final_text = ""
        async for event in runner.run_async(
            user_id=user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = event.content.parts[0].text or ""
        return final_text

    async def run_text(self, agent_name: str, system_prompt: str, user_prompt: str) -> str:
        model = self._resolve_model(agent_name)
        agent = self._LlmAgent(
            name=agent_name,
            instruction=system_prompt,
            model=model,
            generate_content_config=self._types.GenerateContentConfig(temperature=0.3),
        )
        final_text = await self._execute(agent, user_prompt)
        _log(agent_name, user_prompt, final_text)
        return final_text

    async def run_json(
        self, agent_name: str, system_prompt: str, user_prompt: str, schema: type[T]
    ) -> T:
        model = self._resolve_model(agent_name)
        is_native_gemini = isinstance(model, str) and model.startswith("gemini")

        if is_native_gemini:
            # Natywny Gemini: response_schema gwarantuje poprawny JSON
            agent = self._LlmAgent(
                name=agent_name,
                instruction=system_prompt,
                model=model,
                generate_content_config=self._types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2,
                ),
            )
            final_text = await self._execute(agent, user_prompt)
            data = json.loads(final_text)
        else:
            # Non-Gemini: litellm bezpośrednio z JSON mode (Ollama format:json)
            import litellm
            model_str = self.model_override or MODELS.get(agent_name) or MODELS["default"]
            response = await litellm.acompletion(
                model=model_str,
                messages=[
                    {"role": "system", "content": system_prompt
                     + "\n\nCRITICAL: Output pure JSON only. No markdown, no explanation. Start with {."},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            final_text = response.choices[0].message.content or ""
            try:
                data = json.loads(final_text)
            except json.JSONDecodeError:
                match = re.search(r"```json\s*(\{.*?\})\s*```", final_text, re.DOTALL)
                if not match:
                    match = re.search(r"\{.*\}", final_text, re.DOTALL)
                if not match:
                    raise ValueError(f"Brak JSON w odpowiedzi modelu: {final_text[:200]}")
                data = json.loads(match.group(1) if match.lastindex else match.group())

        try:
            obj = schema.model_validate(data)
        except Exception:
            # Niektóre modele owija JSON w {"NazwaSchemy": {...}} — unwrap
            if len(data) == 1:
                obj = schema.model_validate(next(iter(data.values())))
            else:
                raise
        _log(agent_name, user_prompt, json.dumps(data))
        return obj


def get_backend(model: str | None = None) -> Backend:
    """Fabryka — zawsze LogosBackend, opcjonalnie z model override.

    Args:
        model: String modelu lub None (używa config.MODELS).
               Przykłady: "ollama/mistral", "gpt-4o", "claude-3-5-sonnet-20241022"
    """
    return LogosBackend(model_override=model)
