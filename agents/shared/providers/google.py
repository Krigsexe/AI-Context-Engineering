# =============================================================================
# ODIN v7.0 - Google Provider
# =============================================================================
# Gemini models: https://ai.google.dev
# =============================================================================

import os
import time
from typing import List, Optional
import requests

from .base import BaseLLMProvider, Message, LLMResponse


class GoogleProvider(BaseLLMProvider):
    """
    Google provider for Gemini models.

    Models: Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "google"

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Google Gemini API."""
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        start_time = time.time()
        model = kwargs.get("model", self.model)

        # Convert messages to Gemini format
        contents = []
        system_instruction = None

        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m.content}]
                })

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        if stop:
            payload["generationConfig"]["stopSequences"] = stop

        response = requests.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        latency_ms = (time.time() - start_time) * 1000

        candidate = data["candidates"][0]
        content = candidate["content"]["parts"][0]["text"]

        usage = data.get("usageMetadata", {})

        return LLMResponse(
            content=content,
            model=model,
            provider=self.name,
            usage={
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0),
            },
            latency_ms=latency_ms,
            raw_response=data,
            finish_reason=candidate.get("finishReason", "STOP"),
        )

    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        """List available Gemini models."""
        return [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-2.0-flash-exp",
        ]
