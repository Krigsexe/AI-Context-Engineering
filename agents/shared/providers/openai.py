# =============================================================================
# ODIN v7.0 - OpenAI Provider
# =============================================================================
# GPT models: https://openai.com
# Also works with OpenAI-compatible endpoints
# =============================================================================

import os
import time
from typing import List, Optional
import requests

from .base import BaseLLMProvider, Message, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider for GPT models.

    Models: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo, o1
    Also compatible with any OpenAI-compatible API endpoint.
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        organization: str = None,
        timeout: int = 120
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.organization = organization or os.getenv("OPENAI_ORG_ID")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "openai"

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI API."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.organization:
            headers["OpenAI-Organization"] = self.organization

        openai_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if stop:
            payload["stop"] = stop

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        latency_ms = (time.time() - start_time) * 1000

        choice = data["choices"][0]

        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", self.model),
            provider=self.name,
            usage={
                "prompt_tokens": data["usage"]["prompt_tokens"],
                "completion_tokens": data["usage"]["completion_tokens"],
                "total_tokens": data["usage"]["total_tokens"],
            },
            latency_ms=latency_ms,
            raw_response=data,
            finish_reason=choice.get("finish_reason", "stop"),
        )

    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        """List common OpenAI models."""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini",
        ]
