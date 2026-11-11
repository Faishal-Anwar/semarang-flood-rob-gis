#!/usr/bin/env python3
"""Recompute the settlement exposure layer and statistics from the actual geometries.

Why this exists:
The previous `permukiman_terdampak.geojson` and `statistik.json` contained
numbers that were not reproducible from the intersection of the settlement and
flood polygons. This script recalculates the overlay in EPSG:32749 and rewrites
the GeoJSON, statistics, analysis exports and GPKG layers so the website,
dashboard and documents share one source of truth.

Run from the project root:
    python scripts/recompute_analysis.py
"""
from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[1]
WEB_DATA = ROOT / "webgis" / "data"
BACKEND_DATA = ROOT / "backend" / "data"
ANALYSIS_DIR = ROOT / "05_ANALISIS"
GPKG_PATHS = [
    ROOT / "database" / "Database_SIG.gpkg",
    ROOT / "04_DATABASE" / "Database_SIG.gpkg",
    ROOT / "webgis" / "downloads" / "Database_SIG.gpkg",
]

TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32749", always_xy=True)


def load(name: str) -> dict[str, Any]:
    return json.loads((WEB_DATA / name).read_text(encoding="utf-8"))


def area_ha(geom) -> float:
    if geom.is_empty:
        return 0.0
    return transform(TO_UTM.transform, geom).area / 10000.0


def clean_geometry(geom):
    geom = make_valid(geom)
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    polygons = [part for part in getattr(geom, "geoms", []) if part.geom_type in ("Polygon", "MultiPolygon")]
    if not polygons:
        return geom
    return unary_union(polygons)


def round_coords(value, digits: int = 6):
    if isinstance(value, float):
        return round(value, digits)
    if isinstance(value, list):
        return [round_coords(item, digits) for item in value]
    if isinstance(value, tuple):
        return [round_coords(item, digits) for item in value]
    if isinstance(value, dict):
        return {key: round_coords(item, digits) for key, item in value.items()}
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dominant_category(settlement_geom, flood_features):
    best = None
    for feature in flood_features:
        flood_geom = shape(feature["geometry"])
        overlap = area_ha(settlement_geom.intersection(flood_geom))
        if overlap <= 0:
            continue
        if best is None or overlap > best[0]:
            best = (overlap, feature["properties"])
    return best


def risk_status(ratio: float, settlement_ha: float) -> tuple[str, str]:
    if settlement_ha <= 0:
        return "Data permukiman belum tersedia", "Data Belum Tersedia"
    if ratio >= 90:
        return "Sangat Kritis (Prioritas 1)", "Sangat Kritis"
    if ratio >= 70:
        return "Kritis (Prioritas 2)", "Kritis"
    if ratio >= 40:
        return "Waspada (Prioritas 3)", "Waspada"
    if ratio > 0:
        return "Terkendali / Rendah", "Terkendali"
    return "Di Luar Zona Rawan", "Di Luar Zona Rawan"


