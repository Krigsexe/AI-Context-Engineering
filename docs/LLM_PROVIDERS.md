# ODIN v7.0 - LLM Providers / Fournisseurs LLM

**Principle / Principe**: User choice is absolute. ODIN supports ALL providers.
**Principe**: Le choix utilisateur est absolu. ODIN supporte TOUS les fournisseurs.

---

## Supported Providers / Fournisseurs Supportes

### Cloud APIs

| Provider | Models | Endpoint | Auth | Free Tier |
|----------|--------|----------|------|-----------|
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku | api.anthropic.com | API Key | No |
| **OpenAI** | GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo, o1 | api.openai.com | API Key | No |
| **Google** | Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0 | generativelanguage.googleapis.com | API Key | Yes (limited) |
| **xAI** | Grok-2, Grok-2 mini | api.x.ai | API Key | No |
| **Groq** | Llama 3.1 70B, Mixtral 8x7B, Gemma 2 | api.groq.com | API Key | Yes (rate limited) |
| **Mistral AI** | Mistral Large, Mistral Medium, Mistral Small | api.mistral.ai | API Key | No |
| **Cohere** | Command R+, Command R | api.cohere.ai | API Key | Yes (trial) |
| **AI21 Labs** | Jamba 1.5 | api.ai21.com | API Key | Yes (trial) |
| **Together AI** | Llama, Mixtral, Qwen, many others | api.together.xyz | API Key | Yes (limited) |
| **Fireworks AI** | Llama, Mixtral, FireFunction | api.fireworks.ai | API Key | Yes (limited) |
| **Perplexity** | pplx-70b-online, pplx-7b-chat | api.perplexity.ai | API Key | No |
| **DeepSeek** | DeepSeek Coder, DeepSeek Chat | api.deepseek.com | API Key | Yes (limited) |
| **Cerebras** | Llama 3.1 (fast inference) | api.cerebras.ai | API Key | Yes (beta) |

### Local / Self-Hosted

| Provider | Models | Requirements | GPU Required |
|----------|--------|--------------|--------------|
| **Ollama** | Qwen, Llama, Mistral, DeepSeek, Phi, Gemma, CodeLlama, etc. | Docker or native install | Optional (CPU fallback) |
| **vLLM** | Any HuggingFace model | Python, CUDA | Yes (recommended) |
| **llama.cpp** | GGUF quantized models | C++ build | Optional |
| **LocalAI** | Multiple formats | Docker | Optional |
| **LM Studio** | GGUF models | Desktop app | Optional |
| **Jan** | Multiple formats | Desktop app | Optional |
| **GPT4All** | Various quantized | Desktop/CLI | No |
| **text-generation-webui** | HuggingFace models | Python | Yes (recommended) |
| **TGI (Text Generation Inference)** | HuggingFace models | Docker, CUDA | Yes |
| **Tabby** | Code models | Rust | Optional |

### HuggingFace Ecosystem

| Option | Description | Requirements |
|--------|-------------|--------------|
| **HF Inference API** | Cloud inference | API Key |
| **HF Inference Endpoints** | Dedicated deployment | API Key + subscription |
| **HF Transformers (local)** | Direct model loading | Python, GPU recommended |
| **HF TGI** | Optimized serving | Docker, GPU |

### Specialized Providers

| Provider | Specialty | Use Case |
|----------|-----------|----------|
| **Replicate** | Model hosting | Any open model |
| **Banana** | Serverless GPU | Custom deployments |
| **Modal** | Serverless compute | Custom inference |
| **RunPod** | GPU rental | Self-hosted |
| **Vast.ai** | GPU marketplace | Self-hosted |
| **Lambda Labs** | GPU cloud | Self-hosted |

---

## Configuration / Configuration

### Environment Variables

```bash
# Provider selection (choose one or multiple for consensus)
ODIN_LLM_PROVIDER=ollama                    # Primary provider
ODIN_LLM_PROVIDERS=ollama,anthropic,openai  # Multiple for consensus oracle

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1  # Can be changed for proxies

# Google Gemini
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-1.5-pro

# xAI Grok
XAI_API_KEY=...
XAI_MODEL=grok-2

# Groq (fast inference)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-70b-versatile

# Mistral
MISTRAL_API_KEY=...
MISTRAL_MODEL=mistral-large-latest

# Together AI
TOGETHER_API_KEY=...
TOGETHER_MODEL=meta-llama/Llama-3.1-70B-Instruct

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# vLLM (local)
VLLM_BASE_URL=http://localhost:8000
VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct

# HuggingFace
HF_API_KEY=hf_...
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
HF_INFERENCE_ENDPOINT=https://...  # Optional dedicated endpoint

# DeepSeek
DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-coder

# Custom OpenAI-compatible endpoint
CUSTOM_LLM_BASE_URL=https://your-server.com/v1
CUSTOM_LLM_API_KEY=...
CUSTOM_LLM_MODEL=your-model
```

