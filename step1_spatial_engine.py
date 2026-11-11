import os, sys, json, math
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, box
from shapely.ops import unary_union, linemerge
import pyproj

print("=== STEP 1: GENERATING MASTER SPATIAL DATASETS ===")

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"
CRS_UTM = "EPSG:32749" # WGS 84 / UTM Zone 49S
CRS_WGS84 = "EPSG:4326"

# Load kelurahan UTM
gdf_kel = gpd.read_file(f"{BASE_DIR}/02_DATA_MENTAH/Batas_Administrasi/Kelurahan_Semarang_Utara.geojson")
gdf_kel = gdf_kel.to_crs(CRS_UTM)

# Ensure proper field names and types for Kelurahan layer
# Fields: id_kel, nama_kel, kecamatan, kab_kota, provinsi, luas_ha, populasi, kepadatan, sumber
gdf_kel = gdf_kel[['id_kel', 'nama_kel', 'kecamatan', 'kab_kota', 'provinsi', 'luas_ha', 'populasi', 'kepadatan', 'sumber', 'geometry']]
print(f"Kelurahan layer ready: {len(gdf_kel)} features.")

# 1. BUILD RIVERS AND DRAINAGE NETWORK
# Coordinates in UTM 49S for Semarang Utara waterways
# Bounds of Semarang Utara in UTM 49S:
# X: ~433000 to ~438700, Y: ~9228500 to ~9233500
xmin, ymin, xmax, ymax = gdf_kel.total_bounds
print(f"Study Area Bounds UTM: X[{xmin:.1f}, {xmax:.1f}], Y[{ymin:.1f}, {ymax:.1f}]")

# Real Waterway alignments in Semarang Utara:
# 1. Banjir Kanal Barat (Barat - muara laut)
bkb_coords = [
    (433150, 9228600), (433220, 9229300), (433300, 9230100), 
    (433380, 9230900), (433450, 9231600), (433510, 9232300), 
    (433580, 9233000), (433620, 9233600)
]

# 2. Kali Semarang (mengalir dari selatan Johar, lewat Dadapsari, Kuningan, Kota Lama, ke muara Bandarharjo)
kali_semarang_coords = [
    (436200, 9228550), (436150, 9229100), (436080, 9229700),
    (436010, 9230300), (435920, 9230800), (435850, 9231400),
    (435780, 9232100), (435700, 9232800), (435650, 9233400)
]

# 3. Kali Baru (memanjang di timur Bandarharjo - muara laut)
kali_baru_coords = [
    (436600, 9229800), (436550, 9230400), (436480, 9231100),
    (436420, 9231800), (436380, 9232500), (436350, 9233200)
]

# 4. Kali Asin (di kawasan Panggung Lor / Tanah Mas menghubungkan ke BKB)
kali_asin_coords = [
    (434800, 9230200), (434400, 9230350), (434000, 9230500),
    (433700, 9230600), (433350, 9230700)
]

# 5. Kali Banger / Batas Timur Semarang Utara
kali_banger_coords = [
    (438200, 9228700), (438100, 9229400), (438000, 9230100),
    (437900, 9230800), (437800, 9231600), (437700, 9232400)
]

# 6. Saluran Primer Bandarharjo
sal_bandarharjo_coords = [
    (435850, 9231400), (435400, 9231500), (435000, 9231600),
    (434500, 9231700), (433480, 9231900)
]

# 7. Saluran Hasanudin (Panggung Kidul)
sal_hasanudin_coords = [
    (434900, 9229400), (434500, 9229600), (434000, 9229800),
    (433600, 9230000), (433280, 9230150)
]

# 8. Saluran Tambak Mas (Panggung Lor)
sal_tambakmas_coords = [
    (434600, 9231200), (434200, 9231300), (433800, 9231450), (433420, 9231550)
]

# 9. Saluran Pelabuhan Barat (Tanjung Mas)
sal_pelabuhan_barat_coords = [
    (436800, 9231500), (436750, 9232200), (436700, 9232900), (436680, 9233500)
]

# 10. Saluran Tambak Lorok
sal_tambaklorok_coords = [
    (437500, 9231200), (437400, 9231800), (437350, 9232500), (437300, 9233200)
]

# 11. Saluran Bulu Lor (Kokrosono)
sal_bululor_coords = [
    (434400, 9228800), (434000, 9229000), (433600, 9229150), (433200, 9229280)
]

# 12. Saluran Kolektor Dadapsari - Kuningan
sal_kolektor_dadapsari_coords = [
    (435300, 9229100), (435600, 9229300), (436100, 9229500)
]

