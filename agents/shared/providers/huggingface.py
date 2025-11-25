# =============================================================================
# ODIN v7.0 - HuggingFace Provider
# =============================================================================
# Inference API: https://huggingface.co/inference-api
# =============================================================================

import os
import time
from typing import List, Optional
import requests

from .base import BaseLLMProvider, Message, LLMResponse


class HuggingFaceProvider(BaseLLMProvider):
    """
    HuggingFace Inference API provider.

    Supports thousands of models from the HuggingFace Hub.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        endpoint: str = None,
        timeout: int = 120
    ):
        self.api_key = api_key or os.getenv("HF_API_KEY")
        self.model = model or os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        self.endpoint = endpoint or os.getenv("HF_INFERENCE_ENDPOINT")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "huggingface"

    def _get_api_url(self) -> str:
        if self.endpoint:
            return self.endpoint
        return f"https://api-inference.huggingface.co/models/{self.model}"

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using HuggingFace Inference API."""
        if not self.api_key:
            raise ValueError("HF_API_KEY not set")

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Build prompt from messages
        prompt_parts = []
        for m in messages:
            if m.role == "system":
                prompt_parts.append(f"System: {m.content}")
            elif m.role == "user":
                prompt_parts.append(f"User: {m.content}")
            elif m.role == "assistant":
                prompt_parts.append(f"Assistant: {m.content}")

        prompt_parts.append("Assistant:")
        prompt = "\n\n".join(prompt_parts)

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "return_full_text": False,
            }
        }

        if stop:
            payload["parameters"]["stop_sequences"] = stop

        response = requests.post(
            self._get_api_url(),
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        latency_ms = (time.time() - start_time) * 1000

        # Handle different response formats
        if isinstance(data, list):
            content = data[0].get("generated_text", "")
        else:
            content = data.get("generated_text", "")

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.name,
            usage={},  # HF API doesn't return token counts
            latency_ms=latency_ms,
            raw_response=data,
            finish_reason="stop",
        )

    def is_available(self) -> bool:
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        return [
            "meta-llama/Llama-3.1-8B-Instruct",
            "meta-llama/Llama-3.1-70B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "microsoft/Phi-3-mini-4k-instruct",
            "Qwen/Qwen2.5-7B-Instruct",
        ]
