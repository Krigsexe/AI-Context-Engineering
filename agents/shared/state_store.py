# =============================================================================
# ODIN v7.0 - State Store (PostgreSQL)
# =============================================================================
# Persistent state management for agents and tasks
# Supports checkpoints, rollback, and audit trails
# =============================================================================

from __future__ import annotations
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class CheckpointType(Enum):
    """Checkpoint types."""
    AUTO = "auto"           # Automatic checkpoint
    MANUAL = "manual"       # User-requested
    PRE_CHANGE = "pre_change"  # Before risky operation
    MILESTONE = "milestone"    # Task milestone


@dataclass
class Task:
    """
    Task record in state store.
    """
    id: str
    type: str
    status: TaskStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "agent_id": self.agent_id,
            "parent_task_id": self.parent_task_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


@dataclass
class Checkpoint:
    """
    Checkpoint for state rollback.
    """
    id: str
    task_id: str
    type: CheckpointType
    state_snapshot: Dict[str, Any]
    file_hashes: Dict[str, str]
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentLog:
    """
    Agent activity log entry.
    """
    id: str
    agent_id: str
    task_id: Optional[str]
    action: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    level: str = "info"


class StateStore:
    """
    PostgreSQL-backed state store for ODIN.

    Provides:
    - Task management
    - Checkpoint/rollback
    - Agent logging
    - Metrics collection
    """

    def __init__(
        self,
        database_url: str = "postgresql://odin:odin@localhost:5432/odin",
    ):
        """
        Initialize state store.

        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self._conn = None
        self._pool = None

    @property
    def connection(self):
        """Lazy database connection."""
        if self._conn is None:
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                self._conn = psycopg2.connect(
                    self.database_url,
                    cursor_factory=RealDictCursor
                )
            except ImportError:
                raise RuntimeError("psycopg2 required: pip install psycopg2-binary")
        return self._conn

    @contextmanager
    def cursor(self):
        """Get database cursor with automatic commit/rollback."""
        cur = self.connection.cursor()
        try:
            yield cur
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cur.close()

    # =========================================================================
    # Task Management
    # =========================================================================

    def create_task(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        agent_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            task_type: Type of task
            input_data: Task input
            agent_id: Assigned agent
            parent_task_id: Parent task for subtasks
            metadata: Additional metadata

        Returns:
            Created Task object
        """
        task = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            status=TaskStatus.PENDING,
            input_data=input_data,
            agent_id=agent_id,
            parent_task_id=parent_task_id,
            metadata=metadata or {},
        )

        with self.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks
                    (id, type, status, input_data, agent_id, parent_task_id, metadata)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    task.id,
                    task.type,
                    task.status.value,
                    json.dumps(task.input_data),
                    task.agent_id,
                    task.parent_task_id,
                    json.dumps(task.metadata),
                )
            )

        logger.info(f"Created task {task.id} of type {task.type}")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        with self.cursor() as cur:
            cur.execute(
                "SELECT * FROM tasks WHERE id = %s",
                (task_id,)
            )
            row = cur.fetchone()

        if not row:
            return None

        return Task(
            id=row["id"],
            type=row["type"],
            status=TaskStatus(row["status"]),
            input_data=row["input_data"],
            output_data=row["output_data"],
            error=row["error"],
            agent_id=row["agent_id"],
            parent_task_id=row["parent_task_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            completed_at=row["completed_at"],
            metadata=row["metadata"] or {},
        )

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        """Update task status."""
        with self.cursor() as cur:
            updates = ["status = %s", "updated_at = NOW()"]
            params = [status.value]

            if output_data is not None:
                updates.append("output_data = %s")
                params.append(json.dumps(output_data))

            if error is not None:
                updates.append("error = %s")
                params.append(error)

            if status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                updates.append("completed_at = NOW()")

            params.append(task_id)

            cur.execute(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s",
                params
            )

        logger.info(f"Updated task {task_id} to status {status.value}")

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Task]:
        """List tasks with optional filters."""
        conditions = []
        params = []

        if status:
            conditions.append("status = %s")
            params.append(status.value)
        if task_type:
            conditions.append("type = %s")
            params.append(task_type)
        if agent_id:
            conditions.append("agent_id = %s")
            params.append(agent_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        with self.cursor() as cur:
            cur.execute(
                f"""
                SELECT * FROM tasks
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s
                """,
                params
            )
            rows = cur.fetchall()

        return [
            Task(
                id=row["id"],
                type=row["type"],
                status=TaskStatus(row["status"]),
                input_data=row["input_data"],
                output_data=row["output_data"],
                error=row["error"],
                agent_id=row["agent_id"],
                parent_task_id=row["parent_task_id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                completed_at=row["completed_at"],
                metadata=row["metadata"] or {},
            )
            for row in rows
        ]

    # =========================================================================
    # Checkpoint Management
    # =========================================================================

    def create_checkpoint(
        self,
        task_id: str,
        checkpoint_type: CheckpointType,
        state_snapshot: Dict[str, Any],
        file_hashes: Dict[str, str],
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Checkpoint:
        """
        Create a checkpoint for rollback.

        Args:
            task_id: Associated task
            checkpoint_type: Type of checkpoint
            state_snapshot: Current state to preserve
            file_hashes: SIH of project files
            description: Human-readable description
            metadata: Additional metadata

        Returns:
            Created Checkpoint
        """
        checkpoint = Checkpoint(
            id=str(uuid.uuid4()),
            task_id=task_id,
            type=checkpoint_type,
            state_snapshot=state_snapshot,
            file_hashes=file_hashes,
            description=description,
            metadata=metadata or {},
        )

        with self.cursor() as cur:
            cur.execute(
                """
                INSERT INTO checkpoints
                    (id, task_id, type, state_snapshot, file_hashes, description, metadata)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    checkpoint.id,
                    checkpoint.task_id,
                    checkpoint.type.value,
                    json.dumps(checkpoint.state_snapshot),
                    json.dumps(checkpoint.file_hashes),
                    checkpoint.description,
                    json.dumps(checkpoint.metadata),
                )
            )

        logger.info(f"Created checkpoint {checkpoint.id} for task {task_id}")
        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Get checkpoint by ID."""
        with self.cursor() as cur:
            cur.execute(
                "SELECT * FROM checkpoints WHERE id = %s",
                (checkpoint_id,)
            )
            row = cur.fetchone()

        if not row:
            return None

        return Checkpoint(
            id=row["id"],
            task_id=row["task_id"],
            type=CheckpointType(row["type"]),
            state_snapshot=row["state_snapshot"],
            file_hashes=row["file_hashes"],
            description=row["description"],
            created_at=row["created_at"],
            metadata=row["metadata"] or {},
        )

    def list_checkpoints(
        self,
        task_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Checkpoint]:
        """List checkpoints, optionally filtered by task."""
        with self.cursor() as cur:
            if task_id:
                cur.execute(
                    """
                    SELECT * FROM checkpoints
                    WHERE task_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (task_id, limit)
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM checkpoints
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
            rows = cur.fetchall()

        return [
            Checkpoint(
                id=row["id"],
                task_id=row["task_id"],
                type=CheckpointType(row["type"]),
                state_snapshot=row["state_snapshot"],
                file_hashes=row["file_hashes"],
                description=row["description"],
                created_at=row["created_at"],
                metadata=row["metadata"] or {},
            )
            for row in rows
        ]

    def get_latest_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        """Get most recent checkpoint for a task."""
        checkpoints = self.list_checkpoints(task_id=task_id, limit=1)
        return checkpoints[0] if checkpoints else None

    # =========================================================================
    # Agent Logging
    # =========================================================================

    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        details: Dict[str, Any],
        task_id: Optional[str] = None,
        level: str = "info",
    ):
        """
        Log agent action for audit trail.

        Args:
            agent_id: Agent identifier
            action: Action description
            details: Action details
            task_id: Associated task
            level: Log level (info, warning, error)
        """
        log_id = str(uuid.uuid4())

        with self.cursor() as cur:
            cur.execute(
                """
                INSERT INTO agent_logs
                    (id, agent_id, task_id, action, details, level)
                VALUES
                    (%s, %s, %s, %s, %s, %s)
                """,
                (
                    log_id,
                    agent_id,
                    task_id,
                    action,
                    json.dumps(details),
                    level,
                )
            )

        logger.debug(f"Logged action for agent {agent_id}: {action}")

    def get_agent_logs(
        self,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100,
    ) -> List[AgentLog]:
        """Get agent logs with optional filters."""
        conditions = []
        params = []

        if agent_id:
            conditions.append("agent_id = %s")
            params.append(agent_id)
        if task_id:
            conditions.append("task_id = %s")
            params.append(task_id)
        if level:
            conditions.append("level = %s")
            params.append(level)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        with self.cursor() as cur:
            cur.execute(
                f"""
                SELECT * FROM agent_logs
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                params
            )
            rows = cur.fetchall()

        return [
            AgentLog(
                id=row["id"],
                agent_id=row["agent_id"],
                task_id=row["task_id"],
                action=row["action"],
                details=row["details"],
                timestamp=row["timestamp"],
                level=row["level"],
            )
            for row in rows
        ]

    # =========================================================================
    # Metrics
    # =========================================================================

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ):
        """Record a metric value."""
        with self.cursor() as cur:
            cur.execute(
                """
                INSERT INTO metrics (id, name, value, tags)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    name,
                    value,
                    json.dumps(tags or {}),
                )
            )

    def get_metrics(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get metric values."""
        conditions = ["name = %s"]
        params = [name]

        if start_time:
            conditions.append("timestamp >= %s")
            params.append(start_time)
        if end_time:
            conditions.append("timestamp <= %s")
            params.append(end_time)

        params.append(limit)

        with self.cursor() as cur:
            cur.execute(
                f"""
                SELECT * FROM metrics
                WHERE {' AND '.join(conditions)}
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                params
            )
            return cur.fetchall()

    # =========================================================================
    # Cleanup
    # =========================================================================

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


class InMemoryStateStore:
    """
    In-memory state store for testing and development.

    API-compatible with StateStore but doesn't require PostgreSQL.
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._checkpoints: Dict[str, Checkpoint] = {}
        self._logs: List[AgentLog] = []
        self._metrics: List[Dict[str, Any]] = []

    def create_task(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        agent_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        task = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            status=TaskStatus.PENDING,
            input_data=input_data,
            agent_id=agent_id,
            parent_task_id=parent_task_id,
            metadata=metadata or {},
        )
        self._tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = status
            task.updated_at = datetime.utcnow()
            if output_data:
                task.output_data = output_data
            if error:
                task.error = error
            if status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                task.completed_at = datetime.utcnow()

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Task]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        if task_type:
            tasks = [t for t in tasks if t.type == task_type]
        if agent_id:
            tasks = [t for t in tasks if t.agent_id == agent_id]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)[:limit]

    def create_checkpoint(
        self,
        task_id: str,
        checkpoint_type: CheckpointType,
        state_snapshot: Dict[str, Any],
        file_hashes: Dict[str, str],
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Checkpoint:
        checkpoint = Checkpoint(
            id=str(uuid.uuid4()),
            task_id=task_id,
            type=checkpoint_type,
            state_snapshot=state_snapshot,
            file_hashes=file_hashes,
            description=description,
            metadata=metadata or {},
        )
        self._checkpoints[checkpoint.id] = checkpoint
        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        return self._checkpoints.get(checkpoint_id)

    def list_checkpoints(
        self,
        task_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Checkpoint]:
        checkpoints = list(self._checkpoints.values())
        if task_id:
            checkpoints = [c for c in checkpoints if c.task_id == task_id]
        return sorted(checkpoints, key=lambda c: c.created_at, reverse=True)[:limit]

    def get_latest_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        checkpoints = self.list_checkpoints(task_id=task_id, limit=1)
        return checkpoints[0] if checkpoints else None

    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        details: Dict[str, Any],
        task_id: Optional[str] = None,
        level: str = "info",
    ):
        self._logs.append(AgentLog(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            task_id=task_id,
            action=action,
            details=details,
            level=level,
        ))

    def get_agent_logs(
        self,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100,
    ) -> List[AgentLog]:
        logs = self._logs.copy()
        if agent_id:
            logs = [l for l in logs if l.agent_id == agent_id]
        if task_id:
            logs = [l for l in logs if l.task_id == task_id]
        if level:
            logs = [l for l in logs if l.level == level]
        return sorted(logs, key=lambda l: l.timestamp, reverse=True)[:limit]

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ):
        self._metrics.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.utcnow(),
        })

    def get_metrics(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        metrics = [m for m in self._metrics if m["name"] == name]
        if start_time:
            metrics = [m for m in metrics if m["timestamp"] >= start_time]
        if end_time:
            metrics = [m for m in metrics if m["timestamp"] <= end_time]
        return sorted(metrics, key=lambda m: m["timestamp"], reverse=True)[:limit]

    def close(self):
        pass
