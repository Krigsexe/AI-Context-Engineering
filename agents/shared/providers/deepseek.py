# =============================================================================
# ODIN v7.0 - DeepSeek Provider
# =============================================================================
# Code-focused: https://deepseek.com
# =============================================================================

import os
import time
from typing import List, Optional
import requests

from .base import BaseLLMProvider, Message, LLMResponse


class DeepSeekProvider(BaseLLMProvider):
    """
    DeepSeek provider for code-focused models.

    Models: DeepSeek Coder, DeepSeek Chat
    """

    API_URL = "https://api.deepseek.com/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-coder")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "deepseek"

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using DeepSeek API."""
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        ds_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": ds_messages,
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
            usage=data.get("usage", {}),
            latency_ms=latency_ms,
            raw_response=data,
            finish_reason=choice.get("finish_reason", "stop"),
        )

    def is_available(self) -> bool:
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        return ["deepseek-coder", "deepseek-chat"]
