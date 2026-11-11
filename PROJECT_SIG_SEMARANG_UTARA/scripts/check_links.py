#!/usr/bin/env python3
"""Check local href/src targets in the WebGIS HTML pages."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "webgis"
PATTERN = re.compile(r'(?:href|src)=["\']([^"\']+)["\']', re.IGNORECASE)
IGNORED_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "#")


def main() -> int:
    missing: list[tuple[str, str, str]] = []
    checked = 0
    for html in sorted(WEB.glob("*.html")):
        text = html.read_text(encoding="utf-8")
        for raw in PATTERN.findall(text):
            if raw.startswith(IGNORED_PREFIXES) or "${" in raw or "{{" in raw:
                continue
            path = urlsplit(raw).path
            if not path:
                continue
            target = (html.parent / path).resolve()
            checked += 1
            if not target.exists():
                missing.append((html.name, raw, str(target)))

    print(f"[CHECK] {checked} tautan lokal diperiksa")
    if missing:
        print(f"[FAIL] {len(missing)} tautan tidak ditemukan:")
        for source, raw, target in missing:
            print(f"  - {source}: {raw} -> {target}")
        return 1
    print("[PASS] Semua tautan lokal valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
