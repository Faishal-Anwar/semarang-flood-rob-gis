import os
import json
import math
import sqlite3
import secrets
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from collections import defaultdict, deque

app = FastAPI(
    title="Semarang Flood & Rob GIS Monitoring API",
    description=(
        "RESTful Geospatial API for North Semarang Flood & Coastal Inundation Monitoring. "
        "Includes static spatial layers and a near-realtime monitoring endpoint that accepts "
        "manual/field/sensor observations."
    ),
    version="2.0.0"
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8765,http://localhost:8765",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
_rate_buckets = defaultdict(deque)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(self)")
    return response


def enforce_rate_limit(request: Request):
    client = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = _rate_buckets[client]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many requests. Coba lagi dalam satu menit.")
    bucket.append(now)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
WEBGIS_DIR = os.path.join(os.path.dirname(BASE_DIR), "webgis")
DB_PATH = os.path.join(BASE_DIR, "monitoring.db")
API_KEY = os.getenv("MONITORING_API_KEY", "")
REFRESH_INTERVAL_SECONDS = 30
REALTIME_WINDOW_MINUTES = 30
EXTERNAL_TTL_SECONDS = 600
CITIZEN_REPORTS_TTL_SECONDS = 300

PARAMETERS = {
    "tide_level": {
        "label": "Muka air laut",
        "unit": "m",
        "station": "Tide Gauge Tambak Lorok",
        "warning": 1.70,
        "critical": 1.90,
        "decimals": 2
    },
    "water_level": {
        "label": "Muka air sungai",
        "unit": "cm",
        "station": "Sensor Kali Baru",
        "warning": 60.0,
        "critical": 80.0,
        "decimals": 1
    },
    "rainfall": {
        "label": "Curah hujan",
        "unit": "mm/jam",
        "station": "Stasiun Semarang Utara",
        "warning": 10.0,
        "critical": 20.0,
        "decimals": 1
    }
}

THRESHOLDS_PATH = os.path.join(BASE_DIR, "thresholds.json")
DEFAULT_THRESHOLDS = {
    "version": "2026.11",
    "reviewed_at": "2026-11-05",
    "method": "Hujan mengikuti kategori intensitas BMKG; pasang bersifat indikatif; TMA sungai belum terkalibrasi karena tidak ada sensor.",
    "parameters": {
        "rainfall": {
            "warning": 10.0,
            "critical": 20.0,
            "basis": "Kategori hujan lebat 10-20 mm/jam dan sangat lebat >20 mm/jam (BMKG).",
            "source": "BMKG",
            "confidence": "high",
            "calibrated": True
        },
        "tide_level": {
            "warning": 0.95,
            "critical": 1.07,
            "basis": "Persentil 95/99 tinggi muka laut model Open-Meteo Marine 30 hari (p95=0.95 m, p99=1.07 m). Bukan ambang rob resmi.",
            "source": "Open-Meteo Marine 30 hari (p95/p99)",
            "confidence": "medium",
            "calibrated": True,
            "calibration_type": "model_percentile"
        },
        "water_level": {
            "warning": None,
            "critical": None,
            "basis": "Tidak ada sensor TMA lokal; ambang operasional belum dapat ditetapkan.",
            "source": "Belum tersedia",
            "confidence": "none",
            "calibrated": False
        }
    }
}


def load_thresholds():
    data = DEFAULT_THRESHOLDS
    if os.path.exists(THRESHOLDS_PATH):
        try:
            with open(THRESHOLDS_PATH, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as error:
            print(f"Threshold calibration fallback: {error}")
    for parameter, meta in data.get("parameters", {}).items():
        if parameter in PARAMETERS:
            PARAMETERS[parameter]["warning"] = meta.get("warning")
            PARAMETERS[parameter]["critical"] = meta.get("critical")
            PARAMETERS[parameter]["threshold_basis"] = meta.get("basis")
            PARAMETERS[parameter]["threshold_source"] = meta.get("source")
            PARAMETERS[parameter]["threshold_confidence"] = meta.get("confidence")
            PARAMETERS[parameter]["threshold_calibrated"] = meta.get("calibrated", False)
            PARAMETERS[parameter]["threshold_calibration_type"] = meta.get("calibration_type")
    return data


THRESHOLDS = load_thresholds()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_json_file(filename: str):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(WEBGIS_DIR, "data", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File {filename} not found.")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_db():
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT NOT NULL,
                parameter TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'manual',
                lat REAL,
                lon REAL,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_observations_parameter_time
            ON observations(parameter, recorded_at)
        """)
        connection.commit()


init_db()


def demo_value(parameter: str, moment: datetime) -> float:
    """Deterministic demo signal so the UI can be tested without a sensor feed."""
    epoch = moment.timestamp()
    if parameter == "tide_level":
        value = 1.36 + 0.42 * math.sin(2 * math.pi * epoch / 43200) + 0.08 * math.sin(2 * math.pi * epoch / 21600)
        return round(max(0.2, value), 2)
    if parameter == "water_level":
        value = 44 + 27 * math.sin(2 * math.pi * epoch / 43200 + 0.62) + 9 * math.sin(2 * math.pi * epoch / 10800)
        return round(max(0.0, value), 1)
    value = max(0.0, 6.5 + 11.5 * math.sin(2 * math.pi * epoch / 21600 + 1.15) + 3.2 * math.sin(2 * math.pi * epoch / 3600))
    return round(value, 1)


def classify(parameter: str, value: float) -> str:
    meta = PARAMETERS[parameter]
    warning = meta.get("warning")
    critical = meta.get("critical")
    if warning is None or critical is None:
        return "uncalibrated"
    if value >= critical:
        return "kritis"
    if value >= warning:
        return "waspada"
    return "normal"


def latest_observation(parameter: str):
    with get_db() as connection:
        row = connection.execute(
            "SELECT * FROM observations WHERE parameter = ? ORDER BY recorded_at DESC LIMIT 1",
            (parameter,)
        ).fetchone()
        return dict(row) if row else None


def observation_count() -> int:
    with get_db() as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM observations").fetchone()
        return int(row["total"]) if row else 0


_external_cache = {"fetched_at": 0.0, "data": None, "error": None}


def _fetch_json(url: str, timeout: int = 8):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "SemarangFloodRobGIS/2.0 (+academic project)"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _open_meteo_time(value: str) -> datetime:
    # Open-Meteo returns local time without offset when timezone is requested.
    return datetime.fromisoformat(value).replace(tzinfo=timezone(timedelta(hours=7)))


def get_external_observations():
    """Fetch real model data (rainfall + sea level) from Open-Meteo.

    This is external model data, not a local sensor. It is labelled as such in
    the API response and UI. Cache prevents hammering the public API.
    """
    now_ts = time.time()
    if _external_cache["data"] and now_ts - _external_cache["fetched_at"] < EXTERNAL_TTL_SECONDS:
        return _external_cache["data"]

    try:
        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=-6.958&longitude=110.422"
            "&hourly=precipitation,rain"
            "&timezone=Asia%2FJakarta&past_days=1&forecast_days=2"
        )
        marine_url = (
            "https://marine-api.open-meteo.com/v1/marine"
            "?latitude=-6.958&longitude=110.422"
            "&hourly=sea_level_height_msl,wave_height"
            "&timezone=Asia%2FJakarta&past_days=1&forecast_days=2"
        )
        flood_url = (
            "https://flood-api.open-meteo.com/v1/flood"
            "?latitude=-6.958&longitude=110.422"
            "&daily=river_discharge,river_discharge_mean,river_discharge_max"
            "&timezone=Asia%2FJakarta&forecast_days=7"
        )
        weather = _fetch_json(weather_url)
        marine = _fetch_json(marine_url)
        flood = _fetch_json(flood_url)

        times = weather.get("hourly", {}).get("time", [])
        if not times:
            raise ValueError("Open-Meteo returned no hourly timestamps")

        parsed = [_open_meteo_time(value) for value in times]
        now_local = datetime.now(timezone(timedelta(hours=7))).replace(minute=0, second=0, microsecond=0)
        index = min(range(len(parsed)), key=lambda i: abs((parsed[i] - now_local).total_seconds()))

        rain = weather.get("hourly", {}).get("precipitation", [])
        tide = marine.get("hourly", {}).get("sea_level_height_msl", [])
        waves = marine.get("hourly", {}).get("wave_height", [])

        def series(values):
            if not values:
                return []
            start = max(0, index - 48)
            end = min(len(values), index + 1)
            return [
                {"t": iso(parsed[i]), "v": round(float(values[i]), 3)}
                for i in range(start, end)
                if i < len(values)
            ]

        data = {
            "provider": "Open-Meteo",
            "attribution": "https://open-meteo.com/",
            "fetched_at": iso(utc_now()),
            "status": "connected",
            "note": "Model cuaca/pasang global, bukan sensor lokal.",
            "tide_level": {
                "value": round(float(tide[index]), 2),
                "unit": "m",
                "time": iso(parsed[index]),
                "series": series(tide)
            },
            "rainfall": {
                "value": round(float(rain[index]), 1),
                "unit": "mm/jam",
                "time": iso(parsed[index]),
                "series": series(rain)
            },
            "wave_height": {
                "value": round(float(waves[index]), 2) if waves else None,
                "unit": "m",
                "time": iso(parsed[index])
            }
        }

        daily_times = flood.get("daily", {}).get("time", [])
        daily_discharge = flood.get("daily", {}).get("river_discharge", [])
        daily_max = flood.get("daily", {}).get("river_discharge_max", [])
        if daily_times and daily_discharge:
            local_date = datetime.now(timezone(timedelta(hours=7))).date().isoformat()
            day_index = daily_times.index(local_date) if local_date in daily_times else 0
            start_day = max(0, day_index - 3)
            end_day = min(len(daily_discharge), day_index + 4)
            data["river_discharge"] = {
                "value": round(float(daily_discharge[day_index]), 2),
                "max": round(float(daily_max[day_index]), 2) if day_index < len(daily_max) else None,
                "unit": "m³/s",
                "time": daily_times[day_index],
                "series": [
                    {"t": daily_times[i], "v": round(float(daily_discharge[i]), 2)}
                    for i in range(start_day, end_day)
                ],
                "source": "Open-Meteo Flood API (GloFAS)"
            }
        _external_cache.update({"fetched_at": now_ts, "data": data, "error": None})
        return data
    except Exception as error:
        _external_cache.update({"fetched_at": now_ts, "data": None, "error": str(error)})
        return None


_citizen_cache = {"fetched_at": 0.0, "data": None, "error": None}
PETABENCANA_BBOX = {"min_lon": 110.35, "max_lon": 110.48, "min_lat": -6.99, "max_lat": -6.90}


def get_citizen_reports(days: int = 7):
    """Fetch real crowdsourced flood reports from PetaBencana.id.

    The public API returns TopoJSON point geometries. We filter flood reports
    inside the Semarang Utara bounding box and return GeoJSON for the map/UI.
    """
    now_ts = time.time()
    if _citizen_cache["data"] and now_ts - _citizen_cache["fetched_at"] < CITIZEN_REPORTS_TTL_SECONDS:
        return _citizen_cache["data"]

    try:
        timeperiod = max(3600, min(604800, int(days) * 86400))
        url = f"https://api.petabencana.id/reports?admin=ID-JT&timeperiod={timeperiod}"
        payload = _fetch_json(url)
        geometries = payload.get("result", {}).get("objects", {}).get("output", {}).get("geometries", [])
        features = []
        for geometry in geometries:
            props = geometry.get("properties", {}) or {}
            if props.get("disaster_type") != "flood":
                continue
            coords = geometry.get("coordinates")
            if not coords or len(coords) < 2:
                continue
            lon, lat = float(coords[0]), float(coords[1])
            if not (PETABENCANA_BBOX["min_lon"] <= lon <= PETABENCANA_BBOX["max_lon"] and
                    PETABENCANA_BBOX["min_lat"] <= lat <= PETABENCANA_BBOX["max_lat"]):
                continue
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "pkey": props.get("pkey"),
                    "created_at": props.get("created_at"),
                    "source": props.get("source", "petabencana"),
                    "status": props.get("status", "confirmed"),
                    "text": props.get("text"),
                    "image_url": props.get("image_url"),
                    "report_data": props.get("report_data")
                }
            })

        latest = features[0]["properties"].get("created_at") if features else None
        data = {
            "status": "connected",
            "provider": "PetaBencana.id",
            "attribution": "https://petabencana.id/",
            "message": "Laporan urun-daya warga; bukan sensor resmi.",
            "period_days": days,
            "count": len(features),
            "latest": latest,
            "bbox": PETABENCANA_BBOX,
            "fetched_at": iso(utc_now()),
            "features": {
                "type": "FeatureCollection",
                "features": features
            }
        }
        _citizen_cache.update({"fetched_at": now_ts, "data": data, "error": None})
        return data
    except Exception as error:
        data = {
            "status": "unavailable",
            "provider": "PetaBencana.id",
            "attribution": "https://petabencana.id/",
            "message": "Laporan warga tidak dapat diambil saat ini.",
            "period_days": days,
            "count": 0,
            "latest": None,
            "bbox": PETABENCANA_BBOX,
            "fetched_at": iso(utc_now()),
            "error": str(error),
            "features": {"type": "FeatureCollection", "features": []}
        }
        _citizen_cache.update({"fetched_at": now_ts, "data": data, "error": str(error)})
        return data


def build_current_condition(readings, citizen, external=None):
    """Derive a realtime condition from real/external sources only.

    Simulated water level is deliberately excluded from the event status.
    """
    severity = 0
    drivers = []
    tide = readings.get("tide_level", {})
    rain = readings.get("rainfall", {})
    water = readings.get("water_level", {})

    if tide.get("source_type") in ("external", "observation"):
        value = float(tide.get("value") or 0)
        warning, critical = tide.get("warning"), tide.get("critical")
        if critical is not None and value >= critical:
            severity = max(severity, 2)
            drivers.append("pasang laut kritis")
        elif warning is not None and value >= warning:
            severity = max(severity, 1)
            drivers.append("pasang laut waspada")

    if rain.get("source_type") in ("external", "observation"):
        value = float(rain.get("value") or 0)
        warning, critical = rain.get("warning"), rain.get("critical")
        if critical is not None and value >= critical:
            severity = max(severity, 2)
            drivers.append("curah hujan kritis")
        elif warning is not None and value >= warning:
            severity = max(severity, 1)
            drivers.append("curah hujan waspada")

    if water.get("source_type") == "observation":
        value = float(water.get("value") or 0)
        warning, critical = water.get("warning"), water.get("critical")
        if critical is not None and value >= critical:
            severity = max(severity, 2)
            drivers.append("muka air sungai kritis")
        elif warning is not None and value >= warning:
            severity = max(severity, 1)
            drivers.append("muka air sungai waspada")

    report_count = int((citizen or {}).get("count") or 0)
    if report_count > 0:
        severity = max(severity, 1)
        drivers.append(f"{report_count} laporan warga")

    has_external_model = tide.get("source_type") in ("external", "observation") or rain.get("source_type") in ("external", "observation")
    if not has_external_model and report_count == 0:
        return {
            "level": "unknown",
            "headline": "Status realtime belum tersedia",
            "detail": "Sumber eksternal belum terhubung. Data tematik tetap snapshot analisis.",
            "drivers": [],
            "updated_at": iso(utc_now())
        }

    if severity >= 2:
        level = "kritis"
        headline = "Potensi genangan tinggi — pantau kondisi"
        detail = "Ambang model terlampaui. Ini bukan peringatan resmi; verifikasi ke BPBD/BMKG."
    elif severity == 1:
        level = "waspada"
        headline = "Waspada potensi peningkatan air"
        detail = "Salah satu indikator mendekati/melewati ambang. Pantau pembaruan berkala."
    else:
        level = "normal"
        headline = "Tidak ada indikasi banjir/rob saat ini"
        detail = "Pasang laut dan curah hujan di bawah ambang indikatif; tidak ada laporan warga PetaBencana dalam 7 hari. Muka air sungai masih simulasi; debit GloFAS hanya indikator pendukung."

    return {
        "level": level,
        "headline": headline,
        "detail": detail,
        "drivers": drivers,
        "updated_at": iso(utc_now()),
        "based_on": {
            "tide_level": tide.get("value"),
            "rainfall": rain.get("value"),
            "river_discharge": (external or {}).get("river_discharge", {}).get("value") if external else None,
            "citizen_reports": report_count
        },
        "note": "Status indikatif dari model Open-Meteo dan laporan PetaBencana. Hujan memakai kategori BMKG; pasang indikatif; TMA sungai belum terkalibrasi. Bukan peringatan resmi."
    }


def build_data_health(readings, external, citizen, mode):
    """Summarise freshness, provenance, and missing sources for the UI."""
    external_ok = bool(external and external.get("status") == "connected")
    citizen_ok = bool(citizen and citizen.get("status") == "connected")
    simulation_parameters = [
        reading.get("label", key) for key, reading in readings.items()
        if reading.get("source_type") == "simulation"
    ]
    stale_parameters = [
        reading.get("label", key) for key, reading in readings.items()
        if reading.get("source_type") == "observation" and not reading.get("is_live")
    ]
    uncalibrated_parameters = [
        reading.get("label", key) for key, reading in readings.items()
        if reading.get("status") == "uncalibrated"
    ]
    warnings = []
    if uncalibrated_parameters:
        warnings.append("Parameter belum terkalibrasi: " + ", ".join(uncalibrated_parameters))
    if not external_ok:
        warnings.append("Open-Meteo tidak terhubung")
    if not citizen_ok:
        warnings.append("PetaBencana tidak terhubung")
    if simulation_parameters:
        warnings.append("Parameter simulasi: " + ", ".join(simulation_parameters))
    if observation_count() == 0:
        warnings.append("Belum ada observasi lapangan tersimpan")
    if not external_ok and not citizen_ok:
        overall = "offline"
    elif warnings:
        overall = "degraded"
    else:
        overall = "ok"

    return {
        "overall": overall,
        "mode": mode,
        "checked_at": iso(utc_now()),
        "open_meteo": {
            "status": "ok" if external_ok else "unavailable",
            "fetched_at": external.get("fetched_at") if external else None,
            "provider": external.get("provider") if external else None
        },
        "petabencana": {
            "status": "ok" if citizen_ok else "unavailable",
            "fetched_at": citizen.get("fetched_at") if citizen else None,
            "count": citizen.get("count", 0) if citizen else 0,
            "period_days": citizen.get("period_days", 7) if citizen else 7
        },
        "local_sensor": {
            "water_level": "observation" if readings.get("water_level", {}).get("source_type") == "observation" else "missing"
        },
        "observation_count": observation_count(),
        "simulation_parameters": simulation_parameters,
        "stale_parameters": stale_parameters,
        "uncalibrated_parameters": uncalibrated_parameters,
        "warnings": warnings
    }


def build_status():
    generated_at = utc_now()
    external = get_external_observations()
    citizen = get_citizen_reports(7)
    readings = {}
    live_real = 0
    live_external = 0
    stale_real = 0
    simulation = 0
    last_candidates = []

    for parameter, meta in PARAMETERS.items():
        real = latest_observation(parameter)
        reading = {
            "parameter": parameter,
            "label": meta["label"],
            "unit": meta["unit"],
            "station": meta["station"],
            "warning": meta["warning"],
            "critical": meta["critical"],
            "decimals": meta["decimals"],
            "source": "simulasi",
            "source_type": "simulation",
            "provider": "Simulasi",
            "is_live": False,
            "recorded_at": iso(generated_at),
            "age_seconds": 0,
            "confidence": "low",
            "confidence_label": "Rendah"
        }
        used = None

        if real:
            recorded = parse_iso(real["recorded_at"])
            age_seconds = max(0, (generated_at - recorded).total_seconds())
            if age_seconds <= REALTIME_WINDOW_MINUTES * 60:
                used = "observation"
                reading.update({
                    "value": round(float(real["value"]), meta["decimals"]),
                    "station": real["station_id"],
                    "source": "observasi lapangan",
                    "source_type": "observation",
                    "provider": "Observasi lapangan",
                    "is_live": True,
                    "recorded_at": real["recorded_at"],
                    "age_seconds": int(age_seconds)
                })
                live_real += 1
                last_candidates.append(real["recorded_at"])

        if used is None and external and parameter in external:
            ext = external[parameter]
            used = "external"
            recorded = parse_iso(ext["time"])
            age_seconds = max(0, (generated_at - recorded).total_seconds())
            reading.update({
                "value": ext["value"],
                "station": "Open-Meteo Marine · perairan Semarang" if parameter == "tide_level" else "Open-Meteo Forecast · Semarang Utara",
                "source": "Open-Meteo (model cuaca/pasang)",
                "source_type": "external",
                "provider": "Open-Meteo",
                "is_live": True,
                "recorded_at": ext["time"],
                "age_seconds": int(age_seconds)
            })
            live_external += 1
            last_candidates.append(ext["time"])

        if used is None and real:
            recorded = parse_iso(real["recorded_at"])
            age_seconds = max(0, (generated_at - recorded).total_seconds())
            used = "stale"
            reading.update({
                "value": round(float(real["value"]), meta["decimals"]),
                "station": real["station_id"],
                "source": "observasi terakhir",
                "source_type": "observation",
                "provider": "Observasi lapangan (terakhir)",
                "is_live": False,
                "recorded_at": real["recorded_at"],
                "age_seconds": int(age_seconds)
            })
            stale_real += 1
            last_candidates.append(real["recorded_at"])

        if used is None:
            reading.update({
                "value": demo_value(parameter, generated_at),
                "station": "Simulasi model · belum ada sensor",
                "source": "simulasi",
                "source_type": "simulation",
                "provider": "Simulasi",
                "is_live": False,
                "recorded_at": iso(generated_at),
                "age_seconds": 0
            })
            simulation += 1

        if reading["source_type"] == "observation":
            reading["confidence"] = "high" if reading["is_live"] else "low"
        elif reading["source_type"] == "external":
            reading["confidence"] = "medium"
        else:
            reading["confidence"] = "low"
        reading["confidence_label"] = {"high": "Tinggi", "medium": "Sedang", "low": "Rendah"}[reading["confidence"]]
        reading["status"] = "simulation" if reading["source_type"] == "simulation" else classify(parameter, reading["value"])
        readings[parameter] = reading

    if live_real == len(PARAMETERS):
        mode = "live"
        note = "Semua parameter berasal dari observasi lapangan dalam 30 menit terakhir."
    elif live_real > 0 or live_external > 0:
        mode = "hybrid"
        if live_external and simulation and not live_real:
            note = "Muka air laut/curah hujan berasal dari model Open-Meteo; parameter yang belum memiliki sensor masih berupa simulasi."
        elif live_external and live_real:
            note = "Sebagian parameter berasal dari observasi lapangan dan Open-Meteo; parameter lain masih simulasi."
        elif live_real:
            note = "Sebagian parameter berasal dari observasi lapangan; parameter lain masih simulasi."
        else:
            note = "Sebagian parameter berasal dari sumber eksternal; parameter lain masih simulasi."
    elif stale_real > 0:
        mode = "stale"
        note = "Observasi terakhir lebih dari 30 menit lalu. Nilai ditampilkan sebagai data terakhir, bukan realtime."
    else:
        mode = "demo"
        note = "Belum ada observasi lapangan dan API eksternal tidak tersedia. Nilai ditampilkan sebagai simulasi untuk demonstrasi antarmuka."

    providers = []
    if live_real or stale_real:
        providers.append("observasi lapangan")
    if live_external:
        providers.append("Open-Meteo")
    if simulation:
        providers.append("simulasi")
    if citizen and citizen.get("status") == "connected":
        providers.append("PetaBencana")

    return {
        "mode": mode,
        "is_live": mode == "live",
        "generated_at": iso(generated_at),
        "last_update": max(last_candidates) if (live_real or stale_real) else iso(generated_at),
        "refresh_interval_seconds": REFRESH_INTERVAL_SECONDS,
        "realtime_window_minutes": REALTIME_WINDOW_MINUTES,
        "source": " + ".join(providers) if providers else "tidak tersedia",
        "note": note,
        "observation_count": observation_count(),
        "readings": readings,
        "external_data": {
            "provider": external.get("provider") if external else None,
            "status": external.get("status") if external else "unavailable",
            "fetched_at": external.get("fetched_at") if external else None,
            "attribution": "https://open-meteo.com/",
            "note": "Model cuaca/pasang/debit global, bukan sensor lokal.",
            "river_discharge": external.get("river_discharge") if external else None,
            "wave_height": external.get("wave_height") if external else None,
            "citizen_reports": citizen
        },
        "data_health": build_data_health(readings, external, citizen, mode),
        "current_condition": build_current_condition(readings, citizen, external),
        "thresholds": {
            "version": THRESHOLDS.get("version"),
            "reviewed_at": THRESHOLDS.get("reviewed_at"),
            "method": THRESHOLDS.get("method"),
            "parameters": {
                parameter: {
                    "label": meta["label"],
                    "warning": meta["warning"],
                    "critical": meta["critical"],
                    "unit": meta["unit"],
                    "basis": meta.get("threshold_basis"),
                    "source": meta.get("threshold_source"),
                    "confidence": meta.get("threshold_confidence"),
                    "calibrated": meta.get("threshold_calibrated", False),
                    "calibration_type": meta.get("threshold_calibration_type")
                }
                for parameter, meta in PARAMETERS.items()
            }
        }
    }


def build_history(hours: int = 24):
    external = get_external_observations()
    end = utc_now()
    start = end - timedelta(hours=hours)
    series = {}
    sources = {}
    observation_series = 0
    external_series = 0

    for parameter, meta in PARAMETERS.items():
        with get_db() as connection:
            rows = connection.execute(
                "SELECT recorded_at, value FROM observations "
                "WHERE parameter = ? AND recorded_at >= ? "
                "ORDER BY recorded_at ASC",
                (parameter, iso(start))
            ).fetchall()

        if rows:
            observation_series += 1
            sources[parameter] = "observation"
            series[parameter] = [
                {"t": row["recorded_at"], "v": round(float(row["value"]), meta["decimals"])}
                for row in rows
            ]
        elif external and parameter in external and external[parameter].get("series"):
            external_series += 1
            sources[parameter] = "external"
            series[parameter] = [
                point for point in external[parameter]["series"]
                if parse_iso(point["t"]) >= start
            ]
        else:
            sources[parameter] = "simulation"
            points = []
            steps = max(8, int(hours * 2))
            for index in range(steps + 1):
                moment = start + timedelta(hours=hours) * (index / steps)
                points.append({"t": iso(moment), "v": demo_value(parameter, moment)})
            series[parameter] = points

    if observation_series == len(PARAMETERS):
        mode = "live"
    elif observation_series or external_series:
        mode = "hybrid"
    else:
        mode = "demo"

    return {
        "mode": mode,
        "hours": hours,
        "generated_at": iso(end),
        "sources": sources,
        "series": series
    }


class ObservationIn(BaseModel):
    station_id: str = Field(min_length=1, max_length=120)
    parameter: Literal["tide_level", "water_level", "rainfall"]
    value: float
    unit: Optional[str] = None
    recorded_at: Optional[datetime] = None
    source: str = Field(default="field", max_length=80)
    lat: Optional[float] = None
    lon: Optional[float] = None


@app.get("/api")
def api_root():
    return {
        "system": "SEMARANG FLOOD & ROB GIS MONITORING API",
        "version": "2.0.0",
        "study_area": "Kecamatan Semarang Utara, Kota Semarang",
        "status": "operational",
        "monitoring": {
            "mode": "near-realtime polling",
            "refresh_interval_seconds": REFRESH_INTERVAL_SECONDS,
            "realtime_window_minutes": REALTIME_WINDOW_MINUTES,
            "endpoints": {
                "status": "/api/monitoring/status",
                "history": "/api/monitoring/history?hours=24",
                "stations": "/api/monitoring/stations",
                "observations": "/api/monitoring/observations",
                "ingest": "POST /api/monitoring/observations",
                "external": "/api/monitoring/external",
                "reports": "/api/monitoring/reports?days=7"
            }
        },
        "endpoints": {
            "kelurahan": "/api/kelurahan",
            "sungai": "/api/sungai",
            "genangan": "/api/genangan",
            "permukiman": "/api/permukiman",
            "survei": "/api/survei",
            "buffer": "/api/buffer",
            "analisis": "/api/analisis",
            "statistik": "/api/statistik",
            "kelurahan_detail": "/api/kelurahan/{id}"
        },
        "crs": "EPSG:4326 (WGS 84)"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "time": iso(utc_now()),
        "database": os.path.basename(DB_PATH),
        "observations": observation_count()
    }


@app.get("/api/monitoring/thresholds")
def monitoring_thresholds():
    return {
        "version": THRESHOLDS.get("version"),
        "reviewed_at": THRESHOLDS.get("reviewed_at"),
        "method": THRESHOLDS.get("method"),
        "parameters": {
            parameter: {
                "label": meta["label"],
                "unit": meta["unit"],
                "warning": meta["warning"],
                "critical": meta["critical"],
                "basis": meta.get("threshold_basis"),
                "source": meta.get("threshold_source"),
                "confidence": meta.get("threshold_confidence"),
                "calibrated": meta.get("threshold_calibrated", False),
                "calibration_type": meta.get("threshold_calibration_type")
            }
            for parameter, meta in PARAMETERS.items()
        }
    }


@app.get("/api/monitoring/status")
def monitoring_status():
    return build_status()


@app.get("/api/monitoring/history")
def monitoring_history(hours: int = Query(24, ge=1, le=168)):
    return build_history(hours)


@app.get("/api/monitoring/stations")
def monitoring_stations():
    return {
        "stations": [
            {
                "station_id": meta["station"],
                "parameter": parameter,
                "label": meta["label"],
                "unit": meta["unit"],
                "warning": meta["warning"],
                "critical": meta["critical"],
                "basis": meta.get("threshold_basis"),
                "source": meta.get("threshold_source"),
                "confidence": meta.get("threshold_confidence"),
                "calibrated": meta.get("threshold_calibrated", False),
                "calibration_type": meta.get("threshold_calibration_type")
            }
            for parameter, meta in PARAMETERS.items()
        ]
    }


@app.get("/api/monitoring/external")
def monitoring_external():
    data = get_external_observations()
    if not data:
        raise HTTPException(
            status_code=503,
            detail="Open-Meteo tidak dapat diakses. Gunakan observasi lapangan atau mode simulasi."
        )
    return data


@app.get("/api/monitoring/reports")
def monitoring_reports(days: int = Query(7, ge=1, le=7)):
    return get_citizen_reports(days)


@app.get("/api/monitoring/observations")
def monitoring_observations(limit: int = Query(50, ge=1, le=500)):
    with get_db() as connection:
        rows = connection.execute(
            "SELECT * FROM observations ORDER BY recorded_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return {"count": len(rows), "observations": [dict(row) for row in rows]}


@app.post("/api/monitoring/observations", status_code=201)
def create_observation(payload: ObservationIn, request: Request, x_api_key: Optional[str] = Header(default=None)):
    enforce_rate_limit(request)
    if API_KEY and not secrets.compare_digest(x_api_key or "", API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key.")

    meta = PARAMETERS[payload.parameter]
    recorded_at = payload.recorded_at or utc_now()
    unit = payload.unit or meta["unit"]

    with get_db() as connection:
        cursor = connection.execute(
            "INSERT INTO observations "
            "(station_id, parameter, value, unit, recorded_at, source, lat, lon, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                payload.station_id,
                payload.parameter,
                payload.value,
                unit,
                iso(recorded_at),
                payload.source,
                payload.lat,
                payload.lon,
                iso(utc_now())
            )
        )
        connection.commit()
        observation_id = cursor.lastrowid

    return {
        "status": "accepted",
        "id": observation_id,
        "parameter": payload.parameter,
        "value": payload.value,
        "unit": unit,
        "recorded_at": iso(recorded_at),
        "source": payload.source,
        "message": "Observation stored. The dashboard will reflect it on the next poll."
    }


@app.get("/api/kelurahan")
def get_kelurahan():
    return load_json_file("batas_kelurahan.geojson")


@app.get("/api/sungai")
def get_sungai():
    return load_json_file("sungai.geojson")


@app.get("/api/genangan")
def get_genangan():
    return load_json_file("area_genangan.geojson")


@app.get("/api/permukiman")
def get_permukiman():
    return load_json_file("permukiman.geojson")


@app.get("/api/survei")
def get_survei():
    return load_json_file("titik_survei.geojson")


@app.get("/api/buffer")
def get_buffer():
    return load_json_file("buffer_sungai.geojson")


@app.get("/api/analisis")
def get_analisis():
    return load_json_file("permukiman_terdampak.geojson")


@app.get("/api/statistik")
def get_statistik():
    return load_json_file("statistik.json")


@app.get("/api/kelurahan/{kel_id}")
def get_kelurahan_by_id(kel_id: str):
    stats = load_json_file("statistik.json")
    rankings = stats.get("kelurahan_rankings", [])
    kel_id_upper = kel_id.upper()
    for item in rankings:
        if item.get("id_kel") == kel_id_upper or item.get("nama_kel").upper() == kel_id_upper:
            return item
    raise HTTPException(status_code=404, detail=f"Kelurahan '{kel_id}' not found.")


# Mount webgis folder for serving WebGIS static web application
if os.path.exists(WEBGIS_DIR):
    app.mount("/", StaticFiles(directory=WEBGIS_DIR, html=True), name="webgis")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
