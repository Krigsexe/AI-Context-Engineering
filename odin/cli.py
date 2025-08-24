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
from .checkpoint import lock_instance, unlock_instance
from .context_guard import context_signature

# optional plugins (best-effort import)
try:
    from plugins.contextguard.contextguard import validate as plugin_context_validate
except Exception:  # pragma: no cover
    plugin_context_validate = lambda: True
try:
    from plugins.depguard.depguard import check as plugin_dep_check
except Exception:  # pragma: no cover
    plugin_dep_check = lambda path: True


def cmd_init(args):
    lock_instance()
    try:
        ensure_scaffold()
        sih = project_sih(Path.cwd())
        dest = create_backup(Path.cwd(), sih, BACKUPS)
        ctxsig = context_signature(Path.cwd())
        update_checkpoint(last_backup=str(dest), sih_root=hash(tuple(sorted(sih.values()))), sih_snapshot=sih, context_sig=ctxsig)
        print(f"✅ ODIN initialized. Backup at {dest}")
    finally:
        unlock_instance()


def cmd_audit(args):
    lock_instance()
    try:
        out = run_audit(Path.cwd())
        ctxsig = context_signature(Path.cwd())
        # persist snapshot and root into checkpoint
        update_checkpoint(last_audit={k: v for k, v in out.items() if k != "sih_snapshot"},
                          sih_snapshot=out.get("sih_snapshot"),
                          sih_root=out.get("sih_root"),
                          context_sig=ctxsig)
        print(f"✅ Audit complete → {AUDIT_REPORT}")
    finally:
        unlock_instance()


def cmd_rollback(args):
    lock_instance()
    try:
        b = restore_from_backup(Path.cwd(), BACKUPS, mirror=getattr(args, "mirror", False))
        if not b:
            print("⚠️  No backups found."); return
        # After restore, refresh snapshot and context signature
        sih = project_sih(Path.cwd())
        ctxsig = context_signature(Path.cwd())
        update_checkpoint(last_backup=str(b), sih_root=hash(tuple(sorted(sih.values()))), sih_snapshot=sih, context_sig=ctxsig)
        print(f"✅ Restored from {b}")
    finally:
        unlock_instance()


def cmd_start(args):
    profile = args.risk
    lock_instance()
    try:
        # Context signature drift check
        ctxsig_now = context_signature(Path.cwd())
        from .checkpoint import get_checkpoint
        ckpt = get_checkpoint()
        prev_sig = ckpt.get("context_sig")
        if prev_sig and prev_sig != ctxsig_now and not args.allow_drift:
            print("❌ Context drift detected. Use --allow-drift to proceed.")
            return

        # Plugin guards
        if not plugin_context_validate():
            print("❌ ContextGuard validation failed."); return
        if not plugin_dep_check(str(Path.cwd())):
            print("❌ DepGuard check failed."); return

        print(f"▶️  Starting ODIN in '{profile}' risk profile")
        # Future: apply grounded-only + double-pass + schema-guard according to profile
        update_checkpoint(risk_profile=profile, context_sig=ctxsig_now)
    finally:
        unlock_instance()


def cmd_backups_list(args):
    ensure_scaffold()
    if not BACKUPS.exists():
        print("No backups directory."); return
    backups = sorted([p for p in BACKUPS.iterdir() if p.is_dir()])
    for p in backups:
        manifest = p/"manifest.json"
        info = manifest.read_text(encoding="utf-8") if manifest.exists() else "{}"
        print(f"- {p.name}  manifest={len(info)} bytes")


def cmd_backups_prune(args):
    keep = args.keep
    ensure_scaffold()
    backups = sorted([p for p in BACKUPS.iterdir() if p.is_dir()])
    to_delete = backups[:-keep] if keep < len(backups) else []
    for p in to_delete:
        for child in sorted(p.rglob("*"), reverse=True):
            if child.is_file():
                child.unlink()
        for child in sorted(p.rglob("*"), reverse=True):
            if child.is_dir():
                try:
                    child.rmdir()
                except OSError:
                    pass
        try:
            p.rmdir()
        except OSError:
            pass
    print(f"✅ Pruned {len(to_delete)} backups; kept {min(keep, len(backups))}")


def build_parser():
    p = argparse.ArgumentParser(prog="odin", description="ODIN v6.1 – Autonomous AI Codebase Assistant")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="Initialize ODIN scaffold and first backup")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("audit", help="Run integrity audit")
    s.add_argument("--full", action="store_true", help="run full audit")
    s.set_defaults(fn=cmd_audit)

    s = sub.add_parser("rollback", help="Restore from latest backup")
    s.add_argument("--mirror", action="store_true", help="delete files not present in backup")
    s.set_defaults(fn=cmd_rollback)

    s = sub.add_parser("start", help="Start with a risk profile")
    s.add_argument("--risk", choices=["low", "med", "high"], default="low")
    s.add_argument("--allow-drift", action="store_true", help="proceed even if context signature changed")
    s.set_defaults(fn=cmd_start)

    s = sub.add_parser("backups", help="Manage backups")
    ss = s.add_subparsers(dest="sub", required=True)
    s1 = ss.add_parser("list", help="List backups")
    s1.set_defaults(fn=cmd_backups_list)
    s2 = ss.add_parser("prune", help="Prune old backups")
    s2.add_argument("--keep", type=int, default=5, help="number of most recent backups to keep")
    s2.set_defaults(fn=cmd_backups_prune)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
