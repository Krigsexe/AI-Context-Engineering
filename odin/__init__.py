#!/usr/bin/env python3
"""
ODIN v6.0 - Autonomous AI Codebase Assistant (Complete Edition)
Copyright 2025 Make With Passion by Krigs
License: MIT

Main package initialization module.
"""

__version__ = "6.0.0"
__author__ = "Make With Passion by Krigs"
__license__ = "MIT"
__copyright__ = "Copyright 2025 Make With Passion by Krigs"

# Package metadata
ODIN_VERSION = "6.0.0-COMPLETE"
ODIN_RELEASE_DATE = "2025-04-05"
ODIN_NAME = "ODIN v6.0 - Autonomous AI Codebase Assistant"

# Core constants
ODIN_DIR = ".odin"
CHECKPOINT_FILE = "AI_CHECKPOINT.json"
CONFIG_FILE = "config.json"
LEARNING_LOG_FILE = "learning_log.json"
LOCK_FILE = "odin.lock"
AUDIT_REPORT_FILE = "audit_report.md"

# Export main classes and functions
from .core import OdinCore, update_checkpoint, update_config, safe_write_file, safe_write_json
from .cli import main as cli_main
from .instance import InstanceManager
from .audit import AuditEngine
from .backup import SmartBackupManager, BackupManager, BackupError
from .backup_decorator import with_backup, BackupContext, create_manual_backup

__all__ = [
    'OdinCore',
    'cli_main',
    'InstanceManager',
    'AuditEngine',
    'SmartBackupManager',
    'BackupManager',
    'BackupError',
    'with_backup',
    'BackupContext',
    'create_manual_backup',
    'update_checkpoint',
    'update_config',
    'safe_write_file',
    'safe_write_json',
    'ODIN_VERSION',
    'ODIN_NAME',
    'ODIN_DIR',
]
