#!/usr/bin/env python3
"""
ODIN v6.0 - Command Line Interface (CLI)

This module provides the command-line interface for ODIN,
including the 'init', 'audit', 'backup', and 'rollback' commands.
Integrates the smart backup & rollback system for reliable operations.
"""

import click
import os
from .instance import ensure_single_instance
from .core import create_scaffold, perform_first_audit
from .audit import AuditEngine
from .backup import SmartBackupManager, BackupError


@click.group()
def main():
    """
    ODIN CLI entry point.

    Provides commands for initializing, auditing, and rolling back
    the project environments using ODIN Autonomous AI Codebase Assistant.
    """
    pass


@main.command()
def init():
    """
    Initialize the project environment.

    This command runs a single-instance check, creates the project scaffold
    if it's missing, and performs the first audit to verify integrity.
    """
    click.echo("🔍 Checking for active ODIN instances...")
    if ensure_single_instance():
        click.echo("✅ No active ODIN instances detected.")
    
    click.echo("🛠️ Creating project scaffold...")
    if create_scaffold():
        click.echo("✅ Scaffold created successfully.")
    else:
        click.echo("⚠️  Scaffold already exists.")
    
    click.echo("🔍 Performing first audit...")
    audit_report = perform_first_audit()
    click.echo(f"✅ First audit completed. Report saved at {audit_report}")

@main.command()
@click.option('--language', default='python', help='Programming language of the code')
@click.option('--framework', default='pytest', help='Test framework to use')
@click.argument('file', type=click.File('r'))
def testgen(file, language, framework):
    """
    Generate tests for a given function in a source file.

    This command uses the TestGen module to create tests for the specified programming
    language and framework.
    """
    click.echo(f"🔍 Generating tests for {file.name} using language={language}, framework={framework}...")
    code = file.read()

    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '.odin'))
    from testgen import generate_tests_for_function
    tests = generate_tests_for_function(code, language, framework)
    click.echo(tests)

@main.command()
@click.option('--full', is_flag=True, help='Run a full comprehensive audit')
def audit(full):
    """
    Audit the project environment.

    This command invokes the Audit Engine to analyze the project and output
    a health report.
    """
    audit_engine = AuditEngine()
    
    if full:
        click.echo("🔍 Running full audit...")
        audit_path = audit_engine.run_full_audit()
    else:
        click.echo("🔍 Running standard audit...")
        audit_path = audit_engine.run_standard_audit()
    
    click.echo(f"✅ Audit completed. Report saved at {audit_path}")


@main.command()
@click.option('--reason', default='manual_backup', help='Reason for creating backup')
def backup(reason):
    """
    Create a manual backup of the current project state.
    
    This command creates an atomic backup containing the pre-change AI_CHECKPOINT,
    git diff patch, and compressed working tree snapshot for reliable rollback.
    """
    try:
        backup_manager = SmartBackupManager()
        
        click.echo(f"📦 Creating manual backup (reason: {reason})...")
        backup_path = backup_manager.create_backup(reason)
        
        if backup_path:
            click.echo(f"✅ Backup created successfully: {os.path.basename(backup_path)}")
        else:
            click.echo("❌ Backup creation failed")
            
    except BackupError as e:
        click.echo(f"❌ Backup error: {e}")
        exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        exit(1)


@main.command()
@click.option('--limit', default=20, help='Maximum number of backups to show')
def list_backups(limit):
    """
    List all available backups with metadata.
    
    Shows backup timestamps, reasons, integrity hashes, and available snapshots.
    """
    backup_manager = SmartBackupManager()
    
    backups = backup_manager.list_backups()
    
    if not backups:
        click.echo("📦 No backups found")
        return
        
    click.echo(f"📦 Found {len(backups)} backup(s):")
    click.echo()
    
    # Table header
    click.echo(f"{'Filename':<30} {'Timestamp':<20} {'Reason':<20} {'Hash':<18} {'Git':<4} {'Snap':<4} {'Size':<8}")
    click.echo("-" * 110)
    
    for i, backup in enumerate(backups[:limit]):
        git_marker = "✓" if backup['has_git_diff'] else "-"
        snap_marker = "✓" if backup['has_snapshot'] else "-"
        size_str = f"{backup['size_kb']}KB" if backup['size_kb'] > 0 else "N/A"
        
        # Format timestamp
        timestamp = backup['timestamp'][:19] if len(backup['timestamp']) > 19 else backup['timestamp']
        
        click.echo(f"{backup['filename']:<30} {timestamp:<20} {backup['reason'][:19]:<20} {backup['project_hash']:<18} {git_marker:<4} {snap_marker:<4} {size_str:<8}")
    
    if len(backups) > limit:
        click.echo(f"\n... and {len(backups) - limit} more. Use --limit to see more.")


@main.command()
@click.argument('backup_file')
def rollback_to(backup_file):
    """
    Rollback to a specific backup by filename.
    
    BACKUP_FILE should be the filename (e.g., backup_20250108_142000.bak.json)
    or full path to the backup file.
    """
    try:
        backup_manager = SmartBackupManager()
        
        click.echo(f"🔄 Rolling back to backup: {backup_file}")
        
        if backup_manager.rollback_to(backup_file):
            click.echo(f"✅ Rollback completed successfully")
        else:
            click.echo("❌ Rollback failed")
            exit(1)
            
    except Exception as e:
        click.echo(f"❌ Rollback error: {e}")
        exit(1)


@main.command()
def rollback():
    """
    Rollback to the last valid backup.

    This command selects and restores the most recent backup created by the
    ODIN assistant, ensuring codebase integrity.
    """
    try:
        backup_manager = SmartBackupManager()
        
        click.echo("🔄 Initiating rollback to last backup...")
        backup_path = backup_manager.rollback_last_valid()
        
        if backup_path:
            click.echo(f"✅ Rollback completed. Restored from {os.path.basename(backup_path)}")
        else:
            click.echo("❌ Rollback failed - no backups available")
            exit(1)
            
    except Exception as e:
        click.echo(f"❌ Rollback error: {e}")
        exit(1)


@main.command()
@click.option('--keep', default=10, help='Number of recent backups to keep')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def cleanup_backups(keep, confirm):
    """
    Clean up old backup files, keeping only the most recent ones.
    
    This helps manage disk space by removing older backups while preserving
    the most recent ones for rollback purposes.
    """
    try:
        backup_manager = SmartBackupManager()
        
        backups = backup_manager.list_backups()
        
        if len(backups) <= keep:
            click.echo(f"📦 Only {len(backups)} backup(s) found, nothing to clean up")
            return
            
        to_remove = len(backups) - keep
        
        if not confirm:
            click.echo(f"⚠️  This will remove {to_remove} old backup(s), keeping {keep} most recent.")
            if not click.confirm("Continue?"):
                click.echo("❌ Cancelled")
                return
        
        click.echo(f"🧹 Cleaning up old backups...")
        removed_count = backup_manager.cleanup_old_backups(keep)
        
        if removed_count > 0:
            click.echo(f"✅ Removed {removed_count} old backup(s)")
        else:
            click.echo("⚠️  No backups were removed")
            
    except Exception as e:
        click.echo(f"❌ Cleanup error: {e}")
        exit(1)


if __name__ == '__main__':
    main()