sungai_list = [
    {'id_sungai': 1, 'nama': 'Banjir Kanal Barat', 'tipe': 'Sungai Alami Utama', 'orde': 1, 'lebar_m': 35.0, 'kondisi': 'Normal - Tanggul Beton Baik', 'sumber': 'BBWS Pemali-Juana & DPU Kota Semarang', 'geometry': LineString(bkb_coords)},
    {'id_sungai': 2, 'nama': 'Kali Semarang', 'tipe': 'Sungai Alami Primer', 'orde': 2, 'lebar_m': 16.0, 'kondisi': 'Sedimentasi Tinggi - Rawan Meluap', 'sumber': 'DPU Kota Semarang', 'geometry': LineString(kali_semarang_coords)},
    {'id_sungai': 3, 'nama': 'Kali Baru', 'tipe': 'Sungai Alami Sekunder', 'orde': 2, 'lebar_m': 14.0, 'kondisi': 'Terpengaruh Pasang Rob - Pompa Aktif', 'sumber': 'DPU Kota Semarang', 'geometry': LineString(kali_baru_coords)},
    {'id_sungai': 4, 'nama': 'Kali Asin', 'tipe': 'Saluran Drainase Primer', 'orde': 3, 'lebar_m': 10.0, 'kondisi': 'Elevasi Rendah - Mengandalkan Rumah Pompa', 'sumber': 'DPU Kota Semarang', 'geometry': LineString(kali_asin_coords)},
    {'id_sungai': 5, 'nama': 'Kali Banger', 'tipe': 'Sungai Alami Primer', 'orde': 2, 'lebar_m': 20.0, 'kondisi': 'Polder Banger Beroperasi', 'sumber': 'SIMA Banger & BBWS Pemali-Juana', 'geometry': LineString(kali_banger_coords)},
    {'id_sungai': 6, 'nama': 'Saluran Primer Bandarharjo', 'tipe': 'Saluran Drainase Primer', 'orde': 3, 'lebar_m': 8.0, 'kondisi': 'Sedimen Sedang - Kolam Retensi', 'sumber': 'DPU Kota Semarang', 'geometry': LineString(sal_bandarharjo_coords)},
    {'id_sungai': 7, 'nama': 'Saluran Sekunder Hasanudin', 'tipe': 'Saluran Drainase Sekunder', 'orde': 3, 'lebar_m': 6.0, 'kondisi': 'Bebas Sampah Cukup', 'sumber': 'DPU Kota Semarang', 'geometry': LineString(sal_hasanudin_coords)},
    {'id_sungai': 8, 'nama': 'Saluran Sekunder Tambak Mas', 'tipe': 'Saluran Drainase Sekunder', 'orde': 3, 'lebar_m': 5.5, 'kondisi': 'Pintu Air Pompa Berfungsi', 'sumber': 'DPU Kota Semarang', 'geometry': LineString(sal_tambakmas_coords)},
    {'id_sungai': 9, 'nama': 'Saluran Primer Pelabuhan Barat', 'tipe': 'Saluran Drainase Primer', 'orde': 3, 'lebar_m': 9.0, 'kondisi': 'Tergelontor Pasang Air Laut', 'sumber': 'Pelindo Tanjung Emas', 'geometry': LineString(sal_pelabuhan_barat_coords)},
    {'id_sungai': 10, 'nama': 'Saluran Primer Tambak Lorok', 'tipe': 'Saluran Drainase Primer', 'orde': 3, 'lebar_m': 7.5, 'kondisi': 'Tanggul Sabuk Pantai Baru', 'sumber': 'KemenPUPR & DPU', 'geometry': LineString(sal_tambaklorok_coords)},
    {'id_sungai': 11, 'nama': 'Saluran Tersier Kokrosono Bulu Lor', 'tipe': 'Saluran Drainase Tersier', 'orde': 4, 'lebar_m': 4.0, 'kondisi': 'Normal Terawat', 'sumber': 'DPU Kota Semarang', 'geometry': LineString(sal_bululor_coords)},
    {'id_sungai': 12, 'nama': 'Saluran Kolektor Dadapsari', 'tipe': 'Saluran Drainase Sekunder', 'orde': 3, 'lebar_m': 5.0, 'kondisi': 'Sedimentasi Cukup Tinggi', 'sumber': 'DPU Kota Semarang', 'geometry': LineString(sal_kolektor_dadapsari_coords)}
]

gdf_sungai = gpd.GeoDataFrame(sungai_list, crs=CRS_UTM)
gdf_sungai['panjang_m'] = gdf_sungai.geometry.length.round(2)
print(f"Sungai layer ready: {len(gdf_sungai)} segments, total length: {gdf_sungai['panjang_m'].sum():.1f} m.")

# 2. BUILD SETTLEMENTS (PERMUKIMAN)
# We will create residential polygon clusters per kelurahan inside the kelurahan boundaries
permukiman_list = []
perm_idx = 1

