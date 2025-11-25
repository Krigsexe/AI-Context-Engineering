# =============================================================================
# ODIN v7.0 - Groq Provider
# =============================================================================
# Fast inference: https://groq.com
# =============================================================================

import os
import time
from typing import List, Optional
import requests

from .base import BaseLLMProvider, Message, LLMResponse


class GroqProvider(BaseLLMProvider):
    """
    Groq provider for fast LLM inference.

    Models: Llama 3.1, Mixtral, Gemma
    Free tier with rate limits.
    """

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "groq"

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Groq API."""
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set")

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        groq_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": groq_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if stop:
            payload["stop"] = stop

        response = requests.post(
            self.API_URL,
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
        """List available Groq models."""
        return [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.2-90b-text-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ]
