#!/usr/bin/env python3
"""
ODIN v7.0 - Multi-Provider Example

This example demonstrates:
1. Configuring multiple LLM providers
2. Using fallback chains
3. Consensus verification across providers
"""

import asyncio
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import (
    LLMClient,
    LLMProviderFactory,
    list_providers,
    LLMMessage,
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


async def main():
    """Run multi-provider example."""
    print_section("ODIN v7.0 - Multi-Provider Example")

    # List all available providers
    print("\n📋 All supported providers:")
    for provider_name in sorted(list_providers()):
        print(f"  - {provider_name}")

    # Check which providers are actually available
    print("\n🔍 Checking provider availability...")

    available_providers = []
    for provider_name in list_providers():
        try:
            provider = LLMProviderFactory.create(provider_name)
            if provider.is_available():
                available_providers.append(provider_name)
                print(f"  ✓ {provider_name}: Available")
            else:
                print(f"  ✗ {provider_name}: Not configured")
        except Exception as e:
            print(f"  ✗ {provider_name}: Error - {e}")

    if not available_providers:
        print("\n⚠ No providers available!")
        print("\nTo configure providers:")
        print("  - Ollama: Install and run 'ollama pull qwen2.5:7b'")
        print("  - Anthropic: Set ANTHROPIC_API_KEY environment variable")
        print("  - OpenAI: Set OPENAI_API_KEY environment variable")
        print("  - Groq: Set GROQ_API_KEY environment variable")
        return

    print_section("Example 1: Single Provider")

    # Use first available provider
    primary = available_providers[0]
    print(f"\n🎯 Using primary provider: {primary}")

    client = LLMClient(primary_provider=primary)

    messages = [
        LLMMessage(role="system", content="You are a helpful assistant. Be concise."),
        LLMMessage(role="user", content="What is 2 + 2?"),
    ]

    print("\n📤 Sending request...")
    response = client.generate(messages, max_tokens=100)

    print(f"📥 Response from {response.provider}/{response.model}:")
    print(f"   {response.content}")
    print(f"   Latency: {response.latency_ms:.0f}ms")

    # Example 2: Fallback chain
    if len(available_providers) >= 2:
        print_section("Example 2: Fallback Chain")

        fallback = available_providers[1]
        print(f"\n🔗 Fallback chain: {primary} → {fallback}")

        client_with_fallback = LLMClient(
            primary_provider=primary,
            fallback_providers=[fallback],
        )

        print("\n📤 Sending request (will use fallback if primary fails)...")
        response = client_with_fallback.generate(messages, max_tokens=100)

        print(f"📥 Response from {response.provider}/{response.model}:")
        print(f"   {response.content}")

    # Example 3: Consensus (if 2+ providers)
    if len(available_providers) >= 2:
        print_section("Example 3: Consensus Verification")

        print(f"\n🤝 Using providers for consensus: {available_providers[:2]}")

        consensus_client = LLMClient(
            primary_provider=available_providers[0],
            fallback_providers=available_providers[1:],
        )

        consensus_messages = [
            LLMMessage(role="user", content="Is Python a programming language? Answer yes or no."),
        ]

        print("\n📤 Querying multiple providers for consensus...")
        result = consensus_client.generate_with_consensus(
            consensus_messages,
            min_agreement=0.5,
            max_tokens=50,
        )

        print(f"\n📊 Consensus Results:")
        print(f"   Agreement: {result['agreement_ratio']*100:.0f}%")
        print(f"   Consensus reached: {result['has_consensus']}")
        print(f"   Responses:")
        for i, resp in enumerate(result['responses'], 1):
            print(f"     {i}. [{resp.provider}] {resp.content[:100]}")

    print_section("Provider Configuration Reference")

    print("""
To configure different providers, set these environment variables:

Local (no API key needed):
  - Ollama: Just install Ollama and pull a model

Cloud Providers:
  - ANTHROPIC_API_KEY    - Anthropic (Claude)
  - OPENAI_API_KEY       - OpenAI (GPT-4, etc.)
  - GOOGLE_API_KEY       - Google (Gemini)
  - GROQ_API_KEY         - Groq (fast inference)
  - TOGETHER_API_KEY     - Together.ai
  - DEEPSEEK_API_KEY     - DeepSeek
  - HUGGINGFACE_API_KEY  - Hugging Face

Configuration file (odin.config.yaml):
```yaml
llm:
  primary:
    provider: ollama
    model: qwen2.5:7b
  fallback:
    - provider: anthropic
      model: claude-3-haiku-20240307
  consensus:
    enabled: true
    min_agreement: 0.67
```
""")

    print("\nExample complete!")


if __name__ == "__main__":
    asyncio.run(main())
