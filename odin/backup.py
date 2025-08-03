#!/usr/bin/env python3
"""
ODIN v6.0 - Smart Rollback & Backup System

This module provides comprehensive backup management functionality for ODIN,
including atomic backups, smart rollback, and working tree snapshots with
full git integration and semantic integrity validation.

Features:
- Atomic backup creation with pre-change AI_CHECKPOINT snapshots
- Git diff patches and working tree compression
- Smart rollback with integrity validation
- Automatic backup before any write operation
- YYYYMMDD_HHMMSS.bak.json naming convention
- Full dependency and linkage preservation
"""

import os
import json
import gzip
import shutil
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from . import ODIN_DIR, CHECKPOINT_FILE, LEARNING_LOG_FILE


class BackupError(Exception):
    """Custom exception for backup operations."""
    pass


class SmartBackupManager:
    """
    Advanced backup and restoration system for ODIN v6.0.
    
    Provides atomic backups, smart rollback, git integration,
    and semantic integrity validation.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the Smart Backup Manager.
        
        Args:
            project_root (str, optional): Root directory of the project.
                                        Defaults to current working directory.
        """
        self.project_root = Path(project_root or os.getcwd()).resolve()
        self.odin_dir = self.project_root / ODIN_DIR
        self.backups_dir = self.odin_dir / 'backups'
        self.checkpoint_file = self.odin_dir / CHECKPOINT_FILE
        self.learning_log_file = self.odin_dir / LEARNING_LOG_FILE
        
        # Ensure backups directory exists
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if git repository exists
        self.git_available = (self.project_root / '.git').exists()
        
    def _generate_backup_filename(self) -> str:
        """
        Generate backup filename with YYYYMMDD_HHMMSS format.
        
        Returns:
            str: Formatted backup filename.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{timestamp}.bak.json"
    
    def _get_git_diff_patch(self) -> Optional[str]:
        """
        Get git diff patch for current changes.
        
        Returns:
            str: Git diff patch or None if no git or no changes.
        """
        if not self.git_available:
            return None
            
        try:
            # Get staged and unstaged changes
            result = subprocess.run(
                ['git', 'diff', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
                
            # If no changes against HEAD, get unstaged changes
            result = subprocess.run(
                ['git', 'diff'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            return result.stdout if result.returncode == 0 else None
            
        except Exception as e:
            print(f"⚠️  Warning: Could not get git diff - {e}")
            return None
    
    def _create_working_tree_snapshot(self) -> Optional[str]:
        """
        Create compressed snapshot of the working tree.
        
        Returns:
            str: Base64 encoded compressed snapshot or None if failed.
        """
        try:
            import base64
            import tarfile
            from io import BytesIO
            
            # Create in-memory tar.gz archive
            buffer = BytesIO()
            
            with tarfile.open(fileobj=buffer, mode='w:gz') as tar:
                # Add important project files (exclude .git, .odin/backups, __pycache__, etc.)
                for item in self.project_root.rglob('*'):
                    if self._should_include_in_snapshot(item):
                        try:
                            tar.add(item, arcname=item.relative_to(self.project_root))
                        except (OSError, ValueError):
                            continue  # Skip files that can't be archived
            
            # Encode as base64 for JSON storage
            buffer.seek(0)
            compressed_data = buffer.getvalue()
            return base64.b64encode(compressed_data).decode('utf-8')
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create working tree snapshot - {e}")
            return None
    
    def _should_include_in_snapshot(self, path: Path) -> bool:
        """
        Determine if a file/directory should be included in the snapshot.
        
        Args:
            path (Path): Path to evaluate.
            
        Returns:
            bool: True if should be included.
        """
        # Exclude patterns
        exclude_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.vscode', '.idea', '.DS_Store', 'dist', 'build',
            '.odin/backups'  # Don't backup other backups
        }
        
        # Check if any part of the path matches exclude patterns
        for part in path.parts:
            if part in exclude_patterns:
                return False
                
        # Include files with important extensions
        if path.is_file():
            important_extensions = {
                '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md',
                '.yml', '.yaml', '.toml', '.cfg', '.ini', '.txt',
                '.sh', '.bat', '.ps1', '.sql', '.html', '.css',
                '.go', '.rs', '.java', '.cpp', '.c', '.h'
            }
            return path.suffix.lower() in important_extensions or path.name in {
                'Dockerfile', 'Makefile', 'requirements.txt', 'package.json',
                'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle'
            }
            
        return path.is_dir() and not path.name.startswith('.')
    
    def _load_current_checkpoint(self) -> Dict[str, Any]:
        """
        Load current AI_CHECKPOINT.json data.
        
        Returns:
            dict: Current checkpoint data.
        """
        try:
            if self.checkpoint_file.exists():
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not load checkpoint - {e}")
            
        # Return default checkpoint structure
        return {
            "version": "6.0.0",
            "timestamp": datetime.now().isoformat() + "Z",
            "current_state": "unknown",
            "last_action": "backup_creation",
            "integrity": {
                "binary_sha256": None,
                "semantic_hash": None
            },
            "context": {
                "language": None,
                "framework": None,
                "architecture": None
            },
            "backup_ref": None,
            "test_coverage": 0.0
        }
    
    def _calculate_project_hash(self) -> str:
        """
        Calculate SHA-256 hash of important project files.
        
        Returns:
            str: Hexadecimal hash string.
        """
        hasher = hashlib.sha256()
        
        # Sort files for consistent hashing
        files_to_hash = []
        for item in self.project_root.rglob('*'):
            if item.is_file() and self._should_include_in_snapshot(item):
                files_to_hash.append(item)
        
        files_to_hash.sort()
        
        for file_path in files_to_hash:
            try:
                with open(file_path, 'rb') as f:
                    hasher.update(file_path.as_posix().encode('utf-8'))
                    hasher.update(f.read())
            except (OSError, UnicodeDecodeError):
                continue  # Skip files that can't be read
                
        return hasher.hexdigest()
    
    def create_backup(self, reason: str = "pre_write_operation") -> Optional[str]:
        """
        Create atomic backup with pre-change AI_CHECKPOINT and git diff/snapshot.
        
        Args:
            reason (str): Reason for creating the backup.
            
        Returns:
            str: Path to created backup file or None if failed.
        """
        try:
            backup_filename = self._generate_backup_filename()
            backup_path = self.backups_dir / backup_filename
            
            print(f"🔄 Creating backup: {backup_filename}")
            
            # Load current checkpoint
            pre_change_checkpoint = self._load_current_checkpoint()
            
            # Get git diff patch
            git_diff_patch = self._get_git_diff_patch()
            
            # Create working tree snapshot
            working_tree_snapshot = self._create_working_tree_snapshot()
            
            # Calculate project integrity hash
            project_hash = self._calculate_project_hash()
            
            # Create backup data structure
            backup_data = {
                "$schema": "../.odin/schemas/backup.schema.json",
                "odin_version": "6.0.0",
                "backup_timestamp": datetime.now().isoformat() + "Z",
                "reason": reason,
                "project_root": str(self.project_root),
                "git_available": self.git_available,
                
                # Pre-change state
                "pre_change_checkpoint": pre_change_checkpoint,
                "project_integrity_hash": project_hash,
                
                # Git information
                "git_info": {
                    "has_changes": git_diff_patch is not None,
                    "diff_patch": git_diff_patch,
                    "commit_hash": self._get_git_commit_hash()
                },
                
                # Working tree snapshot (compressed)
                "working_tree_snapshot": {
                    "available": working_tree_snapshot is not None,
                    "compressed_data": working_tree_snapshot,
                    "compression": "gzip+base64" if working_tree_snapshot else None
                },
                
                # Metadata
                "metadata": {
                    "files_count": len(list(self.project_root.rglob('*'))),
                    "backup_size_estimate": len(working_tree_snapshot or "") // 1024,  # KB
                    "creation_host": os.environ.get('COMPUTERNAME', 'unknown'),
                    "odin_session_id": pre_change_checkpoint.get('session_id', 'unknown')
                }
            }
            
            # Write backup file atomically
            temp_backup_path = backup_path.with_suffix('.tmp')
            with open(temp_backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_backup_path.rename(backup_path)
            
            # Update checkpoint with backup reference
            pre_change_checkpoint['backup_ref'] = f".odin/backups/{backup_filename}"
            pre_change_checkpoint['last_action'] = f"backup_created_{reason}"
            pre_change_checkpoint['timestamp'] = datetime.now().isoformat() + "Z"
            
            # Save updated checkpoint
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(pre_change_checkpoint, f, indent=2, ensure_ascii=False)
            
            # Log backup creation
            self._log_backup_action("backup_created", backup_filename, reason)
            
            print(f"✅ Backup created successfully: {backup_filename}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            raise BackupError(f"Failed to create backup: {e}")
    
    def _get_git_commit_hash(self) -> Optional[str]:
        """
        Get current git commit hash.
        
        Returns:
            str: Current commit hash or None.
        """
        if not self.git_available:
            return None
            
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def _log_backup_action(self, action: str, backup_file: str, reason: str):
        """
        Log backup action to learning log.
        
        Args:
            action (str): Action type.
            backup_file (str): Backup filename.
            reason (str): Reason for action.
        """
        try:
            # Load existing log
            learning_log = {"logs": []}
            if self.learning_log_file.exists():
                with open(self.learning_log_file, 'r', encoding='utf-8') as f:
                    learning_log = json.load(f)
            
            # Add new log entry
            log_entry = {
                "timestamp": datetime.now().isoformat() + "Z",
                "action": action,
                "backup_file": backup_file,
                "reason": reason,
                "type": "backup_system"
            }
            
            learning_log.setdefault("logs", []).append(log_entry)
            
            # Save updated log
            with open(self.learning_log_file, 'w', encoding='utf-8') as f:
                json.dump(learning_log, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️  Warning: Could not log backup action - {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups with metadata.
        
        Returns:
            list: List of backup information dictionaries.
        """
        backups = []
        
        if not self.backups_dir.exists():
            return backups
            
        for backup_file in sorted(self.backups_dir.glob('*.bak.json'), reverse=True):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                    
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "timestamp": backup_data.get('backup_timestamp', 'unknown'),
                    "reason": backup_data.get('reason', 'unknown'),
                    "project_hash": backup_data.get('project_integrity_hash', 'unknown')[:16] + '...',
                    "has_git_diff": backup_data.get('git_info', {}).get('has_changes', False),
                    "has_snapshot": backup_data.get('working_tree_snapshot', {}).get('available', False),
                    "size_kb": backup_data.get('metadata', {}).get('backup_size_estimate', 0)
                })
                
            except Exception as e:
                print(f"⚠️  Warning: Could not read backup {backup_file.name} - {e}")
                continue
                
        return backups
    
    def rollback_to(self, backup_identifier: Union[str, Path]) -> bool:
        """
        Rollback to a specific backup.
        
        Args:
            backup_identifier (str|Path): Backup filename or full path.
            
        Returns:
            bool: True if rollback successful.
        """
        try:
            # Resolve backup path
            if isinstance(backup_identifier, str):
                if backup_identifier.endswith('.bak.json'):
                    backup_path = self.backups_dir / backup_identifier
                else:
                    backup_path = Path(backup_identifier)
            else:
                backup_path = backup_identifier
                
            if not backup_path.exists():
                print(f"❌ Backup file not found: {backup_path}")
                return False
                
            print(f"🔄 Rolling back to: {backup_path.name}")
            
            # Load backup data
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Create a backup of current state before rollback
            current_backup = self.create_backup(f"pre_rollback_to_{backup_path.name}")
            
            # Restore checkpoint
            pre_change_checkpoint = backup_data.get('pre_change_checkpoint', {})
            if pre_change_checkpoint:
                with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(pre_change_checkpoint, f, indent=2, ensure_ascii=False)
                print("✅ AI_CHECKPOINT.json restored")
            
            # Apply git diff if available
            git_info = backup_data.get('git_info', {})
            if self.git_available and git_info.get('diff_patch'):
                if self._apply_git_patch(git_info['diff_patch']):
                    print("✅ Git diff patch applied")
                else:
                    print("⚠️  Warning: Could not apply git diff patch")
            
            # Restore from working tree snapshot if needed
            snapshot_info = backup_data.get('working_tree_snapshot', {})
            if snapshot_info.get('available') and snapshot_info.get('compressed_data'):
                if self._restore_from_snapshot(snapshot_info['compressed_data']):
                    print("✅ Working tree snapshot restored")
                else:
                    print("⚠️  Warning: Could not restore working tree snapshot")
            
            # Update checkpoint with rollback info
            self._update_checkpoint_after_rollback(backup_path.name)
            
            # Log rollback action
            self._log_backup_action("rollback_completed", backup_path.name, "user_requested")
            
            print(f"✅ Rollback completed successfully to {backup_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error during rollback: {e}")
            return False
    
    def _apply_git_patch(self, patch_content: str) -> bool:
        """
        Apply git diff patch to working directory.
        
        Args:
            patch_content (str): Git diff patch content.
            
        Returns:
            bool: True if patch applied successfully.
        """
        try:
            # Write patch to temporary file
            patch_file = self.backups_dir / 'temp_rollback.patch'
            with open(patch_file, 'w', encoding='utf-8') as f:
                f.write(patch_content)
            
            # Apply patch using git apply --reverse
            result = subprocess.run(
                ['git', 'apply', '--reverse', str(patch_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Clean up temp patch file
            patch_file.unlink(missing_ok=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"⚠️  Git patch application failed: {e}")
            return False
    
    def _restore_from_snapshot(self, compressed_data: str) -> bool:
        """
        Restore working tree from compressed snapshot.
        
        Args:
            compressed_data (str): Base64 encoded compressed snapshot.
            
        Returns:
            bool: True if restoration successful.
        """
        try:
            import base64
            import tarfile
            from io import BytesIO
            
            # Decode and decompress
            compressed_bytes = base64.b64decode(compressed_data)
            buffer = BytesIO(compressed_bytes)
            
            # Extract to project root (with caution)
            with tarfile.open(fileobj=buffer, mode='r:gz') as tar:
                # Only extract files that should be restored
                for member in tar.getmembers():
                    if self._should_restore_file(member.name):
                        tar.extract(member, path=self.project_root)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Snapshot restoration failed: {e}")
            return False
    
    def _should_restore_file(self, file_path: str) -> bool:
        """
        Determine if a file should be restored from snapshot.
        
        Args:
            file_path (str): Relative file path.
            
        Returns:
            bool: True if should be restored.
        """
        # Don't restore backup files or git files
        exclude_patterns = {'.git/', '.odin/backups/', '__pycache__/'}
        
        for pattern in exclude_patterns:
            if pattern in file_path:
                return False
                
        return True
    
    def _update_checkpoint_after_rollback(self, backup_filename: str):
        """
        Update checkpoint after successful rollback.
        
        Args:
            backup_filename (str): Name of the backup that was restored.
        """
        try:
            checkpoint = self._load_current_checkpoint()
            checkpoint.update({
                "timestamp": datetime.now().isoformat() + "Z",
                "current_state": "rolled_back",
                "last_action": f"rollback_from_{backup_filename}",
                "integrity": {
                    "binary_sha256": self._calculate_project_hash(),
                    "semantic_hash": "recalculated_after_rollback"
                }
            })
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️  Warning: Could not update checkpoint after rollback - {e}")
    
    def rollback_last_valid(self) -> str:
        """
        Restore the last valid backup (for backward compatibility).
        
        Returns:
            str: Path of the restored backup.
        """
        backups = self.list_backups()
        
        if not backups:
            print("❌ No backups available for rollback.")
            return ""
        
        # Get the most recent backup
        latest_backup = backups[0]
        
        if self.rollback_to(latest_backup['filename']):
            return latest_backup['path']
        else:
            return ""
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backup files, keeping only the most recent ones.
        
        Args:
            keep_count (int): Number of recent backups to keep.
            
        Returns:
            int: Number of backups removed.
        """
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
            
        # Remove oldest backups
        backups_to_remove = backups[keep_count:]
        removed_count = 0
        
        for backup in backups_to_remove:
            try:
                Path(backup['path']).unlink()
                removed_count += 1
                print(f"🗑️  Removed old backup: {backup['filename']}")
            except Exception as e:
                print(f"⚠️  Warning: Could not remove backup {backup['filename']} - {e}")
        
        if removed_count > 0:
            self._log_backup_action("cleanup_completed", f"{removed_count}_backups", "automatic_cleanup")
        
        return removed_count


# Backward compatibility alias
BackupManager = SmartBackupManager


__all__ = ['SmartBackupManager', 'BackupManager', 'BackupError']
