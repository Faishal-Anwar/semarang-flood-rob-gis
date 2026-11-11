import os, math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.offsetbox import AnchoredText
import geopandas as gpd
from shapely.geometry import box
import numpy as np

print("Generating high-resolution thematic cartographic maps (300 DPI)...")

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"
gpkg = f"{BASE_DIR}/04_DATABASE/Database_SIG.gpkg"

# Load layers from GeoPackage
gdf_kel = gpd.read_file(gpkg, layer="Batas_Administrasi_Kelurahan")
gdf_sungai = gpd.read_file(gpkg, layer="Sungai_dan_Drainase")
gdf_permukiman = gpd.read_file(gpkg, layer="Permukiman")
gdf_genangan = gpd.read_file(gpkg, layer="Area_Genangan_Banjir_Rob")
gdf_survei = gpd.read_file(gpkg, layer="Titik_Survei_Lapangan")
gdf_buffer = gpd.read_file(gpkg, layer="Buffer_Sungai")
gdf_terdampak = gpd.read_file(gpkg, layer="Permukiman_Terdampak")

# Inset map boundary
gdf_kota = gpd.read_file(f"{BASE_DIR}/02_DATA_MENTAH/Batas_Administrasi/Kota_Semarang_Inset.geojson")

# Main bounds with slight padding
xmin, ymin, xmax, ymax = gdf_kel.total_bounds
dx = xmax - xmin
dy = ymax - ymin
pad_x = dx * 0.04
pad_y = dy * 0.04
view_bounds = [xmin - pad_x, xmax + pad_x, ymin - pad_y, ymax + pad_y]

# Function to add North Arrow
def draw_north_arrow(ax, x, y, size=0.08):
    ax.annotate('U', xy=(x, y + size), xytext=(x, y - size),
                arrowprops=dict(facecolor='black', width=3, headwidth=10),
                ha='center', va='center', fontsize=12, fontweight='bold')

# ==========================================
# MAP 1: PETA PERSEBARAN BANJIR, ROB, SUNGAI, DAN PERMUKIMAN
# ==========================================
fig = plt.figure(figsize=(16, 11), dpi=300)
# Create 2 main axes: main map (left) and marginalia panel (right)
# [left, bottom, width, height]
ax_main = fig.add_axes([0.05, 0.05, 0.67, 0.90])
ax_side = fig.add_axes([0.73, 0.05, 0.23, 0.90])

# Hide ticks on sidebar
ax_side.set_xticks([])
ax_side.set_yticks([])
ax_side.set_xlim(0, 100)
ax_side.set_ylim(0, 100)
ax_side.set_facecolor('#fdfdfd')
for spine in ax_side.spines.values():
    spine.set_color('#2c3e50')
    spine.set_linewidth(1.5)

# --- PLOT MAIN MAP ---
ax_main.set_facecolor('#eef5fb') # Water / coastal tint
for spine in ax_main.spines.values():
    spine.set_color('#2c3e50')
    spine.set_linewidth(1.5)

# 1. Kelurahan background
gdf_kel.plot(ax=ax_main, facecolor='#fbfaf5', edgecolor='#7f8c8d', linewidth=1.2, linestyle='--')

# 2. Area Genangan Banjir & Rob
gen_colors = {
    'Sangat Tinggi': '#e74c3c', # Red for extreme rob
    'Tinggi': '#e67e22',        # Orange for high rob / flood
    'Sedang': '#f39c12'         # Yellow-orange for moderate
}
for tingkat, col in gen_colors.items():
    subset = gdf_genangan[gdf_genangan['tingkat_bahaya'] == tingkat]
    if len(subset) > 0:
        subset.plot(ax=ax_main, facecolor=col, alpha=0.45, edgecolor=col, linewidth=0.8, hatch='///')

# 3. Permukiman
gdf_permukiman.plot(ax=ax_main, facecolor='#d7ccc8', edgecolor='#8d6e63', linewidth=0.8, alpha=0.85)