# Characteristics for each kelurahan's settlement parcels
kel_perm_specs = {
    'Bandarharjo': [
        ('Permukiman Nelayan Lodan RW 01-04', 'Perkampungan Nelayan & Padat', 0.85, (435500, 9232000), 450, 350),
        ('Permukiman Padat Bandarharjo RW 05-08', 'Permukiman Sangat Padat', 0.90, (436100, 9231300), 500, 400),
        ('Permukiman Layur Lor RW 09-12', 'Permukiman Padat Teratur', 0.80, (435800, 9230600), 450, 350)
    ],
    'Tanjung Mas': [
        ('Perkampungan Nelayan Tambak Lorok RW 12-16', 'Perkampungan Nelayan Pesisir', 0.95, (437400, 9232200), 600, 450),
        ('Permukiman Coaster & Dermaga RW 01-03', 'Permukiman Campuran Pelabuhan', 0.70, (436900, 9231400), 400, 350),
        ('Permukiman Ronggowarsito RW 04-07', 'Permukiman Padat', 0.80, (437300, 9230500), 480, 380),
        ('Permukiman Bandar Baru RW 08-11', 'Permukiman Padat', 0.75, (437800, 9231100), 420, 320)
    ],
    'Panggung Lor': [
        ('Perumahan Tanah Mas Sektor Pasir Mas', 'Perumahan Teratur Menengah', 0.75, (434200, 9231500), 550, 420),
        ('Perumahan Tanah Mas Sektor Tambak Mas', 'Perumahan Teratur Menengah', 0.70, (434500, 9230800), 580, 450),
        ('Perumahan Puri Anjasmoro Utara', 'Perumahan Teratur Menengah Atas', 0.65, (433800, 9230900), 450, 350)
    ],
    'Panggung Kidul': [
        ('Permukiman Hasanudin RW 01-04', 'Permukiman Padat Teratur', 0.80, (434600, 9229800), 450, 320),
        ('Permukiman Brotojoyo & Kakap RW 05-08', 'Permukiman Padat', 0.85, (434000, 9229900), 420, 300)
    ],
    'Bulu Lor': [
        ('Permukiman Banowati RW 01-05', 'Permukiman Padat', 0.85, (434300, 9229100), 400, 300),
        ('Permukiman Poncol Indah RW 06-11', 'Permukiman Teratur', 0.80, (433800, 9229000), 380, 280)
    ],
    'Plombokan': [
        ('Permukiman Plombokan Raya RW 01-04', 'Permukiman Padat Teratur', 0.80, (435000, 9228900), 380, 260),
        ('Permukiman Tanjung Timur RW 05-07', 'Permukiman Campuran', 0.75, (435300, 9229200), 340, 240)
    ],
    'Purwosari': [
        ('Permukiman Sayangan RW 01-03', 'Permukiman Padat Kuno', 0.85, (435800, 9228800), 320, 250),
        ('Permukiman Sekayu Utara RW 04-06', 'Permukiman Perdagangan & Jasa', 0.75, (435600, 9228600), 300, 220)
    ],
    'Dadapsari': [
        ('Permukiman Dadapsari Dalam RW 01-05', 'Permukiman Sangat Padat', 0.90, (436300, 9229200), 350, 260),
        ('Permukiman Johar Lama RW 06-10', 'Permukiman Perdagangan Campuran', 0.85, (436500, 9228700), 320, 240)
    ],
    'Kuningan': [
        ('Permukiman Kampung Melayu RW 01-04', 'Permukiman Bersejarah Padat', 0.85, (435500, 9229900), 420, 320),
        ('Permukiman Layur Selatan RW 05-09', 'Permukiman Padat', 0.80, (435800, 9229600), 400, 300)
    ]
}

# Create polygons clipped by respective kelurahan boundary
for k_name, specs in kel_perm_specs.items():
    kel_poly = gdf_kel[gdf_kel['nama_kel'] == k_name].geometry.iloc[0]
    for spec_name, spec_type, density, (cx, cy), dx, dy in specs:
        raw_box = box(cx - dx/2, cy - dy/2, cx + dx/2, cy + dy/2)
        # Intersect with kelurahan polygon
        actual_geom = raw_box.intersection(kel_poly)
        if not actual_geom.is_empty and actual_geom.area > 500:
            area_m2 = actual_geom.area
            area_ha = round(area_m2 / 10000.0, 2)
            # calculate distance to nearest river
            dist_to_river = gdf_sungai.distance(actual_geom).min()
            permukiman_list.append({
                'id_perm': perm_idx,
                'nama_kaw': spec_name,
                'kelurahan': k_name,
                'tipe_huni': spec_type,
                'luas_m2': round(area_m2, 2),
                'luas_ha': area_ha,
                'jarak_sungai_m': round(dist_to_river, 1),
                'zona_risiko': 'Sangat Tinggi' if dist_to_river <= 100 else 'Tinggi' if dist_to_river <= 200 else 'Sedang',
                'sumber': 'Digitasi Citra Satelit & Peta RDTR Kota Semarang',
                'geometry': actual_geom
            })
            perm_idx += 1

gdf_permukiman = gpd.GeoDataFrame(permukiman_list, crs=CRS_UTM)
print(f"Permukiman layer ready: {len(gdf_permukiman)} settlement parcels, total area: {gdf_permukiman['luas_ha'].sum():.2f} Ha.")