def main() -> None:
    kelurahan_data = load("batas_kelurahan.geojson")
    settlement_data = load("permukiman.geojson")
    flood_data = load("area_genangan.geojson")
    buffer_data = load("buffer_sungai.geojson")
    survey_data = load("titik_survei.geojson")
    old_stats = load("statistik.json")

    old_by_name = {item["nama_kel"]: item for item in old_stats.get("kelurahan_rankings", [])}
    old_profile = {}
    profile_gpkg = ROOT / "database" / "Database_SIG.gpkg"
    if profile_gpkg.exists():
        try:
            connection = sqlite3.connect(profile_gpkg)
            connection.row_factory = sqlite3.Row
            for row in connection.execute("SELECT * FROM Tabel_Kelurahan_Profil"):
                old_profile[row["nama_kel"]] = dict(row)
            connection.close()
        except Exception:
            old_profile = {}

    settlement_features = settlement_data["features"]
    flood_features = flood_data["features"]
    flood_union = unary_union([shape(feature["geometry"]) for feature in flood_features])
    buffer_union = unary_union([shape(feature["geometry"]) for feature in buffer_data["features"]])
    settlement_union = unary_union([shape(feature["geometry"]) for feature in settlement_features])
    impacted_union = settlement_union.intersection(flood_union)

    # ------------------------------------------------------------------
    # 1. Rebuild settlement exposure polygons from the actual overlay
    # ------------------------------------------------------------------
    impacted_features = []
    for index, feature in enumerate(settlement_features, start=1):
        settlement_geom = shape(feature["geometry"])
        overlap = clean_geometry(settlement_geom.intersection(flood_union))
        overlap_area = area_ha(overlap)
        if overlap_area <= 0.0001:
            continue

        props = feature["properties"]
        total_area = area_ha(settlement_geom)
        dominant = dominant_category(settlement_geom, flood_features)
        hazard = dominant[1] if dominant else {}

        impacted_features.append({
            "type": "Feature",
            "geometry": {
                "type": overlap.geom_type,
                "coordinates": round_coords(mapping(overlap)["coordinates"])
            },
            "properties": {
                "id_terdampak": len(impacted_features) + 1,
                "id_perm": props.get("id_perm", index),
                "nama_kaw": props.get("nama_kaw", f"Kawasan {index}"),
                "kelurahan": props.get("kelurahan", "-"),
                "tipe_huni": props.get("tipe_huni", "-"),
                "luas_total_ha": round(total_area, 2),
                "luas_terpapar_m2": round(overlap_area * 10000, 0),
                "luas_terpapar_ha": round(overlap_area, 2),
                "pct_terpapar": round(overlap_area / total_area * 100, 2) if total_area else 0,
                "jenis_bahaya": hazard.get("jenis_bencana", "Genangan rob"),
                "tingkat_risiko": hazard.get("tingkat_bahaya", "Sedang"),
                "rekomendasi": (
                    "Prioritas perlindungan, retrofit drainase, dan jalur evakuasi"
                    if hazard.get("tingkat_bahaya") == "Sangat Tinggi"
                    else "Perkuat drainase/polder dan sistem peringatan dini"
                    if hazard.get("tingkat_bahaya") == "Tinggi"
                    else "Normalisasi saluran dan pemantauan berkala"
                ),
                "sumber": "Overlay Intersect Permukiman x Area Genangan BPBD (recomputed)"
            }
        })

    impacted_collection = {"type": "FeatureCollection", "features": impacted_features}
    total_impacted = area_ha(impacted_union)
    total_settlement = area_ha(settlement_union)
    total_flood = area_ha(flood_union)
    total_buffer = area_ha(buffer_union)

    # ------------------------------------------------------------------
    # 2. Hazard breakdown from actual intersections
    # ------------------------------------------------------------------
    category_keys = {
        "Sangat Tinggi": "Sangat Tinggi (Bencana Ganda: Rob & Kali)",
        "Tinggi": "Tinggi (Rob Pasang Laut Pesisir)",
        "Sedang": "Sedang (Limpasan Saluran Drainase)"
    }
    hazard_breakdown: dict[str, float] = {}
    for category, label in category_keys.items():
        geoms = [shape(feature["geometry"]) for feature in flood_features if feature["properties"].get("tingkat_bahaya") == category]
        value = area_ha(unary_union(geoms).intersection(settlement_union)) if geoms else 0.0
        hazard_breakdown[label] = round(value, 2)
    hazard_breakdown["Di Luar Zona Rawan (BPBD)"] = round(total_settlement - total_impacted, 2)

    # ------------------------------------------------------------------
    # 3. Per-kelurahan statistics from geometry
    # ------------------------------------------------------------------
    rankings = []
    profile_rows = []
    for feature in kelurahan_data["features"]:
        props = feature["properties"]
        name = props.get("nama_kel", "-")
        kel_geom = shape(feature["geometry"])
        settlement_in_kel = settlement_union.intersection(kel_geom)
        impacted_in_kel = impacted_union.intersection(kel_geom)
        settlement_ha = area_ha(settlement_in_kel)
        impacted_ha = area_ha(impacted_in_kel)
        # Remove sub-centimetre slivers caused by boundary rounding.
        if settlement_ha < 0.01:
            settlement_ha = 0.0
            impacted_ha = 0.0
        if impacted_ha < 0.01:
            impacted_ha = 0.0
        ratio = (impacted_ha / settlement_ha * 100) if settlement_ha > 0 else 0.0
        old = old_by_name.get(name, {})
        status_long, status_short = risk_status(ratio, settlement_ha)

        point_count = sum(
            1 for point in survey_data["features"]
            if shape(point["geometry"]).intersects(kel_geom)
        )

        item = {
            "rank": 0,
            "id_kel": old.get("id_kel", props.get("id_kel", "-")),
            "nama_kel": name,
            "luas_kelurahan_ha": round(area_ha(kel_geom), 2),
            "luas_permukiman_ha": round(settlement_ha, 2),
            "luas_terpapar_ha": round(impacted_ha, 2),
            "rasio_persen": round(ratio, 2),
            "populasi": old.get("populasi", props.get("populasi", 0)),
            "kepadatan_jiwa_ha": old.get("kepadatan_jiwa_ha", props.get("kepadatan", 0)),
            "tingkat_kerentanan": status_long,
            "polder_pompa": old.get("polder_pompa", "-"),
            "pusat_koordinat": old.get("pusat_koordinat", [110.422, -6.958]),
            "status_kerentanan": status_short,
            "jumlah_titik_survei": point_count
        }
        rankings.append(item)
        profile_rows.append({
            "id_kel": item["id_kel"],
            "nama_kel": name,
            "jumlah_rw": old_profile.get(name, {}).get("jumlah_rw", props.get("jumlah_rw", 0)),
            "jumlah_rt": old_profile.get(name, {}).get("jumlah_rt", props.get("jumlah_rt", 0)),
            "populasi_jiwa": item["populasi"],
            "luas_kelurahan_ha": item["luas_kelurahan_ha"],
            "luas_permukiman_ha": item["luas_permukiman_ha"],
            "luas_terpapar_ha": item["luas_terpapar_ha"],
            "persentase_terpapar_pct": item["rasio_persen"],
            "jumlah_titik_survei": point_count,
            "status_kerentanan": status_short
        })

    rankings.sort(
        key=lambda item: (
            1 if item["luas_permukiman_ha"] > 0 else 0,
            item["rasio_persen"],
            item["luas_terpapar_ha"]
        ),
        reverse=True
    )
    for index, item in enumerate(rankings, start=1):
        item["rank"] = index

    # ------------------------------------------------------------------
    # 4. Survey validation against the actual flood geometry
    # ------------------------------------------------------------------
    heights = [point["properties"].get("tinggi_genangan_cm", 0) or 0 for point in survey_data["features"]]
    above_40 = [point for point in survey_data["features"] if (point["properties"].get("tinggi_genangan_cm", 0) or 0) > 40]
    above_40_in_flood = sum(
        1 for point in above_40
        if shape(point["geometry"]).intersects(flood_union)
    )
    survey_validation = {
        "average_inundation_cm": round(sum(heights) / len(heights), 1),
        "points_above_40cm": len(above_40),
        "points_above_40cm_inside_flood_polygon": above_40_in_flood,
        "points_above_40cm_outside_flood_polygon": len(above_40) - above_40_in_flood,
        "note": "Sebagian titik >40 cm berada di luar poligon genangan BPBD; batas model perlu validasi lapangan."
    }

    # ------------------------------------------------------------------
    # 5. Build the corrected statistics document
    # ------------------------------------------------------------------
    buffer_settlement = area_ha(settlement_union.intersection(buffer_union))
    stats = {
        "project_info": {
            **old_stats.get("project_info", {}),
            "analysis_version": "2.1-recomputed",
            "analysis_method": "Overlay intersect geometri pada EPSG:32749"
        },
        "kpi_summary": {
            **old_stats.get("kpi_summary", {}),
            "total_kecamatan_area_ha": round(area_ha(unary_union([shape(f["geometry"]) for f in kelurahan_data["features"]])), 2),
            "total_settlement_area_ha": round(total_settlement, 2),
            "total_hazard_flood_area_ha": round(total_flood, 2),
            "total_impacted_settlement_ha": round(total_impacted, 2),
            "impact_percentage": round(total_impacted / total_settlement * 100, 2) if total_settlement else 0,
            "river_buffer_200m_total_ha": round(total_buffer, 2),
            "settlement_in_buffer_200m_ha": round(buffer_settlement, 2),
            "settlement_in_buffer_200m_pct": round(buffer_settlement / total_settlement * 100, 2) if total_settlement else 0,
            "average_survey_height_cm": survey_validation["average_inundation_cm"]
        },
        "kelurahan_rankings": rankings,
        "hazard_breakdown_ha": hazard_breakdown,
        "buffer_analysis": {
            "zone_100m_ha": next((f["properties"]["luas_ha"] for f in buffer_data["features"] if f["properties"]["radius_m"] == 100), 0),
            "zone_200m_ha": next((f["properties"]["luas_ha"] for f in buffer_data["features"] if f["properties"]["radius_m"] == 200), 0),
            "total_buffer_ha": round(total_buffer, 2),
            "pct_of_subdistrict": round(total_buffer / area_ha(unary_union([shape(f["geometry"]) for f in kelurahan_data["features"]])) * 100, 2),
            "settlement_inside_buffer_ha": round(buffer_settlement, 2),
            "pct_of_settlement": round(buffer_settlement / total_settlement * 100, 2) if total_settlement else 0
        },
        "survey_validation": survey_validation,
        "metadata": {
            "analysis_snapshot": "2026-04",
            "version": "2026.11-audit",
            "hazard_source": "BPBD Kota Semarang / InaRISK",
            "hazard_layer": "Poligon zona rawan rob/banjir (5 poligon)",
            "hazard_note": "Poligon hazard statis; bukan luas genangan atau kejadian aktual.",
            "crs_analysis": "EPSG:32749 (UTM 49S)",
            "crs_web": "EPSG:4326 (WGS 84)",
            "method": "Overlay intersect permukiman x zona rawan; denominator luas permukiman 171,68 Ha",
            "denominator_ha": 171.68
        },
        "analysis_metadata": {
            "recomputed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source_files": [
                "batas_kelurahan.geojson",
                "permukiman.geojson",
                "area_genangan.geojson",
                "buffer_sungai.geojson",
                "titik_survei.geojson"
            ],
            "method": "Intersect geometri permukiman dengan area genangan, buffer, dan batas kelurahan; luas dihitung pada EPSG:32749.",
            "note": "Nilai menggantikan statistik lama yang tidak konsisten dengan geometri. Data tematik adalah snapshot analisis, bukan sensor realtime."
        }
    }

    # ------------------------------------------------------------------
    # 6. Write web/backend data, analysis exports and GPKG copies
    # ------------------------------------------------------------------
    for directory in (WEB_DATA, BACKEND_DATA):
        write_json(directory / "statistik.json", stats)
        write_json(directory / "permukiman_terdampak.geojson", impacted_collection)

    analysis_geojson = ANALYSIS_DIR / "Permukiman_Terdampak" / "Permukiman_Terdampak.geojson"
    analysis_geojson.parent.mkdir(parents=True, exist_ok=True)
    write_json(analysis_geojson, impacted_collection)

    csv_path = ANALYSIS_DIR / "Statistik" / "Tabel_Statistik_Keterpaparan_Kelurahan.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(profile_rows[0].keys()))
        writer.writeheader()
        writer.writerows(profile_rows)

    # Update the non-spatial profile table inside every GeoPackage copy.
    for gpkg in GPKG_PATHS:
        if not gpkg.exists():
            continue
        connection = sqlite3.connect(gpkg)
        try:
            connection.execute("DELETE FROM Tabel_Kelurahan_Profil")
            connection.executemany(
                "INSERT INTO Tabel_Kelurahan_Profil "
                "(id_kel, nama_kel, jumlah_rw, jumlah_rt, populasi_jiwa, luas_kelurahan_ha, "
                "luas_permukiman_ha, luas_terpapar_ha, persentase_terpapar_pct, "
                "jumlah_titik_survei, status_kerentanan) "
                "VALUES (:id_kel, :nama_kel, :jumlah_rw, :jumlah_rt, :populasi_jiwa, :luas_kelurahan_ha, "
                ":luas_permukiman_ha, :luas_terpapar_ha, :persentase_terpapar_pct, "
                ":jumlah_titik_survei, :status_kerentanan)",
                profile_rows
            )
            connection.commit()
        finally:
            connection.close()

    # Update the spatial layer using geopandas/pyogrio when available.
    try:
        import geopandas as gpd
        gdf = gpd.GeoDataFrame.from_features(impacted_features, crs="EPSG:4326").to_crs("EPSG:32749")
        for gpkg in GPKG_PATHS:
            if gpkg.exists():
                gdf.to_file(gpkg, layer="Permukiman_Terdampak", driver="GPKG")
    except Exception as error:  # pragma: no cover - optional dependency
        print(f"[warn] GPKG spatial layer not updated: {error}")

    print(json.dumps({
        "total_settlement_ha": round(total_settlement, 2),
        "total_impacted_ha": round(total_impacted, 2),
        "impact_percentage": round(total_impacted / total_settlement * 100, 2),
        "hazard_breakdown": hazard_breakdown,
        "settlement_in_buffer_ha": round(buffer_settlement, 2),
        "settlement_in_buffer_pct": round(buffer_settlement / total_settlement * 100, 2),
        "affected_settlements": len(impacted_features),
        "survey_validation": survey_validation
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
