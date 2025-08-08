from __future__ import annotations
import argparse
from pathlib import Path
from . import __version__
from .checkpoint import ensure_scaffold, update_checkpoint
from .checkpoint import LOCK, AUDIT_REPORT
from .utils import ODIN_DIR, BACKUPS
from .integrity import project_sih
from .backup import create_backup
from .audit_engine import run_audit
from .rollback import restore_from_backup


def cmd_init(args):
    ensure_scaffold()
    sih = project_sih(Path.cwd())
    dest = create_backup(Path.cwd(), sih, BACKUPS)
    update_checkpoint(last_backup=str(dest), sih_root=hash(tuple(sorted(sih.values()))))
    print(f"✅ ODIN initialized. Backup at {dest}")


def cmd_audit(args):
    out = run_audit(Path.cwd())
    update_checkpoint(last_audit=out)
    print(f"✅ Audit complete → {AUDIT_REPORT}")


def cmd_rollback(args):
    b = restore_from_backup(Path.cwd(), BACKUPS)
    if not b:
        print("⚠️  No backups found."); return
    update_checkpoint(last_backup=str(b))
    print(f"✅ Restored from {b}")


def cmd_start(args):
    profile = args.risk
    print(f"▶️  Starting ODIN in '{profile}' risk profile (simulated)")
    # Ici: brancher grounded-only + double-pass + schema-guard selon profil


def build_parser():
    p = argparse.ArgumentParser(prog="odin", description="ODIN v6.1 – Autonomous AI Codebase Assistant")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="Initialize ODIN scaffold and first backup")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("audit", help="Run integrity audit")
    s.add_argument("--full", action="store_true", help="run full audit")
    s.set_defaults(fn=cmd_audit)

    s = sub.add_parser("rollback", help="Restore from latest backup")
    s.set_defaults(fn=cmd_rollback)

    s = sub.add_parser("start", help="Start with a risk profile")
    s.add_argument("--risk", choices=["low", "med", "high"], default="low")
    s.set_defaults(fn=cmd_start)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
