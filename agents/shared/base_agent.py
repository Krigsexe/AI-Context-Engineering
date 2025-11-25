# =============================================================================
# ODIN v7.0 - Base Agent Class
# =============================================================================
# Foundation for all ODIN agents
# Provides lifecycle management, communication, and state handling
# =============================================================================

from __future__ import annotations
import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from .llm_client import LLMClient
from .message_bus import Message, MessageBus, MessagePriority
from .state_store import StateStore, InMemoryStateStore, TaskStatus, CheckpointType
from .providers import Message as LLMMessage

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle status."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


class ConfidenceLevel(Enum):
    """
    Confidence levels for agent outputs.

    Based on ODIN's epistemic honesty framework.
    """
    AXIOM = 4       # 100% - Deterministic/verified
    HIGH = 3        # 95%+ - Very confident
    MODERATE = 2    # 70-95% - Reasonably confident
    UNCERTAIN = 1   # 40-70% - Uncertain, needs verification
    UNKNOWN = 0     # <40% - Don't know, should not proceed


@dataclass
class AgentCapability:
    """Describes an agent capability."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    requires_approval: bool = False
    risk_level: str = "low"  # low, medium, high, critical


@dataclass
class AgentResult:
    """
    Result from agent execution.
    """
    success: bool
    data: Any
    confidence: ConfidenceLevel
    reasoning: str
    citations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "confidence": self.confidence.value,
            "confidence_name": self.confidence.name,
            "reasoning": self.reasoning,
            "citations": self.citations,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """
    Base class for all ODIN agents.

    Provides:
    - Lifecycle management (init, run, stop)
    - LLM client access
    - Message bus communication
    - State persistence
    - Checkpoint/rollback support
    - Confidence tracking
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        llm_client: Optional[LLMClient] = None,
        message_bus: Optional[MessageBus] = None,
        state_store: Optional[StateStore] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base agent.

        Args:
            agent_id: Unique agent identifier
            llm_client: Shared LLM client
            message_bus: Shared message bus
            state_store: Shared state store
            config: Agent-specific configuration
        """
        self.agent_id = agent_id or f"{self.name}-{uuid.uuid4().hex[:8]}"
        self.llm = llm_client or LLMClient()
        self.bus = message_bus
        self.store = state_store or InMemoryStateStore()
        self.config = config or {}

        self._status = AgentStatus.INITIALIZING
        self._current_task_id: Optional[str] = None
        self._handlers: Dict[str, Callable] = {}

        # Register default message handlers
        self._register_handlers()

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent type name (e.g., 'dev', 'oracle', 'mcp')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable agent description."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        """List of agent capabilities."""
        pass

    @property
    def status(self) -> AgentStatus:
        """Current agent status."""
        return self._status

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    async def start(self):
        """Start the agent."""
        logger.info(f"Starting agent {self.agent_id}")

        try:
            await self.on_start()
            self._status = AgentStatus.READY
            logger.info(f"Agent {self.agent_id} ready")
        except Exception as e:
            self._status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_id} failed to start: {e}")
            raise

    async def stop(self):
        """Stop the agent gracefully."""
        logger.info(f"Stopping agent {self.agent_id}")
        self._status = AgentStatus.STOPPED
        await self.on_stop()

    async def on_start(self):
        """Override for custom startup logic."""
        pass

    async def on_stop(self):
        """Override for custom shutdown logic."""
        pass

    # =========================================================================
    # Task Execution
    # =========================================================================

    @abstractmethod
    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """
        Execute a task.

        Args:
            task_type: Type of task to execute
            input_data: Task input data
            context: Additional context (conversation, state, etc.)

        Returns:
            AgentResult with output and confidence
        """
        pass

    async def run_task(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        create_checkpoint: bool = True,
    ) -> AgentResult:
        """
        Run a task with full lifecycle management.

        Creates task record, checkpoint, executes, and updates state.
        """
        # Create task record
        task = self.store.create_task(
            task_type=task_type,
            input_data=input_data,
            agent_id=self.agent_id,
        )
        self._current_task_id = task.id

        # Log start
        self.store.log_agent_action(
            agent_id=self.agent_id,
            action="task_started",
            details={"task_type": task_type, "input": input_data},
            task_id=task.id,
        )

        # Create checkpoint before execution
        if create_checkpoint:
            self.store.create_checkpoint(
                task_id=task.id,
                checkpoint_type=CheckpointType.PRE_CHANGE,
                state_snapshot={"input": input_data},
                file_hashes={},  # Would be populated by integrity module
                description=f"Before {task_type} execution",
            )

        # Update status
        self._status = AgentStatus.BUSY
        self.store.update_task_status(task.id, TaskStatus.RUNNING)

        try:
            # Execute
            result = await self.execute(task_type, input_data, context)

            # Update task with result
            self.store.update_task_status(
                task.id,
                TaskStatus.COMPLETED if result.success else TaskStatus.FAILED,
                output_data=result.to_dict(),
                error=None if result.success else result.reasoning,
            )

            # Log completion
            self.store.log_agent_action(
                agent_id=self.agent_id,
                action="task_completed",
                details={
                    "success": result.success,
                    "confidence": result.confidence.name,
                },
                task_id=task.id,
            )

            return result

        except Exception as e:
            # Log error
            self.store.log_agent_action(
                agent_id=self.agent_id,
                action="task_error",
                details={"error": str(e)},
                task_id=task.id,
                level="error",
            )

            # Update task status
            self.store.update_task_status(
                task.id,
                TaskStatus.FAILED,
                error=str(e),
            )

            raise

        finally:
            self._status = AgentStatus.READY
            self._current_task_id = None

    # =========================================================================
    # LLM Interaction
    # =========================================================================

    async def ask_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Send prompt to LLM and get response.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Max response tokens

        Returns:
            LLM response content
        """
        messages = []

        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))

        messages.append(LLMMessage(role="user", content=prompt))

        response = self.llm.generate(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.content

    async def ask_llm_with_consensus(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        min_agreement: float = 0.67,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Query LLM with consensus verification.

        Returns dict with response and consensus info.
        """
        messages = []

        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))

        messages.append(LLMMessage(role="user", content=prompt))

        return self.llm.generate_with_consensus(
            messages,
            min_agreement=min_agreement,
            **kwargs
        )

    # =========================================================================
    # Message Handling
    # =========================================================================

    def _register_handlers(self):
        """Register default message handlers."""
        self._handlers["ping"] = self._handle_ping
        self._handlers["status"] = self._handle_status
        self._handlers["task"] = self._handle_task

    async def _handle_ping(self, message: Message) -> Message:
        """Handle ping request."""
        return Message(
            type="pong",
            source=self.agent_id,
            target=message.source,
            payload={"agent": self.name, "status": self.status.value},
        )

    async def _handle_status(self, message: Message) -> Message:
        """Handle status request."""
        return Message(
            type="status_response",
            source=self.agent_id,
            target=message.source,
            payload={
                "agent_id": self.agent_id,
                "name": self.name,
                "status": self.status.value,
                "current_task": self._current_task_id,
                "capabilities": [c.name for c in self.capabilities],
            },
        )

    async def _handle_task(self, message: Message) -> Message:
        """Handle task request."""
        task_type = message.payload.get("task_type")
        input_data = message.payload.get("input_data", {})
        context = message.payload.get("context", {})

        try:
            result = await self.run_task(task_type, input_data, context)
            return Message(
                type="task_result",
                source=self.agent_id,
                target=message.source,
                payload=result.to_dict(),
            )
        except Exception as e:
            return Message(
                type="task_error",
                source=self.agent_id,
                target=message.source,
                payload={"error": str(e)},
                priority=MessagePriority.HIGH,
            )

    async def handle_message(self, message: Message) -> Optional[Message]:
        """
        Handle incoming message.

        Override for custom message handling.
        """
        handler = self._handlers.get(message.type)
        if handler:
            return await handler(message)

        logger.warning(f"No handler for message type: {message.type}")
        return None

    def send_message(
        self,
        target: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ):
        """Send message to another agent."""
        if not self.bus:
            logger.warning("No message bus configured")
            return

        message = Message(
            type=message_type,
            source=self.agent_id,
            target=target,
            payload=payload,
            priority=priority,
        )

        self.bus.publish("agents", message)

    # =========================================================================
    # Confidence & Verification
    # =========================================================================

    def assess_confidence(
        self,
        evidence: List[str],
        contradictions: List[str],
        verification_count: int = 0,
    ) -> ConfidenceLevel:
        """
        Assess confidence level based on evidence.

        Args:
            evidence: Supporting evidence
            contradictions: Contradicting evidence
            verification_count: Number of independent verifications

        Returns:
            Confidence level
        """
        if not evidence:
            return ConfidenceLevel.UNKNOWN

        if contradictions:
            if len(contradictions) >= len(evidence):
                return ConfidenceLevel.UNKNOWN
            return ConfidenceLevel.UNCERTAIN

        if verification_count >= 2:
            return ConfidenceLevel.HIGH

        if len(evidence) >= 3:
            return ConfidenceLevel.MODERATE

        return ConfidenceLevel.UNCERTAIN

    def require_verification(
        self,
        result: AgentResult,
        min_confidence: ConfidenceLevel = ConfidenceLevel.MODERATE,
    ) -> bool:
        """Check if result requires additional verification."""
        return result.confidence.value < min_confidence.value

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def log(self, action: str, details: Dict[str, Any], level: str = "info"):
        """Log agent action."""
        self.store.log_agent_action(
            agent_id=self.agent_id,
            action=action,
            details=details,
            task_id=self._current_task_id,
            level=level,
        )

    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a metric."""
        full_tags = {"agent": self.name, "agent_id": self.agent_id}
        if tags:
            full_tags.update(tags)
        self.store.record_metric(name, value, full_tags)


class AgentRegistry:
    """
    Registry for agent types.

    Enables dynamic agent discovery and instantiation.
    """

    _agents: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, agent_class: Type[BaseAgent]):
        """Register an agent class."""
        # Create temporary instance to get name
        temp = object.__new__(agent_class)
        name = agent_class.name.fget(temp)
        cls._agents[name] = agent_class
        logger.info(f"Registered agent type: {name}")

    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseAgent]]:
        """Get agent class by name."""
        return cls._agents.get(name)

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent types."""
        return list(cls._agents.keys())

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs
    ) -> BaseAgent:
        """Create agent instance by name."""
        agent_class = cls.get(name)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {name}")
        return agent_class(**kwargs)


def agent(cls: Type[BaseAgent]) -> Type[BaseAgent]:
    """Decorator to register an agent class."""
    AgentRegistry.register(cls)
    return cls
