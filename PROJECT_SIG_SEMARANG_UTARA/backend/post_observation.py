#!/usr/bin/env python3
"""Kirim observasi monitoring ke API Semarang Flood & Rob GIS.

Contoh:
  python post_observation.py --parameter tide_level --value 1.82 \
      --station "Tide Gauge Tambak Lorok" --unit m --source field
"""
import argparse
import json
import os
import urllib.error
import urllib.request

DEFAULT_URL = os.environ.get("MONITORING_URL", "http://127.0.0.1:8000/api/monitoring/observations")


def main():
    parser = argparse.ArgumentParser(description="Kirim observasi ke API monitoring.")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL endpoint POST observasi")
    parser.add_argument("--station", required=True, help="Nama stasiun/sensor")
    parser.add_argument("--parameter", required=True, choices=["tide_level", "water_level", "rainfall"])
    parser.add_argument("--value", required=True, type=float)
    parser.add_argument("--unit", default=None, help="Satuan; default mengikuti parameter")
    parser.add_argument("--source", default="field", help="Sumber observasi")
    parser.add_argument("--recorded-at", default=None, help="ISO 8601; default sekarang")
    parser.add_argument("--lat", type=float, default=None)
    parser.add_argument("--lon", type=float, default=None)
    parser.add_argument("--api-key", default=os.environ.get("MONITORING_API_KEY"))
    args = parser.parse_args()

    payload = {
        "station_id": args.station,
        "parameter": args.parameter,
        "value": args.value,
        "source": args.source,
    }
    if args.unit:
        payload["unit"] = args.unit
    if args.recorded_at:
        payload["recorded_at"] = args.recorded_at
    if args.lat is not None:
        payload["lat"] = args.lat
    if args.lon is not None:
        payload["lon"] = args.lon

    headers = {"Content-Type": "application/json"}
    if args.api_key:
        headers["X-API-Key"] = args.api_key

    request = urllib.request.Request(
        args.url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            print(response.status, response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        print("HTTP", error.code, error.read().decode("utf-8"))
        raise SystemExit(1)
    except urllib.error.URLError as error:
        print("Gagal terhubung:", error.reason)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
