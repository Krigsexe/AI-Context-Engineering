# =============================================================================
# ODIN v7.0 - Agent Framework
# =============================================================================
# Multi-agent orchestration for reliable AI-assisted development
# =============================================================================

from .shared import (
    # Base classes
    BaseAgent,
    AgentRegistry,
    AgentStatus,
    AgentCapability,
    AgentResult,
    ConfidenceLevel,
    agent,
    # LLM
    LLMClient,
    LLMProviderFactory,
    create_client_from_config,
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    get_provider,
    list_providers,
    # Messaging
    MessageBus,
    AsyncMessageBus,
    Message,
    MessagePriority,
    # State
    StateStore,
    InMemoryStateStore,
    Task,
    TaskStatus,
    Checkpoint,
    CheckpointType,
    # Integrity
    IntegrityMonitor,
    semantic_hash_file,
    project_sih,
)

# Import agent implementations (triggers registration)
from .cognitive import IntakeAgent, DevAgent, RetrievalAgent
from .oracle import OracleCodeAgent

__version__ = "7.0.0"

__all__ = [
    # Version
    "__version__",
    # Base
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
    # Integrity
    "IntegrityMonitor",
    "semantic_hash_file",
    "project_sih",
    # Agents
    "IntakeAgent",
    "DevAgent",
    "RetrievalAgent",
    "OracleCodeAgent",
]