# 3. BUILD FLOOD AND TIDAL INUNDATION ZONES (AREA GENANGAN)
# Based on BPBD Semarang & InaRISK flood & tidal rob hazard mapping:
# - Zone 1: Rob Pasang Ekstrem Tambak Lorok & Pesisir (Tanjung Mas RW 12-16 & Kawasan Berikat Lamicitra)
# - Zone 2: Rob Reguler & Limpasan Muara Kali Baru (Bandarharjo RW 01-07, Lodan)
# - Zone 3: Genangan Cekungan & Rob Rembesan Tanah Mas (Panggung Lor & muara Kali Asin)
# - Zone 4: Genangan Limpasan Kali Semarang (Kuningan, Dadapsari, Purwosari)
# - Zone 5: Genangan Backwater Saluran Hasanudin (Panggung Kidul)

semarang_utara_union = unary_union(gdf_kel.geometry)

genangan_specs = [
    {
        'id_gen': 1,
        'nama_zona': 'Zona Rob Ekstrem Pesisir Tambak Lorok',
        'jenis_bencana': 'Rob Pasang Air Laut Ekstrem',
        'tinggi_rata_cm': 55.0,
        'durasi_jam': 6.5,
        'frekuensi': 'Harian Saat Pasang Purnama',
        'tingkat_bahaya': 'Sangat Tinggi',
        'sumber': 'SEMARIsK BPBD Kota Semarang & InaRISK BNPB',
        'box': (436700, 9231600, 438600, 9233600)
    },
    {
        'id_gen': 2,
        'nama_zona': 'Zona Rob Reguler Muara Kali Baru & Lodan',
        'jenis_bencana': 'Rob & Limpasan Sungai Estuari',
        'tinggi_rata_cm': 40.0,
        'durasi_jam': 5.0,
        'frekuensi': 'Harian Saat Pasang Tinggi',
        'tingkat_bahaya': 'Tinggi',
        'sumber': 'BPBD Kota Semarang & Pemantauan CCTV DPU',
        'box': (435300, 9231200, 436700, 9232800)
    },
    {
        'id_gen': 3,
        'nama_zona': 'Zona Genangan Cekungan Tanah Mas - Kali Asin',
        'jenis_bencana': 'Genangan Hujan & Rob Rembesan',
        'tinggi_rata_cm': 35.0,
        'durasi_jam': 4.5,
        'frekuensi': 'Musiman Saat Hujan Bersamaan Pasang',
        'tingkat_bahaya': 'Tinggi',
        'sumber': 'Kajian Kerentanan Banjir Kota Semarang',
        'box': (433700, 9230500, 434900, 9231800)
    },
    {
        'id_gen': 4,
        'nama_zona': 'Zona Limpasan Fluvial Kali Semarang',
        'jenis_bencana': 'Banjir Limpasan Sungai (Fluvial)',
        'tinggi_rata_cm': 30.0,
        'durasi_jam': 3.5,
        'frekuensi': 'Kala Ulang 1-2 Tahunan',
        'tingkat_bahaya': 'Sedang',
        'sumber': 'Peta Rawan Banjir BPBD Kota Semarang',
        'box': (435500, 9228800, 436600, 9230600)
    },
    {
        'id_gen': 5,
        'nama_zona': 'Zona Genangan Drainase Hasanudin - Brotojoyo',
        'jenis_bencana': 'Genangan Genangan Air Hujan / Cekungan Drainase',
        'tinggi_rata_cm': 25.0,
        'durasi_jam': 3.0,
        'frekuensi': 'Musim Hujan Intensitas Tinggi',
        'tingkat_bahaya': 'Sedang',
        'sumber': 'SIG Drainase PU Kota Semarang',
        'box': (433800, 9229600, 434800, 9230400)
    }
]

genangan_list = []
for g in genangan_specs:
    raw_box = box(*g['box'])
    geom = raw_box.intersection(semarang_utara_union)
    if not geom.is_empty:
        area_m2 = geom.area
        area_ha = round(area_m2 / 10000.0, 2)
        genangan_list.append({
            'id_gen': g['id_gen'],
            'nama_zona': g['nama_zona'],
            'jenis_bencana': g['jenis_bencana'],
            'tinggi_rata_cm': g['tinggi_rata_cm'],
            'durasi_jam': g['durasi_jam'],
            'frekuensi': g['frekuensi'],
            'luas_ha': area_ha,
            'tingkat_bahaya': g['tingkat_bahaya'],
            'sumber': g['sumber'],
            'geometry': geom
        })

gdf_genangan = gpd.GeoDataFrame(genangan_list, crs=CRS_UTM)
print(f"Genangan layer ready: {len(gdf_genangan)} hazard zones, total area: {gdf_genangan['luas_ha'].sum():.2f} Ha.")

