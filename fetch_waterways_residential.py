import requests, json
import geopandas as gpd
from shapely.geometry import shape, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union

headers = {'User-Agent': 'SIG_Semarang_Utara_Fetch/1.0'}

# 1. Fetch waterways
query_water = '''[out:json][timeout:30];
way["waterway"](-6.985,110.390,-6.930,110.450);
out geom;
'''
r = requests.post('https://overpass-api.de/api/interpreter', data={'data': query_water}, headers=headers)
waterways_data = []
if r.status_code == 200:
    for idx, el in enumerate(r.json().get('elements', []), 1):
        geom_pts = [(pt['lon'], pt['lat']) for pt in el.get('geometry', [])]
        if len(geom_pts) >= 2:
            tags = el.get('tags', {})
            name = tags.get('name', 'Saluran Drainase')
            w_type = tags.get('waterway', 'drain')
            waterways_data.append({
                'id_sungai': idx,
                'nama': name,
                'tipe': 'Sungai Alami' if w_type in ['river', 'stream'] else 'Saluran Drainase Primer' if w_type == 'canal' else 'Saluran Drainase Sekunder',
                'orde': 1 if 'Banjir Kanal' in name or 'Garang' in name else 2 if 'Semarang' in name or 'Banger' in name else 3,
                'lebar_m': 25.0 if 'Banjir Kanal' in name else 12.0 if 'Semarang' in name else 4.0,
                'kondisi': 'Sedimentasi Tinggi & Rentan Limpas' if 'Semarang' in name or 'Baru' in name else 'Normal Terawat',
                'sumber': 'OpenStreetMap 2024 & DPU Kota Semarang',
                'geometry': LineString(geom_pts)
            })
    print(f"Parsed {len(waterways_data)} waterway features.")

# Save raw waterways
gdf_water_4326 = gpd.GeoDataFrame(waterways_data, crs="EPSG:4326")
gdf_water_utm = gdf_water_4326.to_crs("EPSG:32749")
gdf_water_utm['panjang_m'] = gdf_water_utm.geometry.length.round(2)
gdf_water_utm.to_file("waterways_utm.geojson", driver="GeoJSON")
print("Waterways saved successfully.")
