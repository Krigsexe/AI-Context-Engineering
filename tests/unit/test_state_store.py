# =============================================================================
# ODIN v7.0 - Unit Tests: State Store
# =============================================================================

import pytest
from datetime import datetime

from agents.shared.state_store import (
    InMemoryStateStore,
    Task,
    TaskStatus,
    Checkpoint,
    CheckpointType,
)


class TestInMemoryStateStore:
    """Test InMemoryStateStore implementation."""

    @pytest.fixture
    def store(self):
        """Create fresh store for each test."""
        return InMemoryStateStore()

    # =========================================================================
    # Task Tests
    # =========================================================================

    def test_create_task(self, store):
        """Test task creation."""
        task = store.create_task(
            task_type="code_write",
            input_data={"requirements": "Create a function"},
            agent_id="dev-1",
        )

        assert task.id is not None
        assert task.type == "code_write"
        assert task.status == TaskStatus.PENDING
        assert task.input_data == {"requirements": "Create a function"}
        assert task.agent_id == "dev-1"

    def test_get_task(self, store):
        """Test task retrieval."""
        created = store.create_task(
            task_type="test",
            input_data={"data": "value"},
        )

        retrieved = store.get_task(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.type == "test"

    def test_get_task_not_found(self, store):
        """Test retrieval of non-existent task."""
        result = store.get_task("non-existent-id")
        assert result is None

    def test_update_task_status(self, store):
        """Test task status update."""
        task = store.create_task(
            task_type="test",
            input_data={},
        )

        store.update_task_status(
            task.id,
            TaskStatus.RUNNING,
        )

        updated = store.get_task(task.id)
        assert updated.status == TaskStatus.RUNNING

    def test_update_task_with_output(self, store):
        """Test task update with output data."""
        task = store.create_task(
            task_type="test",
            input_data={},
        )

        store.update_task_status(
            task.id,
            TaskStatus.COMPLETED,
            output_data={"result": "success"},
        )

        updated = store.get_task(task.id)
        assert updated.status == TaskStatus.COMPLETED
        assert updated.output_data == {"result": "success"}
        assert updated.completed_at is not None

    def test_update_task_with_error(self, store):
        """Test task update with error."""
        task = store.create_task(
            task_type="test",
            input_data={},
        )

        store.update_task_status(
            task.id,
            TaskStatus.FAILED,
            error="Something went wrong",
        )

        updated = store.get_task(task.id)
        assert updated.status == TaskStatus.FAILED
        assert updated.error == "Something went wrong"

    def test_list_tasks(self, store):
        """Test listing tasks."""
        store.create_task(task_type="type1", input_data={})
        store.create_task(task_type="type2", input_data={})
        store.create_task(task_type="type1", input_data={})

        all_tasks = store.list_tasks()
        assert len(all_tasks) == 3

    def test_list_tasks_filter_by_status(self, store):
        """Test filtering tasks by status."""
        task1 = store.create_task(task_type="test", input_data={})
        task2 = store.create_task(task_type="test", input_data={})

        store.update_task_status(task1.id, TaskStatus.COMPLETED)

        pending = store.list_tasks(status=TaskStatus.PENDING)
        completed = store.list_tasks(status=TaskStatus.COMPLETED)

        assert len(pending) == 1
        assert len(completed) == 1

    def test_list_tasks_filter_by_type(self, store):
        """Test filtering tasks by type."""
        store.create_task(task_type="code_write", input_data={})
        store.create_task(task_type="code_review", input_data={})
        store.create_task(task_type="code_write", input_data={})

        code_write_tasks = store.list_tasks(task_type="code_write")
        assert len(code_write_tasks) == 2

    # =========================================================================
    # Checkpoint Tests
    # =========================================================================

    def test_create_checkpoint(self, store):
        """Test checkpoint creation."""
        task = store.create_task(task_type="test", input_data={})

        checkpoint = store.create_checkpoint(
            task_id=task.id,
            checkpoint_type=CheckpointType.PRE_CHANGE,
            state_snapshot={"state": "value"},
            file_hashes={"file.py": "hash123"},
            description="Before modification",
        )

        assert checkpoint.id is not None
        assert checkpoint.task_id == task.id
        assert checkpoint.type == CheckpointType.PRE_CHANGE
        assert checkpoint.state_snapshot == {"state": "value"}
        assert checkpoint.file_hashes == {"file.py": "hash123"}

    def test_get_checkpoint(self, store):
        """Test checkpoint retrieval."""
        task = store.create_task(task_type="test", input_data={})
        created = store.create_checkpoint(
            task_id=task.id,
            checkpoint_type=CheckpointType.MANUAL,
            state_snapshot={},
            file_hashes={},
            description="Test checkpoint",
        )

        retrieved = store.get_checkpoint(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_list_checkpoints(self, store):
        """Test listing checkpoints."""
        task = store.create_task(task_type="test", input_data={})

        store.create_checkpoint(
            task_id=task.id,
            checkpoint_type=CheckpointType.AUTO,
            state_snapshot={},
            file_hashes={},
            description="Checkpoint 1",
        )
        store.create_checkpoint(
            task_id=task.id,
            checkpoint_type=CheckpointType.AUTO,
            state_snapshot={},
            file_hashes={},
            description="Checkpoint 2",
        )

        checkpoints = store.list_checkpoints(task_id=task.id)
        assert len(checkpoints) == 2

    def test_get_latest_checkpoint(self, store):
        """Test getting latest checkpoint."""
        task = store.create_task(task_type="test", input_data={})

        store.create_checkpoint(
            task_id=task.id,
            checkpoint_type=CheckpointType.AUTO,
            state_snapshot={},
            file_hashes={},
            description="First",
        )
        second = store.create_checkpoint(
            task_id=task.id,
            checkpoint_type=CheckpointType.AUTO,
            state_snapshot={},
            file_hashes={},
            description="Second",
        )

        latest = store.get_latest_checkpoint(task.id)
        assert latest is not None
        assert latest.id == second.id

    # =========================================================================
    # Logging Tests
    # =========================================================================

    def test_log_agent_action(self, store):
        """Test logging agent action."""
        task = store.create_task(task_type="test", input_data={})

        store.log_agent_action(
            agent_id="dev-1",
            action="code_generated",
            details={"lines": 50},
            task_id=task.id,
        )

        logs = store.get_agent_logs(agent_id="dev-1")
        assert len(logs) == 1
        assert logs[0].action == "code_generated"

    def test_get_agent_logs_filter_by_task(self, store):
        """Test filtering logs by task."""
        task1 = store.create_task(task_type="test", input_data={})
        task2 = store.create_task(task_type="test", input_data={})

        store.log_agent_action(
            agent_id="dev-1",
            action="action1",
            details={},
            task_id=task1.id,
        )
        store.log_agent_action(
            agent_id="dev-1",
            action="action2",
            details={},
            task_id=task2.id,
        )

        logs = store.get_agent_logs(task_id=task1.id)
        assert len(logs) == 1
        assert logs[0].action == "action1"

    # =========================================================================
    # Metrics Tests
    # =========================================================================

    def test_record_metric(self, store):
        """Test recording metrics."""
        store.record_metric(
            name="task_duration",
            value=1.5,
            tags={"agent": "dev"},
        )

        metrics = store.get_metrics("task_duration")
        assert len(metrics) == 1
        assert metrics[0]["value"] == 1.5

    def test_get_metrics_by_name(self, store):
        """Test getting metrics by name."""
        store.record_metric("metric1", 1.0)
        store.record_metric("metric2", 2.0)
        store.record_metric("metric1", 1.5)

        metrics = store.get_metrics("metric1")
        assert len(metrics) == 2