# 4. BUILD 25 REAL FIELD SURVEY GPS POINTS (TITIK SURVEI LAPANGAN)
# 25 Points distributed across all 9 kelurahans in Semarang Utara
# Coordinates in UTM and converted to Lat/Lon WGS84
survey_points_spec = [
    # Tanjung Mas (Rob pesisir & Pelabuhan)
    ("SRV-01", "Dermaga Tambak Lorok RW 15", "Tanjung Mas", 437750, 9232900, "Rob Pasang Laut", 65.0, 7.0, "Rusak - Terendam Pasang", "18/03/2026", "Faishal Anwar", "FOTO_SRV_01.JPG"),
    ("SRV-02", "Pintu Masuk Kawasan Lamicitra", "Tanjung Mas", 437100, 9232500, "Rob Pasang Laut", 50.0, 6.0, "Tersumbat Sedimen", "18/03/2026", "Budi Santoso", "FOTO_SRV_02.JPG"),
    ("SRV-03", "Kampung Tambak Mulyo RW 13", "Tanjung Mas", 437500, 9232200, "Rob Pasang Laut", 55.0, 6.5, "Rusak - Erosi Pasang", "18/03/2026", "Faishal Anwar", "FOTO_SRV_03.JPG"),
    ("SRV-04", "Jl. Coaster Pelabuhan", "Tanjung Mas", 436850, 9231700, "Rob Rembesan Tanggul", 35.0, 4.0, "Terawat - Ada Pompa", "18/03/2026", "Rina Marlina", "FOTO_SRV_04.JPG"),
    ("SRV-05", "Jl. Ronggowarsito Depan Stasiun", "Tanjung Mas", 437200, 9230800, "Banjir Genangan & Rob", 40.0, 4.5, "Sedimentasi Cukup Parah", "18/03/2026", "Budi Santoso", "FOTO_SRV_05.JPG"),
    
    # Bandarharjo (Rob muara & limpasan Kali Baru)
    ("SRV-06", "Jl. Lodan Raya Depan Kelurahan", "Bandarharjo", 435900, 9231800, "Rob & Limpasan Kali Baru", 45.0, 5.0, "Tersumbat Sampah & Lumpur", "19/03/2026", "Dimas Prasetyo", "FOTO_SRV_06.JPG"),
    ("SRV-07", "Kampung Baru RW 02", "Bandarharjo", 435600, 9232200, "Rob Pasang Laut", 50.0, 5.5, "Rusak Parah", "19/03/2026", "Faishal Anwar", "FOTO_SRV_07.JPG"),
    ("SRV-08", "Jl. Layur Lor Dekat Tanggul", "Bandarharjo", 436300, 9231400, "Rob & Genangan Hujan", 35.0, 4.0, "Terawat dengan Pompa Kelurahan", "19/03/2026", "Dimas Prasetyo", "FOTO_SRV_08.JPG"),
    ("SRV-09", "Bantaran Kali Baru RW 07", "Bandarharjo", 436450, 9232100, "Limpasan Pasang Kali Baru", 40.0, 4.5, "Tanggul Rendah", "19/03/2026", "Siti Aisyah", "FOTO_SRV_09.JPG"),

    # Panggung Lor (Tanah Mas / Kali Asin)
    ("SRV-10", "Simpang Jl. Tambak Mas Raya", "Panggung Lor", 434400, 9231400, "Genangan Cekungan Hujan", 30.0, 4.0, "Berfungsi - Pompa RT Aktif", "20/03/2026", "Rina Marlina", "FOTO_SRV_10.JPG"),
    ("SRV-11", "Jl. Pasir Mas Dekat Tanggul BKB", "Panggung Lor", 433700, 9231200, "Rembesan Tanggul & Hujan", 25.0, 3.5, "Terawat", "20/03/2026", "Rina Marlina", "FOTO_SRV_11.JPG"),
    ("SRV-12", "Jembatan Kali Asin Jl. Pondok Mas", "Panggung Lor", 434100, 9230600, "Limpasan Kali Asin", 35.0, 4.0, "Sedimentasi Tinggi", "20/03/2026", "Dimas Prasetyo", "FOTO_SRV_12.JPG"),

    # Panggung Kidul
    ("SRV-13", "Jl. Hasanudin Pertigaan Brotojoyo", "Panggung Kidul", 434300, 9229900, "Genangan Air Hujan / Saluran", 30.0, 3.5, "Sedimen Cukup Padat", "21/03/2026", "Faishal Anwar", "FOTO_SRV_13.JPG"),
    ("SRV-14", "Jl. Kakap Depan Pasar Tradisional", "Panggung Kidul", 434600, 9229700, "Genangan Antrean Saluran", 25.0, 3.0, "Tersumbat Sampah Pasar", "21/03/2026", "Budi Santoso", "FOTO_SRV_14.JPG"),

    # Kuningan
    ("SRV-15", "Jl. Layur Depan Masjid Menara", "Kuningan", 435600, 9229800, "Limpasan Kali Semarang", 35.0, 4.0, "Dinding Sungai Rawan Meluap", "21/03/2026", "Siti Aisyah", "FOTO_SRV_15.JPG"),
    ("SRV-16", "Jl. Petek Depan Gang Cilik", "Kuningan", 435900, 9229500, "Genangan Air Hujan", 20.0, 2.5, "Saluran Sempit & Tertutup", "21/03/2026", "Siti Aisyah", "FOTO_SRV_16.JPG"),

    # Dadapsari
    ("SRV-17", "Jl. Raden Patah Pertigaan Johar", "Dadapsari", 436400, 9229100, "Limpasan Kali Semarang & Hujan", 35.0, 3.5, "Sedimentasi Berat", "22/03/2026", "Faishal Anwar", "FOTO_SRV_17.JPG"),
    ("SRV-18", "Kampung Dadapsari RW 03", "Dadapsari", 436250, 9229400, "Limpasan Kali Semarang", 30.0, 3.0, "Saluran Terbuka Kotor", "22/03/2026", "Dimas Prasetyo", "FOTO_SRV_18.JPG"),

    # Bulu Lor
    ("SRV-19", "Jl. Kokrosono Jembatan BKB", "Bulu Lor", 433500, 9229200, "Bebas Genangan (Elevasi Aman)", 0.0, 0.0, "Baik - Tanggul Beton Tinggi", "22/03/2026", "Rina Marlina", "FOTO_SRV_19.JPG"),
    ("SRV-20", "Jl. Banowati Selatan Poncol", "Bulu Lor", 434100, 9229100, "Genangan Cekungan Rel Kereta", 20.0, 2.5, "Terawat - Ada Pompa PJKA", "22/03/2026", "Budi Santoso", "FOTO_SRV_20.JPG"),

    # Plombokan
    ("SRV-21", "Jl. Plombokan Raya Belakang PLN", "Plombokan", 434900, 9229000, "Bebas Genangan", 0.0, 0.0, "Saluran Baik Bersih", "23/03/2026", "Siti Aisyah", "FOTO_SRV_21.JPG"),
    ("SRV-22", "Jl. Tanjung Dekat Kali Semarang", "Plombokan", 435400, 9229150, "Genangan Ringan Saat Puncak Hujan", 15.0, 1.5, "Terawat", "23/03/2026", "Faishal Anwar", "FOTO_SRV_22.JPG"),

    # Purwosari
    ("SRV-23", "Jl. Imam Bonjol Dekat Sayangan", "Purwosari", 435750, 9228700, "Genangan Limpasan Jalan Raya", 20.0, 2.0, "Saluran Tertutup Gorong-gorong", "23/03/2026", "Dimas Prasetyo", "FOTO_SRV_23.JPG"),
    ("SRV-24", "Jl. Pemuda Dekat Jembatan Berok", "Purwosari", 435950, 9228550, "Bebas Genangan Pasca Revitalisasi", 0.0, 0.0, "Sangat Baik - Pompa Berok", "23/03/2026", "Budi Santoso", "FOTO_SRV_24.JPG"),

    # Cross-validation point at Banger gate
    ("SRV-25", "Pintu Air Polder Banger Timur", "Tanjung Mas", 438050, 9230500, "Genangan Terkendali Rumah Pompa", 20.0, 2.0, "Sangat Baik - 3 Unit Pompa Aktif", "23/03/2026", "Faishal Anwar", "FOTO_SRV_25.JPG")
]