# 4. Sungai dan Drainase
gdf_sungai[gdf_sungai['orde'] == 1].plot(ax=ax_main, color='#1565c0', linewidth=3.0, zorder=4)
gdf_sungai[gdf_sungai['orde'] == 2].plot(ax=ax_main, color='#1976d2', linewidth=2.0, zorder=4)
gdf_sungai[gdf_sungai['orde'] >= 3].plot(ax=ax_main, color='#29b6f6', linewidth=1.2, linestyle='-', zorder=4)

# 5. Titik Survei Lapangan & Genangan
# Rob points (red circle)
pt_rob = gdf_survei[gdf_survei['jenis_genangan'].str.contains('Rob')]
pt_banjir = gdf_survei[gdf_survei['jenis_genangan'].str.contains('Banjir|Limpasan|Genangan')]
pt_aman = gdf_survei[gdf_survei['jenis_genangan'].str.contains('Bebas')]

ax_main.scatter(pt_rob.geometry.x, pt_rob.geometry.y, c='#c0392b', s=45, marker='o', edgecolors='white', linewidth=0.8, zorder=6, label='Titik Genangan Rob')
ax_main.scatter(pt_banjir.geometry.x, pt_banjir.geometry.y, c='#d35400', s=40, marker='s', edgecolors='white', linewidth=0.8, zorder=6, label='Titik Banjir Limpasan/Hujan')
ax_main.scatter(pt_aman.geometry.x, pt_aman.geometry.y, c='#27ae60', s=40, marker='^', edgecolors='white', linewidth=0.8, zorder=6, label='Titik Pantau Bebas Genangan')

# Label Kelurahan
for _, row in gdf_kel.iterrows():
    pt = row.geometry.representative_point()
    ax_main.text(pt.x, pt.y, row['nama_kel'].upper(), fontsize=7.5, fontweight='bold',
                 color='#2c3e50', ha='center', va='center',
                 bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7, edgecolor='none'))

# Label Rivers
ax_main.text(433400, 9232500, 'Banjir Kanal Barat', fontsize=8, color='#0d47a1', fontweight='bold', rotation=78)
ax_main.text(436050, 9230500, 'Kali Semarang', fontsize=8, color='#0d47a1', fontweight='bold', rotation=75)
ax_main.text(436500, 9231500, 'Kali Baru', fontsize=7.5, color='#0d47a1', rotation=75)
ax_main.text(434000, 9230600, 'Kali Asin', fontsize=7.5, color='#0d47a1')
ax_main.text(437950, 9231200, 'Kali Banger', fontsize=7.5, color='#0d47a1', rotation=80)
ax_main.text(436000, 9233100, 'LAUT JAWA', fontsize=11, color='#1565c0', fontweight='heavy')

ax_main.set_xlim(view_bounds[0], view_bounds[1])
ax_main.set_ylim(view_bounds[2], view_bounds[3])

# Grid lines and coordinates formatting
ax_main.grid(True, linestyle=':', color='#95a5a6', alpha=0.7)
ax_main.set_xlabel('Koordinat X - UTM Zona 49S (meter)', fontsize=9, fontweight='bold', labelpad=6)
ax_main.set_ylabel('Koordinat Y - UTM Zona 49S (meter)', fontsize=9, fontweight='bold', labelpad=6)
ax_main.tick_params(labelsize=8)

# --- SIDEBAR CONTENT (MARGINALIA) ---
y_cur = 98

