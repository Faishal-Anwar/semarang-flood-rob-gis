#!/usr/bin/env python3
"""Review tide thresholds against 30 days of Open-Meteo Marine model data.

This is a model-percentile review, NOT an official BMKG/BPBD rob threshold.
Usage:
    python scripts/review_thresholds.py
    python scripts/review_thresholds.py --write
"""
from __future__ import annotations

import argparse
import json
import statistics
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS = ROOT / "backend" / "thresholds.json"
URL = (
    "https://marine-api.open-meteo.com/v1/marine"
    "?latitude=-6.958&longitude=110.422"
    "&hourly=sea_level_height_msl"
    "&timezone=Asia%2FJakarta&past_days=30&forecast_days=1"
)


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(p / 100 * (len(ordered) - 1)))))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description="Review tide thresholds")
    parser.add_argument("--write", action="store_true", help="Write p95/p99 into backend/thresholds.json")
    args = parser.parse_args()

    request = urllib.request.Request(URL, headers={"User-Agent": "SemarangFloodRobGIS/2.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    values = [float(v) for v in payload.get("hourly", {}).get("sea_level_height_msl", []) if v is not None]
    if not values:
        print("[FAIL] Tidak ada nilai sea_level_height_msl.")
        return 1

    p50 = percentile(values, 50)
    p90 = percentile(values, 90)
    p95 = percentile(values, 95)
    p99 = percentile(values, 99)
    print("[REVIEW] Open-Meteo Marine · 30 hari")
    print(f"  n={len(values)} · min={min(values):.3f} m · max={max(values):.3f} m")
    print(f"  p50={p50:.3f} m · p90={p90:.3f} m · p95={p95:.3f} m · p99={p99:.3f} m")
    print("  Catatan: persentil model bukan ambang rob resmi BMKG/BPBD.")

    if args.write:
        data = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
        tide = data["parameters"]["tide_level"]
        tide["warning"] = round(p95, 2)
        tide["critical"] = round(p99, 2)
        tide["basis"] = (
            f"Persentil 95/99 tinggi muka laut model Open-Meteo Marine 30 hari "
            f"(p95={p95:.2f} m, p99={p99:.2f} m). Bukan ambang rob resmi."
        )
        tide["source"] = "Open-Meteo Marine 30 hari (p95/p99)"
        tide["confidence"] = "medium"
        tide["calibrated"] = True
        tide["calibration_type"] = "model_percentile"
        data["reviewed_at"] = datetime.now().date().isoformat()
        THRESHOLDS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[OK] Threshold pasang diperbarui: warning={tide['warning']} m, critical={tide['critical']} m")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
