# =============================================================================
# ODIN v7.0 - Universal LLM Client
# =============================================================================
# Provider-agnostic client with fallback and consensus support
# =============================================================================

import os
import logging
from typing import List, Dict, Any

from .providers import (
    BaseLLMProvider,
    Message,
    LLMResponse,
    get_provider,
    list_providers,
)

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def create(provider_name: str, **kwargs) -> BaseLLMProvider:
        """Create a provider instance by name."""
        return get_provider(provider_name, **kwargs)

    @staticmethod
    def list_available() -> List[str]:
        """List all available providers."""
        return list_providers()


class LLMClient:
    """
    Universal LLM client with fallback and consensus support.

    Features:
    - Provider-agnostic interface
    - Automatic fallback chain
    - Multi-model consensus for verification
    - Configuration via environment or explicit params
    """

    def __init__(
        self,
        primary_provider: str = None,
        primary_model: str = None,
        fallback_providers: List[Dict[str, str]] = None,
        consensus_providers: List[Dict[str, str]] = None,
    ):
        """
        Initialize the LLM client.

        Args:
            primary_provider: Primary provider name (default: from env)
            primary_model: Primary model name (default: from env)
            fallback_providers: List of fallback configs [{"provider": "...", "model": "..."}]
            consensus_providers: List of consensus configs for verification
        """
        self.primary_provider = primary_provider or os.getenv("ODIN_LLM_PROVIDER", "ollama")
        self.primary_model = primary_model or os.getenv("ODIN_LLM_MODEL", "qwen2.5:7b")
        self.fallback_configs = fallback_providers or []
        self.consensus_configs = consensus_providers or []

        # Initialize primary provider
        self._primary = LLMProviderFactory.create(
            self.primary_provider,
            model=self.primary_model
        )

        # Initialize fallbacks
        self._fallbacks = []
        for config in self.fallback_configs:
            try:
                provider = LLMProviderFactory.create(
                    config["provider"],
                    model=config.get("model")
                )
                if provider.is_available():
                    self._fallbacks.append(provider)
            except Exception as e:
                logger.warning(f"Failed to initialize fallback {config}: {e}")

        # Initialize consensus providers
        self._consensus = []
        for config in self.consensus_configs:
            try:
                provider = LLMProviderFactory.create(
                    config["provider"],
                    model=config.get("model")
                )
                if provider.is_available():
                    self._consensus.append(provider)
            except Exception as e:
                logger.warning(f"Failed to initialize consensus {config}: {e}")

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        use_fallback: bool = True,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using the primary provider with fallback.

        Args:
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            use_fallback: Whether to try fallbacks on failure
            **kwargs: Additional provider-specific options

        Returns:
            LLMResponse from the first successful provider
        """
        # Try primary provider
        try:
            return self._primary.generate(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"Primary provider failed: {e}")
            if not use_fallback:
                raise

        # Try fallbacks
        for fallback in self._fallbacks:
            try:
                logger.info(f"Trying fallback provider: {fallback.name}")
                return fallback.generate(
                    messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            except Exception as e:
                logger.warning(f"Fallback {fallback.name} failed: {e}")

        raise RuntimeError("All providers failed")

    def generate_with_consensus(
        self,
        messages: List[Message],
        min_agreement: float = 0.67,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate with multi-model consensus verification.

        Args:
            messages: List of messages
            min_agreement: Minimum agreement ratio required
            **kwargs: Additional options

        Returns:
            Dict with:
                - response: Primary response
                - consensus: True if agreement >= min_agreement
                - agreement_score: Actual agreement ratio
                - responses: All responses (for debugging)
        """
        if not self._consensus:
            # No consensus providers configured, just return primary
            response = self.generate(messages, **kwargs)
            return {
                "response": response,
                "consensus": True,
                "agreement_score": 1.0,
                "responses": [response],
            }

        # Get responses from all consensus providers
        responses = []

        # Include primary
        try:
            primary_response = self._primary.generate(messages, **kwargs)
            responses.append(primary_response)
        except Exception as e:
            logger.warning(f"Primary failed in consensus: {e}")

        # Get from consensus providers
        for provider in self._consensus:
            try:
                response = provider.generate(messages, **kwargs)
                responses.append(response)
            except Exception as e:
                logger.warning(f"Consensus provider {provider.name} failed: {e}")

        if not responses:
            raise RuntimeError("No providers returned responses")

        # Simple consensus: compare response lengths and key phrases
        # In production, use semantic similarity
        primary_content = responses[0].content

        agreement_count = 1  # Primary agrees with itself
        for r in responses[1:]:
            if self._responses_agree(primary_content, r.content):
                agreement_count += 1

        agreement_score = agreement_count / len(responses)

        return {
            "response": responses[0],
            "consensus": agreement_score >= min_agreement,
            "agreement_score": agreement_score,
            "responses": responses,
        }

    def _responses_agree(self, response1: str, response2: str) -> bool:
        """
        Simple agreement check between two responses.
        Override for more sophisticated comparison.
        """
        # Normalize
        r1 = response1.lower().strip()
        r2 = response2.lower().strip()

        # Check for explicit agreement/disagreement markers
        if "true" in r1 and "true" in r2:
            return True
        if "false" in r1 and "false" in r2:
            return True
        if "true" in r1 and "false" in r2:
            return False
        if "false" in r1 and "true" in r2:
            return False

        # Check for significant content overlap (simple Jaccard)
        words1 = set(r1.split())
        words2 = set(r2.split())
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return True

        jaccard = intersection / union
        return jaccard > 0.3  # 30% overlap threshold

    def is_available(self) -> bool:
        """Check if at least one provider is available."""
        if self._primary.is_available():
            return True
        return any(f.is_available() for f in self._fallbacks)

    def list_available_providers(self) -> List[str]:
        """List configured and available providers."""
        available = []
        if self._primary.is_available():
            available.append(self._primary.name)
        for f in self._fallbacks:
            if f.is_available():
                available.append(f.name)
        return available


def create_client_from_config(config: Dict[str, Any]) -> LLMClient:
    """
    Create an LLM client from a configuration dictionary.

    Args:
        config: Configuration dict (from odin.config.yaml)

    Returns:
        Configured LLMClient instance
    """
    primary = config.get("primary", {})
    fallback = config.get("fallback", [])
    consensus = config.get("consensus", {}).get("providers", [])

    return LLMClient(
        primary_provider=primary.get("provider", "ollama"),
        primary_model=primary.get("model", "qwen2.5:7b"),
        fallback_providers=fallback,
        consensus_providers=consensus if config.get("consensus", {}).get("enabled") else [],
    )
