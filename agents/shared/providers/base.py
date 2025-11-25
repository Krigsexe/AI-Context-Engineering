# =============================================================================
# ODIN v7.0 - Base LLM Provider Interface
# =============================================================================
# All providers must implement this interface
# =============================================================================

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time


@dataclass
class Message:
    """A message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0
    raw_response: Any = None
    finish_reason: str = ""


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    All providers (Ollama, Anthropic, OpenAI, etc.) must implement this interface.
    This ensures consistent behavior across all providers and enables easy switching.
    """

    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens to generate
            stop: Stop sequences
            **kwargs: Provider-specific options

        Returns:
            LLMResponse with the generated content
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is configured and reachable.

        Returns:
            True if provider can be used, False otherwise
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models for this provider.

        Returns:
            List of model names/IDs
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'ollama', 'anthropic')."""
        pass

    def generate_with_retry(
        self,
        messages: List[Message],
        max_retries: int = 3,
        **kwargs
    ) -> LLMResponse:
        """
        Generate with automatic retry on failure.

        Args:
            messages: List of messages
            max_retries: Maximum retry attempts
            **kwargs: Passed to generate()

        Returns:
            LLMResponse

        Raises:
            Exception: If all retries fail
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                return self.generate(messages, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        raise last_error

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Default implementation uses rough approximation.
        Override for accurate counting.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough approximation: ~4 characters per token
        return len(text) // 4
