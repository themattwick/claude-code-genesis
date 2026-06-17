"""Model-agnostic LLM backend using Google ADK + LiteLlm"""

import json
import logging
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel

try:
    from litellm import completion, completion_with_retries
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

import config

logger = logging.getLogger(__name__)


class LLMBackend:
    """Model-agnostic LLM backend supporting multiple providers"""

    def __init__(
        self,
        provider: str = None,
        model: str = None,
        api_key: str = None,
    ):
        """Initialize LLM backend

        Args:
            provider: LLM provider (gemini, claude, openai, ollama, etc)
            model: Model name/ID
            api_key: API key for the provider
        """
        self.provider = provider or config.LLM_PROVIDER
        self.model = model or config.LLM_MODEL
        self.api_key = api_key or config.LLM_API_KEY

        # Format model string based on provider
        if self.provider == "gemini":
            self.model_id = self.model
        elif self.provider == "claude":
            self.model_id = f"claude-{self.model}"
        elif self.provider == "openai":
            self.model_id = self.model
        elif self.provider == "ollama":
            self.model_id = f"ollama/{self.model}"
        else:
            self.model_id = self.model

        logger.info(f"Initialized LLM Backend: {self.provider} / {self.model_id}")

    def call(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = config.MAX_TOKENS,
    ) -> str:
        """Call LLM with prompt

        Args:
            prompt: User prompt
            system_prompt: System message
            temperature: Temperature for generation
            max_tokens: Max tokens to generate

        Returns:
            LLM response text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            if LITELLM_AVAILABLE:
                response = completion_with_retries(
                    model=self.model_id,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=self.api_key if self.api_key else None,
                    timeout=config.TIMEOUT_SECONDS,
                    max_retries=config.MAX_RETRIES,
                )
                return response.choices[0].message.content
            else:
                # Fallback if litellm not available
                logger.error("litellm not available. Please install: pip install litellm")
                raise ImportError("litellm is required for LLM calls")

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def call_json(
        self,
        prompt: str,
        system_prompt: str = None,
        response_schema: Type[BaseModel] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Call LLM expecting JSON response

        Args:
            prompt: User prompt
            system_prompt: System message
            response_schema: Pydantic model for expected structure
            temperature: Temperature

        Returns:
            Parsed JSON response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if response_schema:
            schema_str = response_schema.model_json_schema()
            prompt = f"{prompt}\n\nRespond with JSON matching this schema:\n{json.dumps(schema_str, indent=2)}"

        messages.append({"role": "user", "content": prompt})

        try:
            if LITELLM_AVAILABLE:
                response = completion_with_retries(
                    model=self.model_id,
                    messages=messages,
                    temperature=temperature,
                    api_key=self.api_key if self.api_key else None,
                    timeout=config.TIMEOUT_SECONDS,
                    max_retries=config.MAX_RETRIES,
                )
                content = response.choices[0].message.content

                # Try to parse JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Try extracting JSON from response
                    import re
                    json_match = re.search(r"\{.*\}", content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    raise ValueError(f"Could not parse JSON from response: {content}")

            else:
                raise ImportError("litellm is required for LLM calls")

        except Exception as e:
            logger.error(f"LLM JSON call failed: {e}")
            raise

    def get_info(self) -> Dict[str, Any]:
        """Get backend info"""
        return {
            "provider": self.provider,
            "model": self.model,
            "model_id": self.model_id,
        }


# Global backend instance
_backend: Optional[LLMBackend] = None


def init_backend(
    provider: str = None,
    model: str = None,
    api_key: str = None,
) -> LLMBackend:
    """Initialize global LLM backend"""
    global _backend
    _backend = LLMBackend(provider=provider, model=model, api_key=api_key)
    return _backend


def get_backend() -> LLMBackend:
    """Get global LLM backend, initialize if needed"""
    global _backend
    if _backend is None:
        _backend = LLMBackend()
    return _backend


def llm_call(prompt: str, system_prompt: str = None, **kwargs) -> str:
    """Convenience function to call LLM"""
    backend = get_backend()
    return backend.call(prompt=prompt, system_prompt=system_prompt, **kwargs)


def llm_call_json(
    prompt: str,
    system_prompt: str = None,
    response_schema: Type[BaseModel] = None,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to call LLM with JSON response"""
    backend = get_backend()
    return backend.call_json(
        prompt=prompt,
        system_prompt=system_prompt,
        response_schema=response_schema,
        **kwargs
    )
