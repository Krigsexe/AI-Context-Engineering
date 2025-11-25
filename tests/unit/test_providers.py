# =============================================================================
# ODIN v7.0 - Unit Tests: LLM Providers
# =============================================================================

import pytest
from unittest.mock import Mock, patch, MagicMock

from agents.shared.providers import (
    BaseLLMProvider,
    Message,
    LLMResponse,
    get_provider,
    list_providers,
)
from agents.shared.providers.ollama import OllamaProvider
from agents.shared.providers.anthropic import AnthropicProvider
from agents.shared.providers.openai import OpenAIProvider


class TestMessage:
    """Test Message dataclass."""

    def test_message_creation(self):
        """Test basic message creation."""
        msg = Message(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_roles(self):
        """Test different message roles."""
        system = Message(role="system", content="You are helpful")
        user = Message(role="user", content="Hi")
        assistant = Message(role="assistant", content="Hello!")

        assert system.role == "system"
        assert user.role == "user"
        assert assistant.role == "assistant"


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_response_creation(self):
        """Test response creation."""
        response = LLMResponse(
            content="Test response",
            model="test-model",
            provider="test-provider",
            usage={"prompt_tokens": 10, "completion_tokens": 20},
            latency_ms=150.5,
            raw_response={"raw": "data"},
            finish_reason="stop",
        )

        assert response.content == "Test response"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.usage["prompt_tokens"] == 10
        assert response.latency_ms == 150.5
        assert response.finish_reason == "stop"


class TestProviderRegistry:
    """Test provider registry functions."""

    def test_list_providers(self):
        """Test listing providers."""
        providers = list_providers()

        assert isinstance(providers, list)
        assert "ollama" in providers
        assert "anthropic" in providers
        assert "openai" in providers

    def test_get_provider_ollama(self):
        """Test getting Ollama provider."""
        provider = get_provider("ollama")

        assert provider is not None
        assert isinstance(provider, OllamaProvider)

    def test_get_provider_invalid(self):
        """Test getting invalid provider raises error."""
        with pytest.raises(ValueError):
            get_provider("nonexistent-provider")


class TestOllamaProvider:
    """Test OllamaProvider."""

    def test_provider_name(self):
        """Test provider name."""
        provider = OllamaProvider()
        assert provider.name == "ollama"

    def test_default_model(self):
        """Test default model."""
        provider = OllamaProvider()
        assert provider.model == "qwen2.5:7b"

    def test_custom_model(self):
        """Test custom model."""
        provider = OllamaProvider(model="llama3.2:8b")
        assert provider.model == "llama3.2:8b"

    def test_custom_base_url(self):
        """Test custom base URL."""
        provider = OllamaProvider(base_url="http://custom:11434")
        assert provider.base_url == "http://custom:11434"

    @patch('requests.get')
    def test_list_models(self, mock_get):
        """Test listing models."""
        mock_get.return_value.json.return_value = {
            "models": [
                {"name": "llama3.2:8b"},
                {"name": "qwen2.5:7b"},
            ]
        }
        mock_get.return_value.status_code = 200

        provider = OllamaProvider()
        models = provider.list_models()

        assert "llama3.2:8b" in models
        assert "qwen2.5:7b" in models

    @patch('requests.get')
    def test_is_available_true(self, mock_get):
        """Test availability check - available."""
        mock_get.return_value.status_code = 200

        provider = OllamaProvider()
        assert provider.is_available() is True

    @patch('requests.get')
    def test_is_available_false(self, mock_get):
        """Test availability check - not available."""
        mock_get.side_effect = Exception("Connection refused")

        provider = OllamaProvider()
        assert provider.is_available() is False


class TestAnthropicProvider:
    """Test AnthropicProvider."""

    def test_provider_name(self):
        """Test provider name."""
        provider = AnthropicProvider(api_key="test-key")
        assert provider.name == "anthropic"

    def test_default_model(self):
        """Test default model."""
        provider = AnthropicProvider(api_key="test-key")
        assert "claude" in provider.model.lower()

    def test_requires_api_key(self):
        """Test that API key is stored."""
        provider = AnthropicProvider(api_key="sk-test-key")
        assert provider.api_key == "sk-test-key"

    def test_is_available_without_key(self):
        """Test availability without API key."""
        provider = AnthropicProvider(api_key="")
        assert provider.is_available() is False


class TestOpenAIProvider:
    """Test OpenAIProvider."""

    def test_provider_name(self):
        """Test provider name."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.name == "openai"

    def test_default_model(self):
        """Test default model."""
        provider = OpenAIProvider(api_key="test-key")
        assert "gpt" in provider.model.lower()

    def test_custom_base_url(self):
        """Test custom base URL for OpenAI-compatible APIs."""
        provider = OpenAIProvider(
            api_key="test-key",
            base_url="http://local-api:8000/v1"
        )
        assert provider.base_url == "http://local-api:8000/v1"
