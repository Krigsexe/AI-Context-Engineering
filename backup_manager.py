#!/usr/bin/env python3
"""
ODIN v6.0 - Complete Backup Manager CLI Integration

This script provides a standalone interface to the ODIN backup system,
demonstrating how to integrate automatic backup functionality into any
write operation workflow.

Usage:
    python backup_manager.py create --reason "before_deployment"
    python backup_manager.py list
    python backup_manager.py rollback --backup backup_20250803_190551.bak.json
    python backup_manager.py cleanup --keep 5
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from odin.backup import SmartBackupManager, BackupError
from odin.backup_decorator import with_backup, BackupContext, create_manual_backup
import argparse
import json
from datetime import datetime
from pathlib import Path


class BackupManagerCLI:
    """Command-line interface for ODIN backup system."""
    
    def __init__(self):
        self.backup_manager = SmartBackupManager()
    
    def create_backup(self, reason="manual_backup"):
        """Create a new backup."""
        try:
            print(f"🔄 Creating backup with reason: {reason}")
            backup_path = self.backup_manager.create_backup(reason)
            
            if backup_path:
                print(f"✅ Backup created successfully:")
                print(f"   📁 {os.path.basename(backup_path)}")
                print(f"   📍 {backup_path}")
                
                # Show backup info
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                print(f"   📊 Files: {backup_data['metadata']['files_count']}")
                print(f"   💾 Size: {backup_data['metadata']['backup_size_estimate']}KB")
                print(f"   🔧 Git changes: {'Yes' if backup_data['git_info']['has_changes'] else 'No'}")
                print(f"   📦 Snapshot: {'Yes' if backup_data['working_tree_snapshot']['available'] else 'No'}")
                
                return backup_path
            else:
                print("❌ Backup creation failed")
                return None
                
        except BackupError as e:
            print(f"❌ Backup error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def list_backups(self, limit=20):
        """List all available backups."""
        backups = self.backup_manager.list_backups()
        
        if not backups:
            print("📦 No backups found")
            return
        
        print(f"📦 Found {len(backups)} backup(s):")
        print()
        
        # Table header
        header = f"{'Filename':<35} {'Timestamp':<20} {'Reason':<25} {'Hash':<18} {'Git':<4} {'Snap':<4} {'Size':<8}"
        print(header)
        print("-" * len(header))
        
        for backup in backups[:limit]:
            git_marker = "✓" if backup['has_git_diff'] else "-"
            snap_marker = "✓" if backup['has_snapshot'] else "-"
            size_str = f"{backup['size_kb']}KB" if backup['size_kb'] > 0 else "N/A"
            
            # Format timestamp
            timestamp = backup['timestamp'][:19] if len(backup['timestamp']) > 19 else backup['timestamp']
            
            row = f"{backup['filename']:<35} {timestamp:<20} {backup['reason'][:24]:<25} {backup['project_hash']:<18} {git_marker:<4} {snap_marker:<4} {size_str:<8}"
            print(row)
        
        if len(backups) > limit:
            print(f"\n... and {len(backups) - limit} more. Use --limit to see more.")
    
    def rollback_to_backup(self, backup_file):
        """Rollback to a specific backup."""
        try:
            print(f"🔄 Rolling back to backup: {backup_file}")
            
            if self.backup_manager.rollback_to(backup_file):
                print(f"✅ Rollback completed successfully")
                print(f"💡 Project state restored from {backup_file}")
                return True
            else:
                print("❌ Rollback failed")
                return False
                
        except Exception as e:
            print(f"❌ Rollback error: {e}")
            return False
    
    def rollback_last(self):
        """Rollback to the last backup."""
        try:
            print("🔄 Initiating rollback to last backup...")
            backup_path = self.backup_manager.rollback_last_valid()
            
            if backup_path:
                print(f"✅ Rollback completed")
                print(f"💡 Restored from {os.path.basename(backup_path)}")
                return True
            else:
                print("❌ Rollback failed - no backups available")
                return False
                
        except Exception as e:
            print(f"❌ Rollback error: {e}")
            return False
    
    def cleanup_backups(self, keep=10, confirm=True):
        """Clean up old backups."""
        try:
            backups = self.backup_manager.list_backups()
            
            if len(backups) <= keep:
                print(f"📦 Only {len(backups)} backup(s) found, nothing to clean up")
                return 0
                
            to_remove = len(backups) - keep
            
            if confirm:
                print(f"⚠️  This will remove {to_remove} old backup(s), keeping {keep} most recent.")
                response = input("Continue? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("❌ Cancelled")
                    return 0
            
            print(f"🧹 Cleaning up old backups...")
            removed_count = self.backup_manager.cleanup_old_backups(keep)
            
            if removed_count > 0:
                print(f"✅ Removed {removed_count} old backup(s)")
            else:
                print("⚠️  No backups were removed")
                
            return removed_count
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            return 0
    
    def show_backup_info(self, backup_file):
        """Show detailed information about a specific backup."""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                # Try looking in .odin/backups/
                backup_path = Path('.odin/backups') / backup_file
                if not backup_path.exists():
                    print(f"❌ Backup file not found: {backup_file}")
                    return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            print(f"📋 Backup Information: {backup_path.name}")
            print("=" * 50)
            print(f"📅 Created: {backup_data['backup_timestamp']}")
            print(f"📝 Reason: {backup_data['reason']}")
            print(f"🏠 Project: {backup_data['project_root']}")
            print(f"🔧 ODIN Version: {backup_data['odin_version']}")
            print(f"💻 Host: {backup_data['metadata']['creation_host']}")
            print()
            
            print("🔍 Project State:")
            checkpoint = backup_data['pre_change_checkpoint']
            print(f"   State: {checkpoint.get('current_state', 'unknown')}")
            print(f"   Last Action: {checkpoint.get('last_action', 'unknown')}")
            print(f"   Test Coverage: {checkpoint.get('test_coverage', 'unknown')}%")
            print()
            
            print("📊 Statistics:")
            print(f"   Files Count: {backup_data['metadata']['files_count']}")
            print(f"   Size Estimate: {backup_data['metadata']['backup_size_estimate']}KB")
            print(f"   Integrity Hash: {backup_data['project_integrity_hash'][:16]}...")
            print()
            
            print("🔧 Git Information:")
            git_info = backup_data['git_info']
            print(f"   Has Changes: {'Yes' if git_info['has_changes'] else 'No'}")
            print(f"   Commit Hash: {git_info['commit_hash'] or 'N/A'}")
            print()
            
            print("📦 Snapshot Information:")
            snapshot = backup_data['working_tree_snapshot']
            print(f"   Available: {'Yes' if snapshot['available'] else 'No'}")
            print(f"   Compression: {snapshot['compression'] or 'N/A'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading backup info: {e}")
            return False


def demonstrate_automatic_backup():
    """Demonstrate automatic backup functionality with decorators."""
    print("\n🔬 Demonstrating Automatic Backup Functionality")
    print("=" * 60)
    
    # Example 1: Using decorator
    @with_backup("before_file_modification")
    def modify_important_file():
        """Example function that modifies files."""
        print("   📝 Modifying important project files...")
        # Simulate file modification
        test_file = Path("test_modification.txt")
        with open(test_file, 'w') as f:
            f.write(f"Modified at {datetime.now()}\n")
        print(f"   ✅ Created/modified {test_file}")
        return str(test_file)
    
    # Example 2: Using context manager
    def modify_with_context():
        """Example using context manager for backup protection."""
        with BackupContext("before_multiple_changes", auto_rollback_on_error=False):
            print("   📝 Making multiple changes...")
            
            # Simulate multiple file operations
            for i in range(3):
                test_file = Path(f"test_file_{i}.txt")
                with open(test_file, 'w') as f:
                    f.write(f"Test file {i} created at {datetime.now()}\n")
                print(f"   ✅ Created {test_file}")
    
    # Example 3: Manual backup before operation
    def modify_with_manual_backup():
        """Example using manual backup creation."""
        backup_path = create_manual_backup("before_manual_operation")
        if backup_path:
            print(f"   📦 Manual backup created: {os.path.basename(backup_path)}")
            
            # Simulate operation
            print("   📝 Performing manual operation...")
            test_file = Path("manual_test.txt")
            with open(test_file, 'w') as f:
                f.write(f"Manual operation at {datetime.now()}\n")
            print(f"   ✅ Created {test_file}")
        else:
            print("   ❌ Could not create manual backup")
    
    print("\n1️⃣ Using @with_backup decorator:")
    result = modify_important_file()
    print(f"   🎯 Function returned: {result}")
    
    print("\n2️⃣ Using BackupContext manager:")
    modify_with_context()
    
    print("\n3️⃣ Using manual backup creation:")
    modify_with_manual_backup()
    
    # Clean up test files
    print("\n🧹 Cleaning up test files...")
    for test_file in Path('.').glob('test_*.txt'):
        test_file.unlink()
        print(f"   🗑️  Removed {test_file}")
    
    for test_file in Path('.').glob('manual_*.txt'):
        test_file.unlink()
        print(f"   🗑️  Removed {test_file}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="ODIN v6.0 Smart Backup Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --reason "before_deployment"
  %(prog)s list --limit 10
  %(prog)s info backup_20250803_190551.bak.json
  %(prog)s rollback-to backup_20250803_190551.bak.json
  %(prog)s rollback-last
  %(prog)s cleanup --keep 5 --no-confirm
  %(prog)s demo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create backup command
    create_parser = subparsers.add_parser('create', help='Create a new backup')
    create_parser.add_argument('--reason', default='manual_backup', 
                              help='Reason for creating the backup')
    
    # List backups command
    list_parser = subparsers.add_parser('list', help='List all backups')
    list_parser.add_argument('--limit', type=int, default=20,
                           help='Maximum number of backups to show')
    
    # Show backup info command
    info_parser = subparsers.add_parser('info', help='Show backup information')
    info_parser.add_argument('backup_file', help='Backup filename or path')
    
    # Rollback to specific backup command
    rollback_to_parser = subparsers.add_parser('rollback-to', help='Rollback to specific backup')
    rollback_to_parser.add_argument('backup_file', help='Backup filename or path')
    
    # Rollback to last backup command
    subparsers.add_parser('rollback-last', help='Rollback to the most recent backup')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.add_argument('--keep', type=int, default=10,
                               help='Number of recent backups to keep')
    cleanup_parser.add_argument('--no-confirm', action='store_true',
                               help='Skip confirmation prompt')
    
    # Demo command
    subparsers.add_parser('demo', help='Demonstrate automatic backup functionality')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = BackupManagerCLI()
    
    # Execute commands
    if args.command == 'create':
        cli.create_backup(args.reason)
        
    elif args.command == 'list':
        cli.list_backups(args.limit)
        
    elif args.command == 'info':
        cli.show_backup_info(args.backup_file)
        
    elif args.command == 'rollback-to':
        cli.rollback_to_backup(args.backup_file)
        
    elif args.command == 'rollback-last':
        cli.rollback_last()
        
    elif args.command == 'cleanup':
        cli.cleanup_backups(args.keep, not args.no_confirm)
        
    elif args.command == 'demo':
        demonstrate_automatic_backup()


if __name__ == '__main__':
    print("🤖 ODIN v6.0 - Smart Rollback & Backup System")
    print("=" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
