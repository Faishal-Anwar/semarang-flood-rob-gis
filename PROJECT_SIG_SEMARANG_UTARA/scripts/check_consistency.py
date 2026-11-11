#!/usr/bin/env python3
"""Audit consistency of key project numbers across data, UI, GPKG, PDF, and PPTX."""
from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "webgis"
STATS = WEB / "data" / "statistik.json"
STATS_BACKEND = ROOT / "backend" / "data" / "statistik.json"
GPKG_COPIES = [
    ROOT / "database" / "Database_SIG.gpkg",
    ROOT / "04_DATABASE" / "Database_SIG.gpkg",
    WEB / "downloads" / "Database_SIG.gpkg",
]
EXPECTED = {
    "total_settlement_area_ha": 171.68,
    "total_impacted_settlement_ha": 120.31,
    "impact_percentage": 70.08,
    "settlement_in_buffer_200m_ha": 81.99,
    "settlement_in_buffer_200m_pct": 47.76,
}

failures: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(message)


def close(actual: float, expected: float, tolerance: float = 0.02) -> bool:
    return abs(float(actual) - float(expected)) <= tolerance


def main() -> int:
    data = json.loads(STATS.read_text(encoding="utf-8"))
    backend = json.loads(STATS_BACKEND.read_text(encoding="utf-8"))
    check(data == backend, "statistik.json webgis dan backend berbeda")

    kpi = data["kpi_summary"]
    for key, expected in EXPECTED.items():
        check(close(kpi.get(key, -999), expected), f"KPI {key} != {expected} (actual {kpi.get(key)})")

    hazard = data.get("hazard_breakdown_ha", {})
    check(close(sum(hazard.values()), kpi["total_settlement_area_ha"]), "Jumlah hazard_breakdown tidak sama dengan total permukiman")
    check(close(sum(hazard.values()) - hazard.get("Di Luar Zona Rawan (BPBD)", 0), kpi["total_impacted_settlement_ha"]), "Jumlah hazard kelas rawan tidak sama dengan 120,31 Ha")

    rankings = data.get("kelurahan_rankings", [])
    check(len(rankings) == 9, f"Ranking kelurahan harus 9, ditemukan {len(rankings)}")
    check(close(sum(r["luas_terpapar_ha"] for r in rankings), kpi["total_impacted_settlement_ha"], 0.03), "Jumlah luas zona rawan ranking tidak sama dengan 120,31 Ha")
    check(close(sum(r["luas_permukiman_ha"] for r in rankings), kpi["total_settlement_area_ha"], 0.03), "Jumlah luas permukiman ranking tidak sama dengan 171,68 Ha")
    check(rankings[0]["nama_kel"] == "Panggung Kidul" and close(rankings[0]["rasio_persen"], 97.37), "Peringkat 1 bukan Panggung Kidul 97,37%")
    check(rankings[1]["nama_kel"] == "Panggung Lor" and close(rankings[1]["rasio_persen"], 95.76), "Peringkat 2 bukan Panggung Lor 95,76%")

    statuses = {r["nama_kel"]: r["tingkat_kerentanan"] for r in rankings}
    check(statuses.get("Bulu Lor") == "Di Luar Zona Rawan", "Status Bulu Lor harus Di Luar Zona Rawan")
    check(statuses.get("Plombokan") == "Di Luar Zona Rawan", "Status Plombokan harus Di Luar Zona Rawan")

    # UI must not reintroduce stale or misleading labels.
    for html in WEB.glob("*.html"):
        text = html.read_text(encoding="utf-8")
        for stale in ["142,57", "142.57", "83,04", "83.04", "Aman / Bebas Genangan", "Tidak Terdampak"]:
            check(stale not in text, f"{html.name} masih memuat label/angka lama: {stale}")
    for html in ["index.html", "dashboard.html", "map.html", "analysis.html"]:
        text = (WEB / html).read_text(encoding="utf-8")
        check("120,31" in text and "70,08" in text, f"{html} tidak memuat KPI 120,31 / 70,08")

    # GeoPackage status values.
    for gpkg in GPKG_COPIES:
        check(gpkg.exists(), f"GeoPackage tidak ditemukan: {gpkg}")
        if not gpkg.exists():
            continue
        conn = sqlite3.connect(gpkg)
        try:
            rows = dict(conn.execute("SELECT nama_kel, status_kerentanan FROM Tabel_Kelurahan_Profil").fetchall())
        finally:
            conn.close()
        check(rows.get("Bulu Lor") == "Di Luar Zona Rawan", f"{gpkg.name}: status Bulu Lor salah")
        check(rows.get("Plombokan") == "Di Luar Zona Rawan", f"{gpkg.name}: status Plombokan salah")

    # PDF report stale-number scan (optional if pdftotext exists).
    report = ROOT / "08_LAPORAN" / "Laporan_Akhir.pdf"
    if report.exists() and shutil_which("pdftotext"):
        out = subprocess.run(["pdftotext", str(report), "-"], capture_output=True, text=True)
        text = out.stdout.replace("\n", " ")
        for stale in ["142,57", "83,04", "Tanjung Mas, Bandarharjo, dan Panggung Lor"]:
            check(stale not in text, f"Laporan PDF masih memuat: {stale}")
        check(not re.search(r"Permukiman_Terdampak\s+Vektor MultiPolygon\s+15", text), "Laporan PDF masih menulis Permukiman_Terdampak 15 Klaster")
        check("120,31" in text and "eksposur statis" in text.lower(), "Laporan PDF tidak memuat eksposur statis 120,31")

    # PPTX stale-note scan.
    pptx = ROOT / "09_PRESENTASI" / "Presentasi_SIG.pptx"
    if pptx.exists():
        try:
            from pptx import Presentation
            prs = Presentation(pptx)
            all_text = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        all_text.append(shape.text_frame.text)
                if slide.has_notes_slide:
                    all_text.append(slide.notes_slide.notes_text_frame.text)
            joined = "\n".join(all_text)
            for stale in ["Tanjung Mas, Bandarharjo, dan Panggung Lor", "15 Klaster"]:
                check(stale not in joined, f"PPTX masih memuat: {stale}")
        except ImportError:
            pass

    print(f"[CHECK] {checks} pemeriksaan dijalankan")
    if failures:
        print(f"[FAIL] {len(failures)} masalah ditemukan:")
        for item in failures:
            print("  -", item)
        return 1
    print("[PASS] Konsistensi data, UI, GeoPackage, PDF, dan PPTX sesuai.")
    return 0


def shutil_which(command: str) -> bool:
    from shutil import which
    return which(command) is not None


if __name__ == "__main__":
    sys.exit(main())
