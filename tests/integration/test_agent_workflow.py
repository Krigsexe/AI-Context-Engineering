# =============================================================================
# ODIN v7.0 - Integration Tests: Agent Workflows
# =============================================================================
# Tests for end-to-end agent workflows with mocked LLM responses
# =============================================================================

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from agents.shared.base_agent import (
    AgentResult,
    AgentCapability,
    ConfidenceLevel,
    AgentRegistry,
)
from agents.shared.state_store import (
    InMemoryStateStore,
    TaskStatus,
    CheckpointType,
)
from agents.shared.providers import Message, LLMResponse


class TestAgentLifecycle:
    """Test agent lifecycle management."""

    @pytest.fixture
    def state_store(self):
        """Create in-memory state store."""
        return InMemoryStateStore()

    @pytest.fixture
    def mock_llm_response(self):
        """Create mock LLM response."""
        return LLMResponse(
            content='{"analysis": "test", "confidence": 0.95}',
            model="test-model",
            provider="mock",
            tokens_used=100,
            latency_ms=50.0,
        )

    def test_agent_registry_discovery(self):
        """Test that agents are discoverable via registry."""
        # Import agents to trigger registration
        from agents.cognitive import IntakeAgent, DevAgent

        agents = AgentRegistry.list_agents()
        assert len(agents) > 0

    def test_state_store_task_workflow(self, state_store):
        """Test complete task workflow through state store."""
        # Create task
        task = state_store.create_task(
            task_type="code_review",
            input_data={"code": "def hello(): pass"},
            agent_id="test-agent",
        )
        assert task.status == TaskStatus.PENDING

        # Update to running
        state_store.update_task_status(task.id, TaskStatus.RUNNING)
        updated = state_store.get_task(task.id)
        assert updated.status == TaskStatus.RUNNING

        # Complete with output
        state_store.update_task_status(
            task.id,
            TaskStatus.COMPLETED,
            output_data={"result": "approved"},
        )
        completed = state_store.get_task(task.id)
        assert completed.status == TaskStatus.COMPLETED
        assert completed.output_data["result"] == "approved"

    def test_checkpoint_workflow(self, state_store):
        """Test checkpoint creation and retrieval."""
        # Create checkpoint
        checkpoint = state_store.create_checkpoint(
            task_id="task-123",
            checkpoint_type=CheckpointType.MANUAL,
            state_snapshot={"progress": 50, "files_processed": 10},
            file_hashes={"main.py": "abc123"},
            description="Mid-point checkpoint",
        )
        assert checkpoint.task_id == "task-123"

        # Retrieve checkpoint
        retrieved = state_store.get_checkpoint(checkpoint.id)
        assert retrieved.state_snapshot["progress"] == 50

        # List checkpoints
        checkpoints = state_store.list_checkpoints(task_id="task-123")
        assert len(checkpoints) >= 1

    def test_agent_logging(self, state_store):
        """Test agent action logging."""
        # Log actions
        state_store.log_agent_action(
            agent_id="agent-1",
            action="start_analysis",
            details={"file": "test.py"},
            task_id="task-1",
        )
        state_store.log_agent_action(
            agent_id="agent-1",
            action="complete_analysis",
            details={"result": "success"},
            task_id="task-1",
        )

        # Retrieve logs
        logs = state_store.get_agent_logs(agent_id="agent-1")
        assert len(logs) >= 2

        # Filter by task
        task_logs = state_store.get_agent_logs(task_id="task-1")
        assert len(task_logs) >= 2

    def test_metrics_recording(self, state_store):
        """Test metrics recording and retrieval."""
        # Record metrics
        state_store.record_metric(
            name="llm_latency",
            value=150.5,
            tags={"provider": "ollama", "model": "qwen"},
        )
        state_store.record_metric(
            name="llm_latency",
            value=200.3,
            tags={"provider": "ollama", "model": "qwen"},
        )
        state_store.record_metric(
            name="token_count",
            value=500,
            tags={"agent": "dev"},
        )

        # Get metrics by name
        latency_metrics = state_store.get_metrics(name="llm_latency")
        assert len(latency_metrics) >= 2


