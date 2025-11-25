# =============================================================================
# ODIN v7.0 - Anthropic Provider
# =============================================================================
# Claude models: https://anthropic.com
# =============================================================================

import os
import time
from typing import List, Optional
import requests

from .base import BaseLLMProvider, Message, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic provider for Claude models.

    Models: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
    """

    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "anthropic"

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic API."""
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        start_time = time.time()

        # Extract system message if present
        system_content = ""
        anthropic_messages = []
        for m in messages:
            if m.role == "system":
                system_content = m.content
            else:
                anthropic_messages.append({
                    "role": m.role,
                    "content": m.content
                })

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json",
        }

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_content:
            payload["system"] = system_content

        if stop:
            payload["stop_sequences"] = stop

        response = requests.post(
            self.API_URL,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        latency_ms = (time.time() - start_time) * 1000

        return LLMResponse(
            content=data["content"][0]["text"],
            model=data.get("model", self.model),
            provider=self.name,
            usage={
                "prompt_tokens": data["usage"]["input_tokens"],
                "completion_tokens": data["usage"]["output_tokens"],
                "total_tokens": data["usage"]["input_tokens"] + data["usage"]["output_tokens"],
            },
            latency_ms=latency_ms,
            raw_response=data,
            finish_reason=data.get("stop_reason", "end_turn"),
        )

    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        """List available Claude models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