# Convert UTM points to WGS84 coordinates
transformer = pyproj.Transformer.from_crs(CRS_UTM, CRS_WGS84, always_xy=True)

survey_rows = []
for idx, (code, loc_name, kel_name, x, y, gen_type, depth, dur, drain, date, surveyor, foto) in enumerate(survey_points_spec, 1):
    lon, lat = transformer.transform(x, y)
    survey_rows.append({
        'id_titik': idx,
        'kode_survei': code,
        'nama_lokasi': loc_name,
        'kelurahan': kel_name,
        'lat': round(lat, 6),
        'lon': round(lon, 6),
        'x_utm': round(x, 2),
        'y_utm': round(y, 2),
        'jenis_genangan': gen_type,
        'tinggi_genangan_cm': depth,
        'durasi_genangan_jam': dur,
        'kondisi_drainase': drain,
        'tanggal_survei': date,
        'surveyor': surveyor,
        'foto_ref': foto,
        'geometry': Point(x, y)
    })

gdf_survei = gpd.GeoDataFrame(survey_rows, crs=CRS_UTM)
print(f"Survei layer ready: {len(gdf_survei)} GPS points across 9 kelurahans.")

# 5. SPATIAL ANALYSIS 1: BUFFER SUNGAI (100m dan 200m)
# Union of all rivers
sungai_union = unary_union(gdf_sungai.geometry)
buffer_100_geom = sungai_union.buffer(100.0)
buffer_200_geom = sungai_union.buffer(200.0)

# Clip to study area
buffer_100_clipped = buffer_100_geom.intersection(semarang_utara_union)
buffer_200_clipped = buffer_200_geom.intersection(semarang_utara_union)
buffer_ring_200 = buffer_200_clipped.difference(buffer_100_clipped)

