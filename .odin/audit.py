#!/usr/bin/env python3
"""
ODIN v6.0 - Standalone Audit Engine

This module provides a standalone version of the audit functionality
that can be run independently as '.odin/audit.py'.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to import from odin module
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from odin.audit import AuditEngine

def main():
    """
    Main function for standalone audit execution.
    """
    print("🔍 ODIN v6.0 - Audit Engine")
    print("=" * 40)
    
    # Check if --full flag is provided
    full_audit = "--full" in sys.argv
    
    # Initialize audit engine
    audit_engine = AuditEngine()
    
    if full_audit:
        print("🔍 Running comprehensive audit...")
        audit_path = audit_engine.run_full_audit()
    else:
        print("🔍 Running standard audit...")
        audit_path = audit_engine.run_standard_audit()
    
    if audit_path:
        print(f"✅ Audit completed successfully!")
        print(f"📄 Report saved: {audit_path}")
    else:
        print("❌ Audit failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
