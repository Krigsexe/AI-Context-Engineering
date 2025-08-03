#!/usr/bin/env python3
"""
ODIN v6.0 - Instance Management Module

This module handles single-instance enforcement to prevent
multiple ODIN instances from running simultaneously.
"""

import os
import sys
import time
import psutil
import filelock
from pathlib import Path
from . import ODIN_DIR, LOCK_FILE


class InstanceManager:
    """
    Manages ODIN instance lifecycle and enforces single-instance rule.
    """
    
    def __init__(self, project_root=None):
        """
        Initialize the instance manager.
        
        Args:
            project_root (str, optional): Root directory of the project.
                                        Defaults to current working directory.
        """
        self.project_root = Path(project_root or os.getcwd()).resolve()
        self.odin_dir = self.project_root / ODIN_DIR
        self.lock_file_path = self.odin_dir / LOCK_FILE
        self.lock = None
        
    def is_odin_running(self):
        """
        Check if another ODIN instance is currently running.
        
        Returns:
            bool: True if another instance is detected, False otherwise.
        """
        if not self.lock_file_path.exists():
            return False
            
        try:
            # Try to read the PID from lock file
            with open(self.lock_file_path, 'r') as f:
                pid_data = f.read().strip()
                if not pid_data:
                    return False
                    
                pid = int(pid_data)
                
            # Check if process with this PID exists and is ODIN
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                # Check if it's actually an ODIN process
                cmdline = ' '.join(process.cmdline())
                if 'odin' in cmdline.lower():
                    return True
                    
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError):
            # Lock file is stale or process is not accessible
            pass
            
        # Clean up stale lock file
        try:
            self.lock_file_path.unlink()
        except FileNotFoundError:
            pass
            
        return False
        
    def graceful_shutdown(self, timeout=10):
        """
        Attempt to gracefully shutdown any running ODIN instance.
        
        Args:
            timeout (int): Maximum time to wait for shutdown in seconds.
            
        Returns:
            bool: True if shutdown was successful, False otherwise.
        """
        if not self.is_odin_running():
            return True
            
        try:
            with open(self.lock_file_path, 'r') as f:
                pid = int(f.read().strip())
                
            process = psutil.Process(pid)
            
            # Send termination signal
            process.terminate()
            
            # Wait for graceful termination
            start_time = time.time()
            while time.time() - start_time < timeout:
                if not psutil.pid_exists(pid):
                    return True
                time.sleep(0.1)
                
            # Force kill if still running
            if psutil.pid_exists(pid):
                process.kill()
                time.sleep(0.5)
                
            return not psutil.pid_exists(pid)
            
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError):
            return True
            
    def create_lock_file(self):
        """
        Create a lock file with current process PID.
        
        Returns:
            bool: True if lock file was created successfully.
        """
        try:
            # Ensure .odin directory exists
            self.odin_dir.mkdir(parents=True, exist_ok=True)
            
            # Write current PID to lock file
            with open(self.lock_file_path, 'w') as f:
                f.write(str(os.getpid()))
                
            return True
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create lock file: {e}")
            return False
            
    def acquire_lock(self, timeout=30):
        """
        Acquire an exclusive file lock for this ODIN instance.
        
        Args:
            timeout (int): Maximum time to wait for lock acquisition.
            
        Returns:
            bool: True if lock was acquired successfully.
        """
        try:
            self.odin_dir.mkdir(parents=True, exist_ok=True)
            
            # Use filelock for cross-platform file locking
            lock_path = str(self.lock_file_path) + '.filelock'
            self.lock = filelock.FileLock(lock_path, timeout=timeout)
            
            with self.lock:
                self.create_lock_file()
                return True
                
        except filelock.Timeout:
            print("⚠️  Timeout: Another ODIN instance is running.")
            return False
        except Exception as e:
            print(f"⚠️  Warning: Could not acquire lock: {e}")
            return False
            
    def release_lock(self):
        """
        Release the instance lock and clean up lock file.
        """
        try:
            if self.lock_file_path.exists():
                self.lock_file_path.unlink()
        except Exception:
            pass
            
        if self.lock:
            try:
                self.lock.release()
            except Exception:
                pass
                
    def wait_for_termination(self, timeout=10):
        """
        Wait for any running ODIN instance to terminate.
        
        Args:
            timeout (int): Maximum time to wait in seconds.
            
        Returns:
            bool: True if no instances are running after wait.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_odin_running():
                return True
            time.sleep(0.5)
            
        return False


def ensure_single_instance():
    """
    Ensure that only one ODIN instance is running.
    
    This function implements the fundamental rule of single-instance enforcement.
    If another instance is detected, it attempts graceful shutdown.
    
    Returns:
        bool: True if single instance is ensured, False if conflicts remain.
    """
    manager = InstanceManager()
    
    if manager.is_odin_running():
        print("⚠️  Active ODIN instance detected. Shutting down...")
        
        if manager.graceful_shutdown():
            print("✅ Previous instance shut down successfully.")
        else:
            print("❌ Could not shut down previous instance.")
            print("Please manually terminate any running ODIN processes.")
            return False
            
        # Wait for complete termination
        if not manager.wait_for_termination():
            print("⚠️  Warning: Previous instance may still be running.")
            
    # Create new lock file for this instance
    return manager.create_lock_file()


# Module cleanup on exit
import atexit

def cleanup_on_exit():
    """Clean up lock files on process exit."""
    manager = InstanceManager()
    manager.release_lock()

atexit.register(cleanup_on_exit)