class TestIntegrityWorkflow:
    """Test semantic integrity workflow."""

    def test_project_hash_workflow(self, tmp_path):
        """Test project hashing workflow."""
        from agents.shared.integrity import (
            project_sih,
            compare_sih,
            IntegrityMonitor,
        )

        # Create test project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main(): pass\n")
        (tmp_path / "src" / "utils.py").write_text("def util(): pass\n")

        # Compute initial hash
        initial_hashes = project_sih(tmp_path)
        assert len(initial_hashes) >= 2

        # Modify a file
        (tmp_path / "src" / "main.py").write_text("def main(): return 42\n")

        # Compute new hash and compare
        new_hashes = project_sih(tmp_path)
        changes = compare_sih(initial_hashes, new_hashes)

        assert "src/main.py" in changes["modified"]
        assert len(changes["added"]) == 0
        assert len(changes["removed"]) == 0

    def test_integrity_monitor(self, tmp_path):
        """Test IntegrityMonitor for drift detection."""
        from agents.shared.integrity import IntegrityMonitor

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1\n")

        # Initialize monitor
        monitor = IntegrityMonitor(tmp_path)
        monitor.capture_baseline()

        # Check no drift initially (returns dict with added/removed/modified)
        drift = monitor.check_drift()
        assert len(drift["modified"]) == 0
        assert len(drift["added"]) == 0
        assert len(drift["removed"]) == 0

        # Modify file
        test_file.write_text("x = 2\n")

        # Check drift detected
        drift = monitor.check_drift()
        assert len(drift["modified"]) > 0


class TestProviderIntegration:
    """Test LLM provider integration (mocked)."""

    def test_provider_registry(self):
        """Test provider registry functionality."""
        from agents.shared.providers import list_providers, get_provider

        providers = list_providers()
        assert "ollama" in providers
        assert "anthropic" in providers
        assert "openai" in providers

    def test_ollama_provider_initialization(self):
        """Test Ollama provider can be initialized."""
        from agents.shared.providers import OllamaProvider

        provider = OllamaProvider(
            base_url="http://localhost:11434",
            model="qwen2.5:7b",
        )
        assert provider.name == "ollama"
        assert provider.model == "qwen2.5:7b"

    @patch("requests.get")
    def test_ollama_availability_check(self, mock_get):
        """Test Ollama availability check."""
        from agents.shared.providers import OllamaProvider

        # Mock successful response
        mock_get.return_value = Mock(status_code=200)

        provider = OllamaProvider()
        assert provider.is_available() is True

        # Mock failed response
        mock_get.side_effect = Exception("Connection refused")
        assert provider.is_available() is False

    def test_llm_client_initialization(self):
        """Test LLM client initialization."""
        from agents.shared.llm_client import LLMClient

        client = LLMClient(
            primary_provider="ollama",
            primary_model="qwen2.5:7b",
            fallback_providers=[{"provider": "anthropic", "model": "claude-3-haiku"}],
        )
        assert client.primary_provider == "ollama"
        assert client.primary_model == "qwen2.5:7b"
        assert len(client.fallback_configs) == 1


class TestAgentCapabilities:
    """Test agent capability definitions."""

    def test_capability_creation(self):
        """Test AgentCapability dataclass."""
        cap = AgentCapability(
            name="code_review",
            description="Review code for quality",
            input_schema={"code": "string", "language": "string"},
            output_schema={"issues": "list", "score": "number"},
            requires_approval=True,
            risk_level="medium",
        )
        assert cap.name == "code_review"
        assert cap.requires_approval is True
        assert cap.risk_level == "medium"

    def test_confidence_levels(self):
        """Test confidence level ordering."""
        assert ConfidenceLevel.AXIOM.value > ConfidenceLevel.HIGH.value
        assert ConfidenceLevel.HIGH.value > ConfidenceLevel.MODERATE.value
        assert ConfidenceLevel.MODERATE.value > ConfidenceLevel.UNCERTAIN.value
        assert ConfidenceLevel.UNCERTAIN.value > ConfidenceLevel.UNKNOWN.value

    def test_agent_result_creation(self):
        """Test AgentResult dataclass."""
        result = AgentResult(
            success=True,
            data={"analysis": "complete"},
            confidence=ConfidenceLevel.HIGH,
            reasoning="Based on code analysis",
            warnings=["Consider adding tests"],
        )
        assert result.success is True
        assert result.confidence == ConfidenceLevel.HIGH
        assert len(result.warnings) == 1

        # Test dict conversion
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["confidence_name"] == "HIGH"
        assert result_dict["confidence"] == ConfidenceLevel.HIGH.value