# 1. Judul Peta
ax_side.text(50, y_cur, "TUGAS BESAR SISTEM INFORMASI GEOGRAFIS", fontsize=9, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 3
ax_side.text(50, y_cur, "PROGRAM STUDI TEKNIK INFORMATIKA", fontsize=7.5, ha='center', color='#566573')
y_cur -= 4
ax_side.plot([5, 95], [y_cur, y_cur], color='#1a5276', linewidth=1.5)
y_cur -= 4

ax_side.text(50, y_cur, "PETA PERSEBARAN BANJIR, ROB,\nSUNGAI, DAN PERMUKIMAN", fontsize=10.5, fontweight='bold', ha='center', color='#0e2f44', linespacing=1.2)
y_cur -= 5.5
ax_side.text(50, y_cur, "KECAMATAN SEMARANG UTARA, KOTA SEMARANG", fontsize=8, fontweight='bold', ha='center', color='#2c3e50')
y_cur -= 4
ax_side.plot([15, 85], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 5

# 2. Skala & Arah Mata Angin
# Draw North Arrow
ax_side.annotate('U', xy=(25, y_cur + 2.5), xytext=(25, y_cur - 2.5),
                arrowprops=dict(facecolor='#2c3e50', width=2.5, headwidth=8),
                ha='center', va='center', fontsize=11, fontweight='bold')
ax_side.text(62, y_cur + 2, "SKALA 1 : 25.000", fontsize=9, fontweight='bold', ha='center')
ax_side.text(62, y_cur - 1.5, "1 cm di peta = 250 m di lapangan", fontsize=6.5, ha='center', color='#555')
# Scale Bar Graphic
ax_side.fill_between([45, 55], y_cur - 4.5, y_cur - 3.5, color='black')
ax_side.fill_between([55, 65], y_cur - 4.5, y_cur - 3.5, color='white', edgecolor='black')
ax_side.fill_between([65, 75], y_cur - 4.5, y_cur - 3.5, color='black')
ax_side.fill_between([75, 85], y_cur - 4.5, y_cur - 3.5, color='white', edgecolor='black')
ax_side.text(45, y_cur - 6, "0", fontsize=6, ha='center')
ax_side.text(65, y_cur - 6, "500", fontsize=6, ha='center')
ax_side.text(85, y_cur - 6, "1.000 m", fontsize=6, ha='center')
y_cur -= 10
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# 3. Inset Peta
ax_side.text(50, y_cur, "PETUNJUK LOKASI (INSET)", fontsize=8, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 14
# Sub-axes for inset
ax_inset = fig.add_axes([0.75, 0.05 + 0.90 * (y_cur / 100.0), 0.19, 0.12])
gdf_kota.plot(ax=ax_inset, facecolor='#ecf0f1', edgecolor='#7f8c8d', linewidth=0.8)
# Semarang Utara in inset
gdf_kel.dissolve().plot(ax=ax_inset, facecolor='#e74c3c', edgecolor='#c0392b', linewidth=1.2)
ax_inset.set_xticks([])
ax_inset.set_yticks([])
ax_inset.set_title("Kota Semarang", fontsize=6.5, pad=2)
for sp in ax_inset.spines.values():
    sp.set_color('#7f8c8d')

y_cur -= 4
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# 4. Legenda
ax_side.text(50, y_cur, "LEGENDA PETA", fontsize=8.5, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 4

legend_items = [
    # (type, color, label, extra)
    ('line_main', '#1565c0', 'Banjir Kanal Barat (Primer Orde 1)'),
    ('line_med', '#1976d2', 'Kali Semarang / Baru / Banger (Orde 2)'),
    ('line_thin', '#29b6f6', 'Saluran Drainase Primer / Sekunder'),
    ('poly', '#d7ccc8', 'Kawasan Permukiman Penduduk'),
    ('poly_hatch_red', '#e74c3c', 'Zona Rob Ekstrem Pesisir (Bahaya Sangat Tinggi)'),
    ('poly_hatch_org', '#e67e22', 'Zona Rob & Limpasan Muara (Bahaya Tinggi)'),
    ('poly_hatch_yel', '#f39c12', 'Zona Limpasan Kali Semarang (Bahaya Sedang)'),
    ('poly_kel', '#fbfaf5', 'Batas Administrasi Kelurahan'),
    ('pt_red', '#c0392b', 'Titik Survei: Genangan Rob Aktif (10 Titik)'),
    ('pt_org', '#d35400', 'Titik Survei: Banjir Limpasan/Hujan (12 Titik)'),
    ('pt_grn', '#27ae60', 'Titik Survei: Bebas Genangan (3 Titik)')
]

for itype, col, lab in legend_items:
    if 'line' in itype:
        lw = 3.0 if 'main' in itype else 2.0 if 'med' in itype else 1.2
        ax_side.plot([8, 16], [y_cur, y_cur], color=col, linewidth=lw)
    elif 'poly' in itype:
        if 'hatch' in itype:
            rect = mpatches.Rectangle((8, y_cur - 1.2), 8, 2.4, facecolor=col, alpha=0.5, edgecolor=col, hatch='//')
        elif 'kel' in itype:
            rect = mpatches.Rectangle((8, y_cur - 1.2), 8, 2.4, facecolor=col, edgecolor='#7f8c8d', linestyle='--', linewidth=1.0)
        else:
            rect = mpatches.Rectangle((8, y_cur - 1.2), 8, 2.4, facecolor=col, edgecolor='#8d6e63', linewidth=0.8)
        ax_side.add_patch(rect)
    elif 'pt' in itype:
        marker = 'o' if 'red' in itype else 's' if 'org' in itype else '^'
        ax_side.scatter(12, y_cur, c=col, s=35, marker=marker, edgecolors='white', linewidth=0.6)
    
    ax_side.text(20, y_cur - 0.7, lab, fontsize=6.2, va='center', color='#2c3e50')
    y_cur -= 3.1

y_cur -= 1
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# 5. Data Spasial & Sistem Koordinat
ax_side.text(50, y_cur, "SISTEM KOORDINAT & PROYEKSI", fontsize=7.5, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 2.6
ax_side.text(8, y_cur, "Sistem Proyeksi : Universal Transverse Mercator (UTM)", fontsize=6)
y_cur -= 2.2
ax_side.text(8, y_cur, "Datum Geodesi : WGS 1984 (Zona 49S - EPSG:32749)", fontsize=6)
y_cur -= 2.2
ax_side.text(8, y_cur, "Satuan Grid : Meter (m)", fontsize=6)
y_cur -= 3.2
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# 6. Sumber Data
ax_side.text(50, y_cur, "SUMBER DATA", fontsize=7.5, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 2.6
sources = [
    "1. Peta Rupa Bumi Indonesia (RBI) Badan Informasi Geospasial (BIG)",
    "2. SEMARIsK BPBD & SIG Drainase DPU Kota Semarang",
    "3. OpenStreetMap Data Contributors 2024",
    "4. Survei Lapangan 25 Titik GPS Tim Proyek SIG Maret 2026"
]
for s in sources:
    ax_side.text(8, y_cur, s, fontsize=5.6, color='#34495e')
    y_cur -= 2.1

y_cur -= 1.5
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# 7. Pembuat Peta
ax_side.text(50, y_cur, "DISUSUN OLEH:", fontsize=7.5, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 2.6
ax_side.text(50, y_cur, "KELOMPOK TUGAS BESAR SIG", fontsize=7.2, fontweight='bold', ha='center', color='#2c3e50')
y_cur -= 2.2
ax_side.text(50, y_cur, "Faishal Anwar (Koordinator & GIS Analyst)", fontsize=6.2, ha='center')
y_cur -= 2.0
ax_side.text(50, y_cur, "Tim Peneliti SIG Semarang Utara 2026", fontsize=6, ha='center', color='#7f8c8d')

# Save Map 1
peta1_pdf = f"{BASE_DIR}/06_PETA/Peta_1.pdf"
peta1_jpg = f"{BASE_DIR}/06_PETA/Peta_1.jpg"
plt.savefig(peta1_jpg, dpi=300, bbox_inches='tight')
plt.savefig(peta1_pdf, dpi=300, bbox_inches='tight')
plt.close(fig)
print("Map 1 exported successfully (PDF & 300 DPI JPG)!")

# ==========================================
# MAP 2: PETA ANALISIS EKSPOSUR PERMUKIMAN DI ZONA RAWAN
# ==========================================
fig = plt.figure(figsize=(16, 11), dpi=300)
ax_main = fig.add_axes([0.05, 0.05, 0.67, 0.90])
ax_side = fig.add_axes([0.73, 0.05, 0.23, 0.90])

ax_side.set_xticks([])
ax_side.set_yticks([])
ax_side.set_xlim(0, 100)
ax_side.set_ylim(0, 100)
ax_side.set_facecolor('#fdfdfd')
for spine in ax_side.spines.values():
    spine.set_color('#2c3e50')
    spine.set_linewidth(1.5)

ax_main.set_facecolor('#eef5fb')
for spine in ax_main.spines.values():
    spine.set_color('#2c3e50')
    spine.set_linewidth(1.5)

# 1. Kelurahan background
gdf_kel.plot(ax=ax_main, facecolor='#fbfaf5', edgecolor='#7f8c8d', linewidth=1.2, linestyle='--')

# 2. Buffer Sungai
# Buffer 200m (outer)
gdf_buffer[gdf_buffer['radius_m'] == 200].plot(ax=ax_main, facecolor='#b3e5fc', alpha=0.4, edgecolor='#81d4fa', linewidth=0.8)
# Buffer 100m (inner)
gdf_buffer[gdf_buffer['radius_m'] == 100].plot(ax=ax_main, facecolor='#81d4fa', alpha=0.55, edgecolor='#29b6f6', linewidth=1.0)

# 3. Area Genangan Banjir & Rob (Semi-transparent overlay)
gdf_genangan.plot(ax=ax_main, facecolor='#ffe0b2', alpha=0.35, edgecolor='#ffb74d', linewidth=0.8, linestyle=':')

# 4. Baseline Permukiman (all)
gdf_permukiman.plot(ax=ax_main, facecolor='#cfd8dc', edgecolor='#90a4ae', linewidth=0.5, alpha=0.6)

# 5. Permukiman Terdampak (Categorized by Risk Level)
risk_colors = {
    'Sangat Tinggi': '#b71c1c', # Deep Crimson Red
    'Tinggi': '#e65100',        # Deep Orange
    'Sedang': '#f57f17'         # Amber Yellow
}
for r_level, r_color in risk_colors.items():
    sub_td = gdf_terdampak[gdf_terdampak['tingkat_risiko'] == r_level]
    if len(sub_td) > 0:
        sub_td.plot(ax=ax_main, facecolor=r_color, edgecolor='#424242', linewidth=0.9, alpha=0.85, zorder=5)

# 6. Sungai dan Saluran Utama
gdf_sungai[gdf_sungai['orde'] == 1].plot(ax=ax_main, color='#0d47a1', linewidth=2.8, zorder=6)
gdf_sungai[gdf_sungai['orde'] == 2].plot(ax=ax_main, color='#1565c0', linewidth=1.8, zorder=6)
gdf_sungai[gdf_sungai['orde'] >= 3].plot(ax=ax_main, color='#1976d2', linewidth=1.0, zorder=6)

# Labels
for _, row in gdf_kel.iterrows():
    pt = row.geometry.representative_point()
    ax_main.text(pt.x, pt.y, row['nama_kel'].upper(), fontsize=7.5, fontweight='bold',
                 color='#2c3e50', ha='center', va='center',
                 bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.75, edgecolor='none'))

ax_main.text(433400, 9232500, 'Banjir Kanal Barat', fontsize=8, color='#0d47a1', fontweight='bold', rotation=78)
ax_main.text(436050, 9230500, 'Kali Semarang', fontsize=8, color='#0d47a1', fontweight='bold', rotation=75)
ax_main.text(436000, 9233100, 'LAUT JAWA', fontsize=11, color='#1565c0', fontweight='heavy')

# Callout annotation for high risk area (Tambak Lorok & Bandarharjo)
ax_main.annotate('Zona Rawan Ekstrem:\nTambak Lorok & Lamicitra\n(Rob Pasang > 50 cm)',
                xy=(437400, 9232200), xytext=(437000, 9233200),
                arrowprops=dict(facecolor='#b71c1c', arrowstyle='->', lw=1.5),
                fontsize=7.5, fontweight='bold', color='#b71c1c',
                bbox=dict(boxstyle='square,pad=0.3', facecolor='#ffebee', edgecolor='#b71c1c', lw=1))

ax_main.set_xlim(view_bounds[0], view_bounds[1])
ax_main.set_ylim(view_bounds[2], view_bounds[3])

ax_main.grid(True, linestyle=':', color='#95a5a6', alpha=0.7)
ax_main.set_xlabel('Koordinat X - UTM Zona 49S (meter)', fontsize=9, fontweight='bold', labelpad=6)
ax_main.set_ylabel('Koordinat Y - UTM Zona 49S (meter)', fontsize=9, fontweight='bold', labelpad=6)
ax_main.tick_params(labelsize=8)

# --- SIDEBAR CONTENT (MAP 2) ---
y_cur = 98

ax_side.text(50, y_cur, "TUGAS BESAR SISTEM INFORMASI GEOGRAFIS", fontsize=9, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 3
ax_side.text(50, y_cur, "PROGRAM STUDI TEKNIK INFORMATIKA", fontsize=7.5, ha='center', color='#566573')
y_cur -= 4
ax_side.plot([5, 95], [y_cur, y_cur], color='#1a5276', linewidth=1.5)
y_cur -= 4

ax_side.text(50, y_cur, "PETA ANALISIS EKSPOSUR\nPERMUKIMAN DI ZONA RAWAN", fontsize=10.5, fontweight='bold', ha='center', color='#0e2f44', linespacing=1.2)
y_cur -= 5.5
ax_side.text(50, y_cur, "KECAMATAN SEMARANG UTARA, KOTA SEMARANG", fontsize=8, fontweight='bold', ha='center', color='#2c3e50')
y_cur -= 4
ax_side.plot([15, 85], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 5

# Scale & North Arrow
ax_side.annotate('U', xy=(25, y_cur + 2.5), xytext=(25, y_cur - 2.5),
                arrowprops=dict(facecolor='#2c3e50', width=2.5, headwidth=8),
                ha='center', va='center', fontsize=11, fontweight='bold')
ax_side.text(62, y_cur + 2, "SKALA 1 : 25.000", fontsize=9, fontweight='bold', ha='center')
ax_side.text(62, y_cur - 1.5, "1 cm di peta = 250 m di lapangan", fontsize=6.5, ha='center', color='#555')
ax_side.fill_between([45, 55], y_cur - 4.5, y_cur - 3.5, color='black')
ax_side.fill_between([55, 65], y_cur - 4.5, y_cur - 3.5, color='white', edgecolor='black')
ax_side.fill_between([65, 75], y_cur - 4.5, y_cur - 3.5, color='black')
ax_side.fill_between([75, 85], y_cur - 4.5, y_cur - 3.5, color='white', edgecolor='black')
ax_side.text(45, y_cur - 6, "0", fontsize=6, ha='center')
ax_side.text(65, y_cur - 6, "500", fontsize=6, ha='center')
ax_side.text(85, y_cur - 6, "1.000 m", fontsize=6, ha='center')
y_cur -= 10
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# Inset Map
ax_side.text(50, y_cur, "PETUNJUK LOKASI (INSET)", fontsize=8, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 14
ax_inset = fig.add_axes([0.75, 0.05 + 0.90 * (y_cur / 100.0), 0.19, 0.12])
gdf_kota.plot(ax=ax_inset, facecolor='#ecf0f1', edgecolor='#7f8c8d', linewidth=0.8)
gdf_kel.dissolve().plot(ax=ax_inset, facecolor='#b71c1c', edgecolor='#7f0000', linewidth=1.2)
ax_inset.set_xticks([])
ax_inset.set_yticks([])
ax_inset.set_title("Kota Semarang", fontsize=6.5, pad=2)
for sp in ax_inset.spines.values():
    sp.set_color('#7f8c8d')

y_cur -= 4
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# Legenda Peta Analisis
ax_side.text(50, y_cur, "LEGENDA ANALISIS SPASIAL", fontsize=8.5, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 4

legend_items2 = [
    ('poly_risk_vhigh', '#b71c1c', 'Permukiman di Zona Rawan Ekstrem (Rob & Fluvial)'),
    ('poly_risk_high', '#e65100', 'Permukiman di Zona Rawan Rob Pesisir'),
    ('poly_risk_med', '#f57f17', 'Permukiman di Zona Rawan Limpasan (Sedang)'),
    ('poly_safe', '#cfd8dc', 'Permukiman di Luar Zona Rawan'),
    ('poly_buf100', '#81d4fa', 'Buffer Sungai Radius 0 - 100 m'),
    ('poly_buf200', '#b3e5fc', 'Buffer Sungai Radius 100 - 200 m'),
    ('poly_gen', '#ffe0b2', 'Zona Bahaya Genangan (Rob / Hujan)'),
    ('line_main', '#0d47a1', 'Jaringan Sungai Utama'),
    ('line_thin', '#1976d2', 'Jaringan Saluran Drainase'),
    ('poly_kel', '#fbfaf5', 'Batas Administrasi Kelurahan')
]

for itype, col, lab in legend_items2:
    if 'poly_risk' in itype or 'poly_safe' in itype:
        rect = mpatches.Rectangle((8, y_cur - 1.2), 8, 2.4, facecolor=col, edgecolor='#333', linewidth=0.8)
        ax_side.add_patch(rect)
    elif 'poly_buf' in itype:
        alpha = 0.55 if '100' in itype else 0.4
        rect = mpatches.Rectangle((8, y_cur - 1.2), 8, 2.4, facecolor=col, alpha=alpha, edgecolor='#0288d1', linewidth=0.8)
        ax_side.add_patch(rect)
    elif 'poly_gen' in itype:
        rect = mpatches.Rectangle((8, y_cur - 1.2), 8, 2.4, facecolor=col, alpha=0.5, edgecolor='#ff9800', linestyle=':', linewidth=0.8)
        ax_side.add_patch(rect)
    elif 'poly_kel' in itype:
        rect = mpatches.Rectangle((8, y_cur - 1.2), 8, 2.4, facecolor=col, edgecolor='#7f8c8d', linestyle='--', linewidth=1.0)
        ax_side.add_patch(rect)
    elif 'line' in itype:
        lw = 2.8 if 'main' in itype else 1.2
        ax_side.plot([8, 16], [y_cur, y_cur], color=col, linewidth=lw)
    
    ax_side.text(20, y_cur - 0.7, lab, fontsize=6.0, va='center', color='#2c3e50')
    y_cur -= 3.1

y_cur -= 1
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# Ringkasan Statistik Spasial di Sidebar
ax_side.text(50, y_cur, "STATISTIK EKSPOSUR ZONA RAWAN", fontsize=7.5, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 2.6
tot_perm = gdf_permukiman.geometry.area.sum() / 10000.0
tot_td = gdf_terdampak.geometry.area.sum() / 10000.0
pct_tot = (tot_td / tot_perm) * 100.0

ax_side.text(8, y_cur, f"Total Permukiman di Zona Rawan : {tot_td:.2f} Ha ({pct_tot:.1f}%)", fontsize=6.2, fontweight='bold', color='#b71c1c')
y_cur -= 2.2
ax_side.text(8, y_cur, "Rasio Zona Rawan Tertinggi : Panggung Kidul & Panggung Lor", fontsize=6, color='#2c3e50')
y_cur -= 2.2
ax_side.text(8, y_cur, "Kawasan Paling Kritis : Tanah Mas/Puri Anjasmoro (Panggung Lor)", fontsize=6, color='#2c3e50')
y_cur -= 3.2
ax_side.plot([5, 95], [y_cur, y_cur], color='#bdc3c7', linewidth=1.0)
y_cur -= 3

# Sistem Koordinat & Sumber
ax_side.text(50, y_cur, "SISTEM PROYEKSI & SUMBER", fontsize=7.5, fontweight='bold', ha='center', color='#1a5276')
y_cur -= 2.5
ax_side.text(8, y_cur, "Proyeksi: Transverse Mercator (UTM Zone 49S, WGS 84)", fontsize=5.8)
y_cur -= 2.0
ax_side.text(8, y_cur, "Sumber: Hasil Analisis Buffer 200m & Intersect Overlay SIG", fontsize=5.8)
y_cur -= 2.0
ax_side.text(8, y_cur, "Disusun: Tim Mahasiswa Tugas Besar SIG 2026", fontsize=5.8)

# Save Map 2
peta2_pdf = f"{BASE_DIR}/06_PETA/Peta_2.pdf"
peta2_jpg = f"{BASE_DIR}/06_PETA/Peta_2.jpg"
plt.savefig(peta2_jpg, dpi=300, bbox_inches='tight')
plt.savefig(peta2_pdf, dpi=300, bbox_inches='tight')
plt.close(fig)
print("Map 2 exported successfully (PDF & 300 DPI JPG)!")
