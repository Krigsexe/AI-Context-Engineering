# =============================================================================
# ODIN v7.0 - Custom OpenAI-Compatible Provider
# =============================================================================
# For any OpenAI-compatible endpoint (vLLM, LocalAI, LM Studio, etc.)
# =============================================================================

import os
import time
from typing import List, Optional
import requests

from .base import BaseLLMProvider, Message, LLMResponse


class CustomOpenAIProvider(BaseLLMProvider):
    """
    Custom provider for any OpenAI-compatible API endpoint.

    Use this for:
    - vLLM servers
    - LocalAI
    - LM Studio
    - Tabby
    - Any self-hosted OpenAI-compatible API
    """

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        model: str = None,
        timeout: int = 300
    ):
        self.base_url = base_url or os.getenv("CUSTOM_LLM_BASE_URL", "http://localhost:8000/v1")
        self.api_key = api_key or os.getenv("CUSTOM_LLM_API_KEY", "")
        self.model = model or os.getenv("CUSTOM_LLM_MODEL", "default")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "custom"

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI-compatible API."""
        start_time = time.time()

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        custom_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
        ]

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": custom_messages,
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
            usage=data.get("usage", {}),
            latency_ms=latency_ms,
            raw_response=data,
            finish_reason=choice.get("finish_reason", "stop"),
        )

    def is_available(self) -> bool:
        """Check if endpoint is reachable."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except Exception:
            return True  # Assume available if we can't check

    def list_models(self) -> List[str]:
        """Try to list models from the endpoint."""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return [self.model]
