# =============================================================================
# ODIN v7.0 - Shared Agent Components
# =============================================================================
# Core infrastructure for all ODIN agents
# =============================================================================

# Base agent class and registry
from .base_agent import (
    BaseAgent,
    AgentRegistry,
    AgentStatus,
    AgentCapability,
    AgentResult,
    ConfidenceLevel,
    agent,
)

# LLM client and providers
from .llm_client import (
    LLMClient,
    LLMProviderFactory,
    create_client_from_config,
)

# Provider types
from .providers import (
    BaseLLMProvider,
    Message as LLMMessage,
    LLMResponse,
    get_provider,
    register_provider,
    list_providers,
)

# Message bus for inter-agent communication
from .message_bus import (
    MessageBus,
    AsyncMessageBus,
    Message,
    MessagePriority,
)

# State persistence
from .state_store import (
    StateStore,
    InMemoryStateStore,
    Task,
    TaskStatus,
    Checkpoint,
    CheckpointType,
    AgentLog,
)

# Integrity monitoring
from .integrity import (
    IntegrityMonitor,
    semantic_hash_file,
    project_sih,
    compare_sih,
    compute_project_hash,
)

__all__ = [
    # Base agent
    "BaseAgent",
    "AgentRegistry",
    "AgentStatus",
    "AgentCapability",
    "AgentResult",
    "ConfidenceLevel",
    "agent",
    # LLM
    "LLMClient",
    "LLMProviderFactory",
    "create_client_from_config",
    "BaseLLMProvider",
    "LLMMessage",
    "LLMResponse",
    "get_provider",
    "register_provider",
    "list_providers",
    # Messaging
    "MessageBus",
    "AsyncMessageBus",
    "Message",
    "MessagePriority",
    # State
    "StateStore",
    "InMemoryStateStore",
    "Task",
    "TaskStatus",
    "Checkpoint",
    "CheckpointType",
    "AgentLog",
    # Integrity
    "IntegrityMonitor",
    "semantic_hash_file",
    "project_sih",
    "compare_sih",
    "compute_project_hash",
]
