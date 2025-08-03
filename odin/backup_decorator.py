#!/usr/bin/env python3
"""
ODIN v6.0 - Backup Decorator

This module provides decorators and utilities for automatic backup creation
before any write operation, ensuring reliability and rollback capability.

Features:
- @with_backup decorator for functions that modify files
- Automatic pre-write operation backup creation  
- Integration with SmartBackupManager
- Error handling and rollback on failures
"""

import functools
import os
from pathlib import Path
from typing import Callable, Any, Optional
from .backup import SmartBackupManager, BackupError


def with_backup(reason: Optional[str] = None):
    """
    Decorator that creates a backup before executing the decorated function.
    
    This decorator ensures that any write operation is preceded by an atomic
    backup, allowing for reliable rollback in case of errors.
    
    Args:
        reason (str, optional): Custom reason for backup creation.
                               Defaults to function name.
    
    Usage:
        @with_backup("before_config_update")
        def update_config(new_config):
            # Function that modifies configuration files
            pass
    
    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Determine backup reason
            backup_reason = reason or f"pre_{func.__name__}"
            
            # Create backup manager
            try:
                backup_manager = SmartBackupManager()
                
                # Create backup before operation
                print(f"🔄 Creating automatic backup before {func.__name__}...")
                backup_path = backup_manager.create_backup(backup_reason)
                
                if not backup_path:
                    print(f"⚠️  Warning: Could not create backup before {func.__name__}")
                else:
                    print(f"✅ Backup created: {os.path.basename(backup_path)}")
                
                # Execute the original function
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful operation
                    backup_manager._log_backup_action(
                        "operation_completed", 
                        os.path.basename(backup_path) if backup_path else "none", 
                        f"successful_{func.__name__}"
                    )
                    
                    return result
                    
                except Exception as e:
                    # Log failed operation
                    if backup_path:
                        backup_manager._log_backup_action(
                            "operation_failed", 
                            os.path.basename(backup_path), 
                            f"failed_{func.__name__}_{str(e)[:50]}"
                        )
                    
                    print(f"❌ Operation {func.__name__} failed: {e}")
                    
                    # Optionally offer rollback (in production, this might be automatic)
                    if backup_path:
                        print(f"💡 Backup available for rollback: {os.path.basename(backup_path)}")
                    
                    # Re-raise the exception
                    raise
                    
            except BackupError as e:
                print(f"❌ Backup system error before {func.__name__}: {e}")
                # Still execute the function but warn user
                print(f"⚠️  Proceeding without backup (high risk)")
                return func(*args, **kwargs)
                
        return wrapper
    return decorator


def ensure_backup_before_write(file_paths: list, reason: str = "file_modification"):
    """
    Ensure backup is created before modifying specific files.
    
    Args:
        file_paths (list): List of file paths that will be modified.
        reason (str): Reason for the backup.
        
    Returns:
        str: Path to created backup or None if failed.
    """
    try:
        backup_manager = SmartBackupManager()
        
        # Check if any of the target files exist and would be modified
        files_exist = any(Path(fp).exists() for fp in file_paths)
        
        if files_exist:
            print(f"🔄 Creating backup before modifying {len(file_paths)} file(s)...")
            backup_path = backup_manager.create_backup(reason)
            
            if backup_path:
                print(f"✅ Pre-modification backup: {os.path.basename(backup_path)}")
                return backup_path
            else:
                print("⚠️  Warning: Could not create pre-modification backup")
                
        return None
        
    except Exception as e:
        print(f"❌ Error creating pre-modification backup: {e}")
        return None


class BackupContext:
    """
    Context manager for operations that require backup protection.
    
    Usage:
        with BackupContext("before_major_refactor"):
            # Perform file modifications
            update_multiple_files()
            refactor_codebase()
    """
    
    def __init__(self, reason: str, auto_rollback_on_error: bool = False):
        """
        Initialize backup context.
        
        Args:
            reason (str): Reason for creating the backup.
            auto_rollback_on_error (bool): Whether to automatically rollback on exception.
        """
        self.reason = reason
        self.auto_rollback_on_error = auto_rollback_on_error
        self.backup_path = None
        self.backup_manager = None
        
    def __enter__(self):
        """Create backup when entering context."""
        try:
            self.backup_manager = SmartBackupManager()
            
            print(f"🔄 Creating backup for context: {self.reason}")
            self.backup_path = self.backup_manager.create_backup(self.reason)
            
            if self.backup_path:
                print(f"✅ Context backup: {os.path.basename(self.backup_path)}")
            else:
                print("⚠️  Warning: Could not create context backup")
                
            return self
            
        except Exception as e:
            print(f"❌ Error creating context backup: {e}")
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handle context exit, optionally rolling back on error."""
        if exc_type is not None:
            # An exception occurred
            print(f"❌ Exception in context: {exc_val}")
            
            if self.auto_rollback_on_error and self.backup_path and self.backup_manager:
                print("🔄 Auto-rolling back due to context exception...")
                try:
                    if self.backup_manager.rollback_to(self.backup_path):
                        print("✅ Automatic rollback completed")
                    else:
                        print("❌ Automatic rollback failed")
                except Exception as rollback_error:
                    print(f"❌ Rollback error: {rollback_error}")
            elif self.backup_path:
                print(f"💡 Backup available for manual rollback: {os.path.basename(self.backup_path)}")
        
        else:
            # No exception, operation completed successfully
            if self.backup_manager and self.backup_path:
                self.backup_manager._log_backup_action(
                    "context_completed", 
                    os.path.basename(self.backup_path), 
                    f"successful_context_{self.reason}"
                )


# Convenience function for manual backup creation
def create_manual_backup(reason: str = "manual_checkpoint") -> Optional[str]:
    """
    Create a manual backup with specified reason.
    
    Args:
        reason (str): Reason for creating the backup.
        
    Returns:
        str: Path to created backup or None if failed.
    """
    try:
        backup_manager = SmartBackupManager()
        backup_path = backup_manager.create_backup(reason)
        
        if backup_path:
            print(f"✅ Manual backup created: {os.path.basename(backup_path)}")
        
        return backup_path
        
    except Exception as e:
        print(f"❌ Manual backup failed: {e}")
        return None


__all__ = [
    'with_backup',
    'ensure_backup_before_write', 
    'BackupContext',
    'create_manual_backup'
]
