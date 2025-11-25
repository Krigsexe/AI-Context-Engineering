# =============================================================================
# ODIN v7.0 - Together AI Provider
# =============================================================================
# Many open models: https://together.ai
# =============================================================================

import os
import time
from typing import List, Optional
import requests

from .base import BaseLLMProvider, Message, LLMResponse


class TogetherProvider(BaseLLMProvider):
    """
    Together AI provider.

    Supports many open models: Llama, Mistral, Qwen, and more.
    """

    API_URL = "https://api.together.xyz/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ):
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self.model = model or os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3.1-70B-Instruct")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "together"

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Together API."""
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY not set")

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        together_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": together_messages,
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
        return [
            "meta-llama/Llama-3.1-70B-Instruct",
            "meta-llama/Llama-3.1-8B-Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-ai/deepseek-coder-33b-instruct",
        ]
