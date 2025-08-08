import argparse, shutil, time
from pathlib import Path
from .checkpoint import ensure_scaffold
from .integrity import project_sih
from .audit_engine import run_audit
from .utils import BACKUPS
def cmd_init(args):
    ensure_scaffold()
    sih = project_sih(Path.cwd())
    ts = time.strftime("%Y%m%d-%H%M%S"); dest = BACKUPS/ts
    for rel in sih.keys():
        p=Path(rel); d=dest/p; d.parent.mkdir(parents=True, exist_ok=True)
        if p.exists(): shutil.copy2(p,d)
    print(f"✅ ODIN initialized. Backup at {dest}")
def cmd_audit(args):
    out=run_audit(Path.cwd()); print(f"✅ Audit complete. Files: {out['file_count']}")
def cmd_rollback(args):
    bdir=BACKUPS
    if not bdir.exists(): print("⚠️  No backups"); return
    cands=sorted([p for p in bdir.iterdir() if p.is_dir()])
    if not cands: print("⚠️  No backups"); return
    b=cands[-1]
    for p in b.rglob("*"):
        if p.is_dir(): continue
        rel=p.relative_to(b); dst=Path.cwd()/rel; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p,dst)
    print(f"✅ Restored from {b}")
def build_parser():
    p=argparse.ArgumentParser(prog="odin", description="ODIN v6.1 – Offline-First")
    s=p.add_subparsers(dest="cmd", required=True)
    s.add_parser("init").set_defaults(fn=cmd_init)
    s.add_parser("audit").set_defaults(fn=cmd_audit)
    s.add_parser("rollback").set_defaults(fn=cmd_rollback)
    return p
def main():
    parser=build_parser(); args=parser.parse_args(); args.fn(args)
if __name__=="__main__": main()