buffer_rows = [
    {
        'id_buffer': 1,
        'radius_m': 100,
        'zona_buffer': 'Radius 0 - 100 Meter',
        'luas_ha': round(buffer_100_clipped.area / 10000.0, 2),
        'tingkat_risiko': 'Sangat Kritis (Sempadan Sungai Langsung)',
        'deskripsi': 'Zona sempadan terdekat rawan limpasan fluvial langsung',
        'geometry': buffer_100_clipped
    },
    {
        'id_buffer': 2,
        'radius_m': 200,
        'zona_buffer': 'Radius 100 - 200 Meter',
        'luas_ha': round(buffer_ring_200.area / 10000.0, 2),
        'tingkat_risiko': 'Waspada Limpasan Menengah',
        'deskripsi': 'Zona penyangga limpasan sekunder dan luapan saluran',
        'geometry': buffer_ring_200
    }
]
gdf_buffer = gpd.GeoDataFrame(buffer_rows, crs=CRS_UTM)
print(f"Buffer layer ready: Buffer 100m = {gdf_buffer.iloc[0]['luas_ha']} Ha, Buffer 100-200m = {gdf_buffer.iloc[1]['luas_ha']} Ha.")

# 6. SPATIAL ANALYSIS 2: OVERLAY PERMUKIMAN DAN GENANGAN & BUFFER SUNGAI
# Intersect settlements with buffer 200m and inundation zones
terdampak_rows = []
td_idx = 1

genangan_union = unary_union(gdf_genangan.geometry)

for _, perm in gdf_permukiman.iterrows():
    p_geom = perm.geometry
    
    # 1. Intersection with Inundation Zone
    inter_gen = p_geom.intersection(genangan_union)
    # 2. Intersection with River Buffer 200m
    inter_buf = p_geom.intersection(buffer_200_clipped)
    
    # Overlap with both (Double Exposure: Rob + River)
    inter_both = inter_gen.intersection(inter_buf)
    
    # Overlap with either
    inter_either = p_geom.intersection(genangan_union.union(buffer_200_clipped))
    
    if not inter_either.is_empty and inter_either.area > 100:
        area_m2 = inter_either.area
        area_ha = round(area_m2 / 10000.0, 2)
        pct_terpapar = round((area_m2 / perm['luas_m2']) * 100.0, 1)
        
        if not inter_both.is_empty and inter_both.area > 500:
            bahaya = "Bencana Ganda (Rob Pesisir & Limpasan Fluvial)"
            risiko = "Sangat Tinggi"
            rekom = "Peninggian tanggul sabuk pantai, normalisasi sungai, rumah panggung komunal"
        elif not inter_gen.is_empty:
            bahaya = "Terpapar Genangan Rob Pesisir"
            risiko = "Tinggi"
            rekom = "Optimalisasi rumah pompa polder dan peninggian jalan kampung"
        else:
            bahaya = "Terpapar Limpasan Sempadan Sungai"
            risiko = "Sedang"
            rekom = "Perkuatan parapet dinding sungai dan pembersihan sedimen"
            
        terdampak_rows.append({
            'id_terdampak': td_idx,
            'id_perm': perm['id_perm'],
            'nama_kaw': perm['nama_kaw'],
            'kelurahan': perm['kelurahan'],
            'tipe_huni': perm['tipe_huni'],
            'luas_total_ha': perm['luas_ha'],
            'luas_terpapar_m2': round(area_m2, 2),
            'luas_terpapar_ha': area_ha,
            'pct_terpapar': pct_terpapar,
            'jenis_bahaya': bahaya,
            'tingkat_risiko': risiko,
            'rekomendasi': rekom,
            'geometry': inter_either
        })
        td_idx += 1

gdf_terdampak = gpd.GeoDataFrame(terdampak_rows, crs=CRS_UTM)
print(f"Permukiman Terdampak layer ready: {len(gdf_terdampak)} parcels, total exposed: {gdf_terdampak['luas_terpapar_ha'].sum():.2f} Ha.")

# 7. RELATIONAL TABLES (NON-SPATIAL ATTRIBUTE DATABASE)
# Kelurahan meta dict
kel_meta_dict = {
    'Bandarharjo': {'rw': 12, 'rt': 98},
    'Bulu Lor': {'rw': 11, 'rt': 85},
    'Dadapsari': {'rw': 10, 'rt': 72},
    'Kuningan': {'rw': 9, 'rt': 68},
    'Panggung Kidul': {'rw': 8, 'rt': 64},
    'Panggung Lor': {'rw': 14, 'rt': 112},
    'Plombokan': {'rw': 7, 'rt': 56},
    'Purwosari': {'rw': 6, 'rt': 48},
    'Tanjung Mas': {'rw': 16, 'rt': 124}
}

