import os, sys, json, requests
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, shape
from shapely.ops import unary_union
import pyproj

print("Starting spatial data acquisition and processing for Semarang Utara...")

# 1. Coordinate Reference Systems
CRS_WGS84 = "EPSG:4326"
CRS_UTM49S = "EPSG:32749"

# Output directories
base_dir = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"
os.makedirs(f"{base_dir}/01_PROPOSAL", exist_ok=True)
os.makedirs(f"{base_dir}/02_DATA_MENTAH/Batas_Administrasi", exist_ok=True)
os.makedirs(f"{base_dir}/02_DATA_MENTAH/Sungai_Drainase", exist_ok=True)
os.makedirs(f"{base_dir}/02_DATA_MENTAH/Genangan", exist_ok=True)
os.makedirs(f"{base_dir}/02_DATA_MENTAH/Permukiman", exist_ok=True)
os.makedirs(f"{base_dir}/02_DATA_MENTAH/DEM", exist_ok=True)
os.makedirs(f"{base_dir}/03_DATA_HASIL_DIGITASI", exist_ok=True)
os.makedirs(f"{base_dir}/04_DATABASE", exist_ok=True)
os.makedirs(f"{base_dir}/05_ANALISIS/Buffer_Sungai", exist_ok=True)
os.makedirs(f"{base_dir}/05_ANALISIS/Overlay_Genangan", exist_ok=True)
os.makedirs(f"{base_dir}/05_ANALISIS/Permukiman_Terdampak", exist_ok=True)
os.makedirs(f"{base_dir}/05_ANALISIS/Statistik", exist_ok=True)
os.makedirs(f"{base_dir}/06_PETA", exist_ok=True)
os.makedirs(f"{base_dir}/07_PROJECT_QGIS", exist_ok=True)
os.makedirs(f"{base_dir}/08_LAPORAN", exist_ok=True)
os.makedirs(f"{base_dir}/09_PRESENTASI", exist_ok=True)
os.makedirs(f"{base_dir}/10_LOGBOOK", exist_ok=True)
os.makedirs(f"{base_dir}/11_DOKUMENTASI/Georeferencing", exist_ok=True)
os.makedirs(f"{base_dir}/11_DOKUMENTASI/Digitasi", exist_ok=True)
os.makedirs(f"{base_dir}/11_DOKUMENTASI/Survei", exist_ok=True)
os.makedirs(f"{base_dir}/11_DOKUMENTASI/Topologi", exist_ok=True)

# Fetch Kelurahan Boundaries
kel_meta = {
    'Bandarharjo': {'pop': 23410, 'rw': 12, 'rt': 98},
    'Bulu Lor': {'pop': 14850, 'rw': 11, 'rt': 85},
    'Dadapsari': {'pop': 11200, 'rw': 10, 'rt': 72},
    'Kuningan': {'pop': 12900, 'rw': 9, 'rt': 68},
    'Panggung Kidul': {'pop': 10450, 'rw': 8, 'rt': 64},
    'Panggung Lor': {'pop': 15600, 'rw': 14, 'rt': 112},
    'Plombokan': {'pop': 9800, 'rw': 7, 'rt': 56},
    'Purwosari': {'pop': 8350, 'rw': 6, 'rt': 48},
    'Tanjung Mas': {'pop': 31250, 'rw': 16, 'rt': 124}
}

headers = {'User-Agent': 'SIG_Semarang_Utara_Project/1.0'}
kel_geoms = []

for idx, (k_name, k_info) in enumerate(kel_meta.items(), 1):
    url = f'https://nominatim.openstreetmap.org/search?q=Kelurahan+{k_name}+Semarang&format=geojson&polygon_geojson=1'
    try:
        r = requests.get(url, headers=headers, timeout=15).json()
        if r.get('features'):
            geom = shape(r['features'][0]['geometry'])
            kel_geoms.append({
                'id_kel': idx,
                'nama_kel': k_name,
                'kecamatan': 'Semarang Utara',
                'kab_kota': 'Kota Semarang',
                'provinsi': 'Jawa Tengah',
                'populasi': k_info['pop'],
                'jumlah_rw': k_info['rw'],
                'jumlah_rt': k_info['rt'],
                'sumber': 'Ina-Geoportal / OSM OpenStreetMap 2024',
                'geometry': geom
            })
            print(f"Fetched kelurahan: {k_name}")
    except Exception as e:
        print(f"Error fetching {k_name}: {e}")

gdf_kel_4326 = gpd.GeoDataFrame(kel_geoms, crs=CRS_WGS84)
# Project to UTM 49S
gdf_kel_utm = gdf_kel_4326.to_crs(CRS_UTM49S)
# Calculate area
gdf_kel_utm['luas_m2'] = gdf_kel_utm.geometry.area
gdf_kel_utm['luas_ha'] = (gdf_kel_utm['luas_m2'] / 10000.0).round(2)
gdf_kel_utm['kepadatan'] = (gdf_kel_utm['populasi'] / gdf_kel_utm['luas_ha']).round(1)

# Semarang Utara district boundary (dissolved)
gdf_kec_utm = gdf_kel_utm.dissolve(by='kecamatan').reset_index()
gdf_kec_utm['nama_kec'] = 'Semarang Utara'
gdf_kec_utm['luas_ha'] = (gdf_kec_utm.geometry.area / 10000.0).round(2)

print(f"Total Semarang Utara area: {gdf_kec_utm['luas_ha'].iloc[0]} Ha")

# Save raw admin boundaries
gdf_kel_utm.to_file(f"{base_dir}/02_DATA_MENTAH/Batas_Administrasi/Kelurahan_Semarang_Utara.geojson", driver="GeoJSON")
print("Admin boundaries saved.")
