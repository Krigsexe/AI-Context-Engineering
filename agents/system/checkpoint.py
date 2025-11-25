# =============================================================================
# ODIN v7.0 - Checkpoint Agent
# =============================================================================
# State checkpointing and rollback management
# =============================================================================

from __future__ import annotations
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..shared import (
    BaseAgent,
    AgentCapability,
    AgentResult,
    ConfidenceLevel,
    CheckpointType,
    agent,
    project_sih,
    compare_sih,
)


@agent
class CheckpointAgent(BaseAgent):
    """
    Checkpoint Agent - State preservation and rollback.

    Responsibilities:
    1. Create state checkpoints before risky operations
    2. Store file state and metadata
    3. Enable rollback to previous states
    4. Track state history
    5. Manage checkpoint lifecycle
    """

    @property
    def name(self) -> str:
        return "checkpoint"

    @property
    def description(self) -> str:
        return "Creates and manages state checkpoints for rollback capability"

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="create_checkpoint",
                description="Create a state checkpoint",
                input_schema={
                    "project_root": "string",
                    "description": "string",
                    "checkpoint_type": "string",
                },
                output_schema={
                    "checkpoint_id": "string",
                    "file_count": "int",
                },
            ),
            AgentCapability(
                name="rollback",
                description="Rollback to a checkpoint",
                input_schema={
                    "checkpoint_id": "string",
                },
                output_schema={
                    "files_restored": "int",
                    "success": "bool",
                },
                requires_approval=True,
                risk_level="high",
            ),
            AgentCapability(
                name="list_checkpoints",
                description="List available checkpoints",
                input_schema={
                    "task_id": "string",
                },
                output_schema={
                    "checkpoints": "list",
                },
            ),
            AgentCapability(
                name="compare_states",
                description="Compare current state to checkpoint",
                input_schema={
                    "checkpoint_id": "string",
                },
                output_schema={
                    "changes": "object",
                },
            ),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_dir = Path(kwargs.get("backup_dir", ".odin/backups"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def execute(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Execute checkpoint task."""

        handlers = {
            "create_checkpoint": self._create_checkpoint,
            "rollback": self._rollback,
            "list_checkpoints": self._list_checkpoints,
            "compare_states": self._compare_states,
            "cleanup_old": self._cleanup_old_checkpoints,
        }

        handler = handlers.get(task_type)
        if not handler:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.UNKNOWN,
                reasoning=f"Unknown task type: {task_type}",
            )

        return await handler(input_data, context)

    async def _create_checkpoint(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Create a state checkpoint."""

        project_root = Path(input_data.get("project_root", "."))
        description = input_data.get("description", "Manual checkpoint")
        checkpoint_type = input_data.get("checkpoint_type", CheckpointType.MANUAL.value)
        task_id = input_data.get("task_id", self._current_task_id or "unknown")

        try:
            # Generate checkpoint ID
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            checkpoint_id = f"{task_id}_{timestamp}"

            # Create checkpoint directory
            checkpoint_dir = self.backup_dir / checkpoint_id
            checkpoint_dir.mkdir(parents=True, exist_ok=True)

            # Compute SIH for all project files
            file_hashes = project_sih(project_root)

            # Backup files that might be modified
            backed_up_files = []
            for rel_path in file_hashes.keys():
                src_path = project_root / rel_path
                if src_path.exists() and src_path.is_file():
                    # Only backup source code files
                    if self._should_backup(src_path):
                        dst_path = checkpoint_dir / rel_path
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        backed_up_files.append(rel_path)

            # Save checkpoint metadata
            metadata = {
                "id": checkpoint_id,
                "task_id": task_id,
                "type": checkpoint_type,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
                "project_root": str(project_root.absolute()),
                "file_hashes": file_hashes,
                "backed_up_files": backed_up_files,
            }

            metadata_file = checkpoint_dir / "checkpoint.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))

            # Store in state store if available
            if self.store:
                self.store.create_checkpoint(
                    task_id=task_id,
                    checkpoint_type=CheckpointType(checkpoint_type),
                    state_snapshot={"description": description},
                    file_hashes=file_hashes,
                    description=description,
                    metadata={"backup_dir": str(checkpoint_dir)},
                )

            self.log("checkpoint_created", {
                "checkpoint_id": checkpoint_id,
                "file_count": len(backed_up_files),
            })

            return AgentResult(
                success=True,
                data={
                    "checkpoint_id": checkpoint_id,
                    "file_count": len(backed_up_files),
                    "total_files_tracked": len(file_hashes),
                    "backup_path": str(checkpoint_dir),
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Checkpoint created: {checkpoint_id}",
            )

        except Exception as e:
            self.log("checkpoint_error", {"error": str(e)}, level="error")
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Checkpoint creation failed: {e}",
            )

    async def _rollback(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Rollback to a checkpoint."""

        checkpoint_id = input_data.get("checkpoint_id", "")

        if not checkpoint_id:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No checkpoint ID provided",
            )

        checkpoint_dir = self.backup_dir / checkpoint_id
        metadata_file = checkpoint_dir / "checkpoint.json"

        if not metadata_file.exists():
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Checkpoint not found: {checkpoint_id}",
            )

        try:
            # Load metadata
            metadata = json.loads(metadata_file.read_text())
            project_root = Path(metadata["project_root"])
            backed_up_files = metadata.get("backed_up_files", [])

            # Create a rollback checkpoint first (safety net)
            safety_result = await self._create_checkpoint({
                "project_root": str(project_root),
                "description": f"Pre-rollback safety checkpoint (rolling back to {checkpoint_id})",
                "checkpoint_type": CheckpointType.PRE_CHANGE.value,
            }, context)

            if not safety_result.success:
                return AgentResult(
                    success=False,
                    data=None,
                    confidence=ConfidenceLevel.AXIOM,
                    reasoning="Could not create safety checkpoint before rollback",
                )

            # Restore files
            restored_count = 0
            errors = []

            for rel_path in backed_up_files:
                src_path = checkpoint_dir / rel_path
                dst_path = project_root / rel_path

                if src_path.exists():
                    try:
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        restored_count += 1
                    except Exception as e:
                        errors.append(f"{rel_path}: {e}")

            self.log("rollback_completed", {
                "checkpoint_id": checkpoint_id,
                "files_restored": restored_count,
                "errors": len(errors),
            })

            return AgentResult(
                success=len(errors) == 0,
                data={
                    "checkpoint_id": checkpoint_id,
                    "files_restored": restored_count,
                    "errors": errors,
                    "safety_checkpoint": safety_result.data.get("checkpoint_id"),
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Rolled back to {checkpoint_id}: {restored_count} files restored",
                warnings=errors if errors else None,
            )

        except Exception as e:
            self.log("rollback_error", {"error": str(e)}, level="error")
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Rollback failed: {e}",
            )

    async def _list_checkpoints(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """List available checkpoints."""

        task_id = input_data.get("task_id")
        limit = input_data.get("limit", 20)

        checkpoints = []

        try:
            for checkpoint_dir in sorted(self.backup_dir.iterdir(), reverse=True):
                if not checkpoint_dir.is_dir():
                    continue

                metadata_file = checkpoint_dir / "checkpoint.json"
                if not metadata_file.exists():
                    continue

                metadata = json.loads(metadata_file.read_text())

                # Filter by task_id if provided
                if task_id and metadata.get("task_id") != task_id:
                    continue

                checkpoints.append({
                    "id": metadata.get("id"),
                    "task_id": metadata.get("task_id"),
                    "type": metadata.get("type"),
                    "description": metadata.get("description"),
                    "created_at": metadata.get("created_at"),
                    "file_count": len(metadata.get("backed_up_files", [])),
                })

                if len(checkpoints) >= limit:
                    break

            return AgentResult(
                success=True,
                data={
                    "checkpoints": checkpoints,
                    "total": len(checkpoints),
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Found {len(checkpoints)} checkpoints",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Failed to list checkpoints: {e}",
            )

    async def _compare_states(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Compare current state to a checkpoint."""

        checkpoint_id = input_data.get("checkpoint_id", "")

        if not checkpoint_id:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning="No checkpoint ID provided",
            )

        checkpoint_dir = self.backup_dir / checkpoint_id
        metadata_file = checkpoint_dir / "checkpoint.json"

        if not metadata_file.exists():
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Checkpoint not found: {checkpoint_id}",
            )

        try:
            metadata = json.loads(metadata_file.read_text())
            project_root = Path(metadata["project_root"])
            old_hashes = metadata.get("file_hashes", {})

            # Get current state
            current_hashes = project_sih(project_root)

            # Compare
            changes = compare_sih(old_hashes, current_hashes)

            has_changes = bool(
                changes["added"] or changes["removed"] or changes["modified"]
            )

            return AgentResult(
                success=True,
                data={
                    "checkpoint_id": checkpoint_id,
                    "has_changes": has_changes,
                    "added": changes["added"],
                    "removed": changes["removed"],
                    "modified": changes["modified"],
                    "unchanged_count": len(changes["unchanged"]),
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"{'Changes detected' if has_changes else 'No changes'} since checkpoint",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"State comparison failed: {e}",
            )

    async def _cleanup_old_checkpoints(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Clean up old checkpoints."""

        max_age_days = input_data.get("max_age_days", 7)
        keep_minimum = input_data.get("keep_minimum", 5)

        try:
            checkpoints = []
            for checkpoint_dir in self.backup_dir.iterdir():
                if not checkpoint_dir.is_dir():
                    continue

                metadata_file = checkpoint_dir / "checkpoint.json"
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text())
                    created_at = datetime.fromisoformat(metadata["created_at"])
                    checkpoints.append((checkpoint_dir, created_at))

            # Sort by age (oldest first)
            checkpoints.sort(key=lambda x: x[1])

            # Keep minimum number
            to_delete = checkpoints[:-keep_minimum] if len(checkpoints) > keep_minimum else []

            # Filter by age
            cutoff = datetime.utcnow().replace(tzinfo=None)
            deleted = 0

            for checkpoint_dir, created_at in to_delete:
                age_days = (cutoff - created_at.replace(tzinfo=None)).days
                if age_days > max_age_days:
                    shutil.rmtree(checkpoint_dir)
                    deleted += 1

            return AgentResult(
                success=True,
                data={
                    "deleted_count": deleted,
                    "remaining_count": len(checkpoints) - deleted,
                },
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Cleaned up {deleted} old checkpoints",
            )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                confidence=ConfidenceLevel.AXIOM,
                reasoning=f"Cleanup failed: {e}",
            )

    def _should_backup(self, path: Path) -> bool:
        """Check if file should be backed up."""
        # Backup source code and config files
        backup_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs",
            ".java", ".cpp", ".c", ".h", ".hpp",
            ".json", ".yaml", ".yml", ".toml", ".xml",
            ".md", ".txt", ".sql", ".sh", ".bash",
        }
        return path.suffix.lower() in backup_extensions