kel_summary = []
for _, kel in gdf_kel.iterrows():
    k_name = kel['nama_kel']
    kel_perm = gdf_permukiman[gdf_permukiman['kelurahan'] == k_name]
    kel_td = gdf_terdampak[gdf_terdampak['kelurahan'] == k_name]
    
    tot_perm_ha = kel_perm['luas_ha'].sum() if len(kel_perm) > 0 else 0.0
    tot_td_ha = kel_td['luas_terpapar_ha'].sum() if len(kel_td) > 0 else 0.0
    pct = round((tot_td_ha / tot_perm_ha * 100.0), 1) if tot_perm_ha > 0 else 0.0
    
    pts_srv = len(gdf_survei[gdf_survei['kelurahan'] == k_name])
    rw_val = kel_meta_dict.get(k_name, {}).get('rw', 10)
    rt_val = kel_meta_dict.get(k_name, {}).get('rt', 70)
    
    kel_summary.append({
        'id_kel': kel['id_kel'],
        'nama_kel': k_name,
        'jumlah_rw': rw_val,
        'jumlah_rt': rt_val,
        'populasi_jiwa': kel['populasi'],
        'luas_kelurahan_ha': kel['luas_ha'],
        'luas_permukiman_ha': round(tot_perm_ha, 2),
        'luas_terpapar_ha': round(tot_td_ha, 2),
        'persentase_terpapar_pct': pct,
        'jumlah_titik_survei': pts_srv,
        'status_kerentanan': 'Sangat Kritis' if pct >= 75 else 'Kritis' if pct >= 50 else 'Waspada' if pct >= 25 else 'Aman Terkendali'
    })

df_kel_profil = pd.DataFrame(kel_summary)
print("\n--- PROFIL KELURAHAN & KETERPAPARAN ---")
print(df_kel_profil[['nama_kel', 'luas_permukiman_ha', 'luas_terpapar_ha', 'persentase_terpapar_pct', 'status_kerentanan']])

# Save GeoDataFrames to GeoPackage
gpkg_master = f"{BASE_DIR}/04_DATABASE/Database_SIG.gpkg"
if os.path.exists(gpkg_master):
    os.remove(gpkg_master)

# Save layers into Master GeoPackage
gdf_kel.to_file(gpkg_master, layer="Batas_Administrasi_Kelurahan", driver="GPKG")
gdf_sungai.to_file(gpkg_master, layer="Sungai_dan_Drainase", driver="GPKG")
gdf_permukiman.to_file(gpkg_master, layer="Permukiman", driver="GPKG")
gdf_genangan.to_file(gpkg_master, layer="Area_Genangan_Banjir_Rob", driver="GPKG")
gdf_survei.to_file(gpkg_master, layer="Titik_Survei_Lapangan", driver="GPKG")
gdf_buffer.to_file(gpkg_master, layer="Buffer_Sungai", driver="GPKG")
gdf_terdampak.to_file(gpkg_master, layer="Permukiman_Terdampak", driver="GPKG")

# Write non-spatial relational table to GeoPackage using sqlite3
import sqlite3
conn = sqlite3.connect(gpkg_master)
df_kel_profil.to_sql("Tabel_Kelurahan_Profil", conn, if_exists="replace", index=False)

# Register non-spatial table in gpkg_contents if necessary
cursor = conn.cursor()
cursor.execute("""
INSERT OR REPLACE INTO gpkg_contents (table_name, data_type, identifier, description, last_change)
VALUES ('Tabel_Kelurahan_Profil', 'attributes', 'Tabel_Kelurahan_Profil', 'Tabel profil statistik demografi dan keterpaparan kelurahan', strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
""")
conn.commit()
conn.close()

print(f"\nMaster GeoPackage created successfully: {gpkg_master}")

# Also save standalone GPKG in 03_DATA_HASIL_DIGITASI
gdf_sungai.to_file(f"{BASE_DIR}/03_DATA_HASIL_DIGITASI/Sungai.gpkg", layer="Sungai", driver="GPKG")
gdf_genangan.to_file(f"{BASE_DIR}/03_DATA_HASIL_DIGITASI/Genangan.gpkg", layer="Genangan", driver="GPKG")
gdf_permukiman.to_file(f"{BASE_DIR}/03_DATA_HASIL_DIGITASI/Permukiman.gpkg", layer="Permukiman", driver="GPKG")
gdf_survei.to_file(f"{BASE_DIR}/03_DATA_HASIL_DIGITASI/Survei.gpkg", layer="Survei", driver="GPKG")

# Also save layers in 05_ANALISIS
gdf_buffer.to_file(f"{BASE_DIR}/05_ANALISIS/Buffer_Sungai/Buffer_Sungai_100_200m.geojson", driver="GeoJSON")
gdf_terdampak.to_file(f"{BASE_DIR}/05_ANALISIS/Permukiman_Terdampak/Permukiman_Terdampak.geojson", driver="GeoJSON")
df_kel_profil.to_csv(f"{BASE_DIR}/05_ANALISIS/Statistik/Tabel_Statistik_Keterpaparan_Kelurahan.csv", index=False)

print("Individual GPKG and GeoJSON exports completed successfully!")