### Configuration File (odin.config.yaml)

```yaml
llm:
  # Primary provider for main tasks
  primary:
    provider: ollama
    model: qwen2.5:7b
    temperature: 0.2
    max_tokens: 4096

  # Fallback chain (tried in order if primary fails)
  fallback:
    - provider: groq
      model: llama-3.1-70b-versatile
    - provider: anthropic
      model: claude-3-5-sonnet-20241022

  # Consensus oracle (multiple models for verification)
  consensus:
    enabled: true
    min_agreement: 0.67  # 2/3 majority
    providers:
      - provider: ollama
        model: qwen2.5:7b
      - provider: ollama
        model: llama3.1:8b
      - provider: groq
        model: mixtral-8x7b-32768

  # Specialized models by task type
  specialized:
    code_generation:
      provider: ollama
      model: deepseek-coder:6.7b
    code_review:
      provider: anthropic
      model: claude-3-5-sonnet-20241022
    research:
      provider: perplexity
      model: pplx-70b-online
    fast_inference:
      provider: groq
      model: llama-3.1-8b-instant

# Provider-specific settings
providers:
  ollama:
    base_url: http://localhost:11434
    timeout: 300
    gpu_layers: -1  # Auto-detect

  anthropic:
    max_retries: 3
    timeout: 120

  openai:
    organization: org-...  # Optional
    timeout: 120

  groq:
    timeout: 60  # Fast inference
```

---

## Universal Provider Interface / Interface Universelle

### Python Abstraction

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Message:
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    usage: Dict[str, int]  # tokens
    latency_ms: float
    raw_response: Any  # Provider-specific

