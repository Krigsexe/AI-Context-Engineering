# =============================================================================
# ODIN v7.0 - Unit Tests: Base Agent
# =============================================================================

import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

from agents.shared.base_agent import (
    BaseAgent,
    AgentRegistry,
    AgentStatus,
    AgentCapability,
    AgentResult,
    ConfidenceLevel,
    agent,
)
from agents.shared.state_store import InMemoryStateStore


class TestAgentResult:
    """Test AgentResult dataclass."""

    def test_result_creation(self):
        """Test basic result creation."""
        result = AgentResult(
            success=True,
            data={"output": "test"},
            confidence=ConfidenceLevel.HIGH,
            reasoning="Test completed successfully",
        )

        assert result.success is True
        assert result.data == {"output": "test"}
        assert result.confidence == ConfidenceLevel.HIGH
        assert result.reasoning == "Test completed successfully"

    def test_result_with_warnings(self):
        """Test result with warnings."""
        result = AgentResult(
            success=True,
            data={},
            confidence=ConfidenceLevel.MODERATE,
            reasoning="Done",
            warnings=["Warning 1", "Warning 2"],
        )

        assert len(result.warnings) == 2

    def test_result_to_dict(self):
        """Test result serialization."""
        result = AgentResult(
            success=True,
            data={"key": "value"},
            confidence=ConfidenceLevel.HIGH,
            reasoning="Test",
            citations=["source1"],
        )

        data = result.to_dict()

        assert data["success"] is True
        assert data["data"] == {"key": "value"}
        assert data["confidence"] == 3  # HIGH.value
        assert data["confidence_name"] == "HIGH"
        assert "source1" in data["citations"]


class TestAgentCapability:
    """Test AgentCapability dataclass."""

    def test_capability_creation(self):
        """Test capability creation."""
        cap = AgentCapability(
            name="generate_code",
            description="Generate code from requirements",
            input_schema={"requirements": "string"},
            output_schema={"code": "string"},
        )

        assert cap.name == "generate_code"
        assert cap.requires_approval is False
        assert cap.risk_level == "low"

    def test_capability_high_risk(self):
        """Test high-risk capability."""
        cap = AgentCapability(
            name="delete_files",
            description="Delete files",
            input_schema={"paths": "list"},
            output_schema={"deleted": "int"},
            requires_approval=True,
            risk_level="high",
        )

        assert cap.requires_approval is True
        assert cap.risk_level == "high"


class TestConfidenceLevel:
    """Test ConfidenceLevel enum."""

    def test_confidence_values(self):
        """Test confidence level values."""
        assert ConfidenceLevel.UNKNOWN.value == 0
        assert ConfidenceLevel.UNCERTAIN.value == 1
        assert ConfidenceLevel.MODERATE.value == 2
        assert ConfidenceLevel.HIGH.value == 3
        assert ConfidenceLevel.AXIOM.value == 4

    def test_confidence_ordering(self):
        """Test confidence levels can be compared."""
        assert ConfidenceLevel.UNKNOWN.value < ConfidenceLevel.UNCERTAIN.value
        assert ConfidenceLevel.AXIOM.value > ConfidenceLevel.HIGH.value


class ConcreteAgent(BaseAgent):
    """Concrete agent implementation for testing."""

    @property
    def name(self) -> str:
        return "test_agent"

    @property
    def description(self) -> str:
        return "A test agent for unit tests"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="test_task",
                description="A test task",
                input_schema={"input": "string"},
                output_schema={"output": "string"},
            )
        ]

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        if task_type == "test_task":
            return AgentResult(
                success=True,
                data={"output": f"Processed: {input_data.get('input', '')}"},
                confidence=ConfidenceLevel.HIGH,
                reasoning="Test task completed",
            )
        elif task_type == "failing_task":
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="Task failed intentionally",
            )
        else:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Unknown task: {task_type}",
            )


class TestBaseAgent:
    """Test BaseAgent base class."""

    @pytest.fixture
    def agent(self):
        """Create test agent."""
        store = InMemoryStateStore()
        return ConcreteAgent(state_store=store)

    def test_agent_creation(self, agent):
        """Test agent creation."""
        assert agent.name == "test_agent"
        assert agent.description == "A test agent for unit tests"
        assert len(agent.capabilities) == 1

    def test_agent_id_generated(self, agent):
        """Test agent ID is generated."""
        assert agent.agent_id is not None
        assert agent.agent_id.startswith("test_agent-")

    def test_agent_custom_id(self):
        """Test custom agent ID."""
        agent = ConcreteAgent(agent_id="custom-id-123")
        assert agent.agent_id == "custom-id-123"

    def test_agent_initial_status(self, agent):
        """Test initial agent status."""
        assert agent.status == AgentStatus.INITIALIZING

    @pytest.mark.asyncio
    async def test_agent_start(self, agent):
        """Test agent start."""
        await agent.start()
        assert agent.status == AgentStatus.READY

    @pytest.mark.asyncio
    async def test_agent_stop(self, agent):
        """Test agent stop."""
        await agent.start()
        await agent.stop()
        assert agent.status == AgentStatus.STOPPED

    @pytest.mark.asyncio
    async def test_execute_success(self, agent):
        """Test successful task execution."""
        await agent.start()

        result = await agent.execute(
            "test_task",
            {"input": "test data"},
        )

        assert result.success is True
        assert result.confidence == ConfidenceLevel.HIGH
        assert "Processed: test data" in result.data["output"]

    @pytest.mark.asyncio
    async def test_execute_failure(self, agent):
        """Test failed task execution."""
        await agent.start()

        result = await agent.execute(
            "failing_task",
            {},
        )

        assert result.success is False

    @pytest.mark.asyncio
    async def test_run_task_creates_record(self, agent):
        """Test that run_task creates task record."""
        await agent.start()

        result = await agent.run_task(
            "test_task",
            {"input": "test"},
        )

        # Check task was created in store
        tasks = agent.store.list_tasks()
        assert len(tasks) >= 1

    @pytest.mark.asyncio
    async def test_run_task_creates_checkpoint(self, agent):
        """Test that run_task creates checkpoint."""
        await agent.start()

        result = await agent.run_task(
            "test_task",
            {"input": "test"},
            create_checkpoint=True,
        )

        # Check checkpoint was created
        checkpoints = agent.store.list_checkpoints()
        assert len(checkpoints) >= 1


class TestAgentRegistry:
    """Test AgentRegistry."""

    def test_register_agent(self):
        """Test agent registration."""
        # ConcreteAgent should be registered via import
        agents = AgentRegistry.list_agents()
        # Note: Actual agents registered at import time
        assert isinstance(agents, list)

    def test_get_unknown_agent(self):
        """Test getting unknown agent returns None."""
        result = AgentRegistry.get("nonexistent_agent_xyz")
        assert result is None


class TestAgentDecorator:
    """Test @agent decorator."""

    def test_decorator_registers_agent(self):
        """Test that decorator registers agent."""
        @agent
        class DecoratedAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "decorated_test"

            @property
            def description(self) -> str:
                return "Decorated test agent"

            @property
            def capabilities(self) -> List[AgentCapability]:
                return []

            async def execute(self, task_type, input_data, context=None):
                return AgentResult(
                    success=True,
                    data={},
                    confidence=ConfidenceLevel.HIGH,
                    reasoning="Done",
                )

        # Agent should be registered
        retrieved = AgentRegistry.get("decorated_test")
        assert retrieved is not None
