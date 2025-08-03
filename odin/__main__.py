#!/usr/bin/env python3
"""
ODIN v6.0 - Autonomous AI Codebase Assistant
Main entry point for CLI execution

This module provides the main entry point for the ODIN CLI when run as:
- python -m odin
- odin (via console_scripts entry point)
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from .cli import main
except ImportError:
    # Fallback import for development
    try:
        from cli import main
    except ImportError as e:
        print(f"❌ ODIN Error: Could not import CLI module: {e}")
        print("Please ensure ODIN is properly installed:")
        print("  pip install odin-ai")
        sys.exit(1)


def main_entry():
    """
    Main entry point with error handling and environment setup.
    """
    try:
        # Set up environment
        os.environ.setdefault('ODIN_CLI_MODE', '1')
        
        # Call the main CLI function
        main()
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user.")
        sys.exit(130)  # Standard exit code for Ctrl+C
        
    except Exception as e:
        print(f"❌ ODIN Fatal Error: {e}")
        if os.environ.get('ODIN_DEBUG', '').lower() in ('1', 'true', 'yes'):
            print("\n🔍 Debug traceback:")
            traceback.print_exc()
        print("\n💡 For help, run: odin --help")
        sys.exit(1)


if __name__ == "__main__":
    main_entry()