class BaseLLMProvider(ABC):
    """Universal interface for all LLM providers"""

    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and reachable"""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models for this provider"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

# Provider implementations
class OllamaProvider(BaseLLMProvider): ...
class AnthropicProvider(BaseLLMProvider): ...
class OpenAIProvider(BaseLLMProvider): ...
class GoogleProvider(BaseLLMProvider): ...
class GroqProvider(BaseLLMProvider): ...
class MistralProvider(BaseLLMProvider): ...
class TogetherProvider(BaseLLMProvider): ...
class HuggingFaceProvider(BaseLLMProvider): ...
class DeepSeekProvider(BaseLLMProvider): ...
class XAIProvider(BaseLLMProvider): ...
class VLLMProvider(BaseLLMProvider): ...
class CustomOpenAICompatibleProvider(BaseLLMProvider): ...

# Provider factory
class LLMProviderFactory:
    _providers = {
        "ollama": OllamaProvider,
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "google": GoogleProvider,
        "groq": GroqProvider,
        "mistral": MistralProvider,
        "together": TogetherProvider,
        "huggingface": HuggingFaceProvider,
        "deepseek": DeepSeekProvider,
        "xai": XAIProvider,
        "vllm": VLLMProvider,
        "custom": CustomOpenAICompatibleProvider,
    }

    @classmethod
    def get(cls, provider_name: str, **config) -> BaseLLMProvider:
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return cls._providers[provider_name](**config)

    @classmethod
    def register(cls, name: str, provider_class: type):
        """Allow community to register new providers"""
        cls._providers[name] = provider_class
```

---

## User Choice Scenarios / Scenarios de Choix Utilisateur

### Scenario 1: Full Local (Privacy-First)

```yaml
# User with GPU, wants 100% local
llm:
  primary:
    provider: ollama
    model: qwen2.5:14b  # Larger local model
  consensus:
    providers:
      - provider: ollama
        model: qwen2.5:14b
      - provider: ollama
        model: llama3.1:8b
      - provider: ollama
        model: deepseek-coder:6.7b
```

### Scenario 2: Cloud-First (Performance)

```yaml
# User wants best performance, has budget
llm:
  primary:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
  fallback:
    - provider: openai
      model: gpt-4o
  consensus:
    providers:
      - provider: anthropic
        model: claude-3-5-sonnet-20241022
      - provider: openai
        model: gpt-4o
      - provider: google
        model: gemini-1.5-pro
```

### Scenario 3: Hybrid (Cost-Optimized)

```yaml
# User wants balance of cost and quality
llm:
  primary:
    provider: groq  # Free tier, fast
    model: llama-3.1-70b-versatile
  fallback:
    - provider: anthropic  # Premium fallback
      model: claude-3-haiku-20240307
  specialized:
    code_generation:
      provider: ollama  # Local for code
      model: deepseek-coder:6.7b
```

### Scenario 4: CPU-Only (No GPU)

```yaml
# User with no GPU
llm:
  primary:
    provider: groq  # Cloud inference
    model: llama-3.1-8b-instant
  fallback:
    - provider: ollama
      model: qwen2.5:3b  # Small model, CPU OK
```

### Scenario 5: Enterprise (Self-Hosted)

```yaml
# Enterprise with own infrastructure
llm:
  primary:
    provider: vllm
    model: Qwen/Qwen2.5-72B-Instruct
    base_url: https://internal-llm.company.com
  consensus:
    providers:
      - provider: vllm
        model: Qwen/Qwen2.5-72B-Instruct
      - provider: vllm
        model: meta-llama/Llama-3.1-70B-Instruct
```

---

## Adding New Providers / Ajouter de Nouveaux Fournisseurs

ODIN is designed for community contributions. To add a new provider:

### 1. Implement the interface

```python
# agents/shared/providers/my_new_provider.py

from .base import BaseLLMProvider, Message, LLMResponse

class MyNewProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or os.getenv("MY_PROVIDER_API_KEY")
        self.base_url = base_url or "https://api.myprovider.com"
        self.model = model or "default-model"

    def generate(self, messages, temperature=0.2, max_tokens=4096, **kwargs):
        # Implementation
        ...

    def is_available(self) -> bool:
        return self.api_key is not None

    def list_models(self) -> List[str]:
        # Query API for available models
        ...

    @property
    def name(self) -> str:
        return "my_new_provider"
```

### 2. Register the provider

```python
# agents/shared/providers/__init__.py

from .my_new_provider import MyNewProvider
LLMProviderFactory.register("my_new_provider", MyNewProvider)
```

### 3. Document in this file

Add entry to the providers table above.

### 4. Submit PR

Follow CONTRIBUTING.md guidelines.

---

## Model Recommendations by Use Case

| Use Case | Recommended Models | Why |
|----------|-------------------|-----|
| **Code Generation** | DeepSeek Coder, Claude 3.5 Sonnet, GPT-4o | Trained on code, high accuracy |
| **Code Review** | Claude 3.5 Sonnet, GPT-4o | Strong reasoning |
| **Fast Iteration** | Groq (Llama 3.1), Claude 3 Haiku | Low latency |
| **Research** | Perplexity, Gemini 1.5 Pro | Web access, large context |
| **Privacy-Critical** | Ollama (any), vLLM, llama.cpp | 100% local |
| **Long Context** | Gemini 1.5 Pro (1M), Claude 3 (200K) | Large context windows |
| **Multilingual** | GPT-4o, Claude 3.5, Qwen 2.5 | Strong multilingual |
| **Low Resource** | Qwen 2.5 3B, Phi-3 Mini | Small models |

---

## Cost Comparison / Comparaison des Couts

| Provider | Model | Input ($/1M tokens) | Output ($/1M tokens) |
|----------|-------|---------------------|----------------------|
| Anthropic | Claude 3.5 Sonnet | $3.00 | $15.00 |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 |
| OpenAI | GPT-4o | $2.50 | $10.00 |
| OpenAI | GPT-4o mini | $0.15 | $0.60 |
| Google | Gemini 1.5 Pro | $1.25 | $5.00 |
| Google | Gemini 1.5 Flash | $0.075 | $0.30 |
| Groq | Llama 3.1 70B | Free (rate limited) | Free |
| Mistral | Large | $2.00 | $6.00 |
| Together | Llama 3.1 70B | $0.88 | $0.88 |
| DeepSeek | Coder | $0.14 | $0.28 |
| Ollama | Any | Free (local compute) | Free |

*Prices as of November 2025, subject to change.*

---

## Offline Mode / Mode Hors-Ligne

ODIN supports full offline operation with local providers:

```yaml
# Offline-only configuration
llm:
  primary:
    provider: ollama
    model: qwen2.5:7b

  # Disable cloud features
  cloud_enabled: false

  # Pre-download models
  preload_models:
    - qwen2.5:7b
    - llama3.1:8b
    - deepseek-coder:6.7b
```

Setup script for offline:
```bash
# Pre-download all models
./scripts/download_models.sh --offline-bundle

# Creates:
# - models/qwen2.5-7b.gguf
# - models/llama3.1-8b.gguf
# - models/deepseek-coder-6.7b.gguf
```

---

*This document is community-maintained. Contributions welcome.*
*Ce document est maintenu par la communaute. Contributions bienvenues.*
