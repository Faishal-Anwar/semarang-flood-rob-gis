#!/usr/bin/env python3
"""Create a consistent SQLite backup of backend/monitoring.db.

Usage:
    python scripts/backup_db.py
    python scripts/backup_db.py --keep 14
"""
from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "backend" / "monitoring.db"
TARGET_DIR = ROOT / "backend" / "backups"


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup monitoring.db")
    parser.add_argument("--keep", type=int, default=14, help="Number of backups to retain")
    args = parser.parse_args()

    if not SOURCE.exists():
        print(f"[SKIP] Database tidak ditemukan: {SOURCE}")
        return 0

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = TARGET_DIR / f"monitoring_{stamp}.db"

    source_conn = sqlite3.connect(SOURCE)
    target_conn = sqlite3.connect(target)
    try:
        source_conn.backup(target_conn)
    finally:
        target_conn.close()
        source_conn.close()

    backups = sorted(TARGET_DIR.glob("monitoring_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in backups[args.keep:]:
        old.unlink()

    print(f"[OK] Backup dibuat: {target}")
    print(f"[OK] Total backup disimpan: {min(len(backups), args.keep)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
