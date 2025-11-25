# =============================================================================
# ODIN v7.0 - LLM Provider Registry
# =============================================================================
# All providers are registered here for the factory pattern
# Community contributions: Add your provider here
# =============================================================================

from .base import BaseLLMProvider, Message, LLMResponse
from .ollama import OllamaProvider
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .google import GoogleProvider
from .groq import GroqProvider
from .together import TogetherProvider
from .deepseek import DeepSeekProvider
from .huggingface import HuggingFaceProvider
from .custom import CustomOpenAIProvider

# Provider registry
PROVIDERS = {
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "google": GoogleProvider,
    "groq": GroqProvider,
    "together": TogetherProvider,
    "deepseek": DeepSeekProvider,
    "huggingface": HuggingFaceProvider,
    "custom": CustomOpenAIProvider,
}

def get_provider(name: str, **kwargs) -> BaseLLMProvider:
    """Get a provider instance by name."""
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}")
    return PROVIDERS[name](**kwargs)

def register_provider(name: str, provider_class: type):
    """Register a new provider (for community extensions)."""
    PROVIDERS[name] = provider_class

def list_providers() -> list:
    """List all available providers."""
    return list(PROVIDERS.keys())

__all__ = [
    "BaseLLMProvider",
    "Message",
    "LLMResponse",
    "get_provider",
    "register_provider",
    "list_providers",
    "PROVIDERS",
]
