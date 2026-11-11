import os
import json
import geopandas as gpd

print("=== EXPORTING GEOPACKAGE LAYERS TO WGS 84 (EPSG:4326) GEOJSON FOR WEBGIS ===")

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"
GPKG_PATH = os.path.join(BASE_DIR, "database/Database_SIG.gpkg")
WEBGIS_DATA_DIR = os.path.join(BASE_DIR, "webgis/data")
BACKEND_DATA_DIR = os.path.join(BASE_DIR, "backend/data")

os.makedirs(WEBGIS_DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DATA_DIR, exist_ok=True)

layer_mapping = {
    "Batas_Administrasi_Kelurahan": "batas_kelurahan.geojson",
    "Sungai_dan_Drainase": "sungai.geojson",
    "Permukiman": "permukiman.geojson",
    "Area_Genangan_Banjir_Rob": "area_genangan.geojson",
    "Titik_Survei_Lapangan": "titik_survei.geojson",
    "Buffer_Sungai": "buffer_sungai.geojson",
    "Permukiman_Terdampak": "permukiman_terdampak.geojson"
}

for layer_name, geojson_filename in layer_mapping.items():
    print(f"-> Processing layer '{layer_name}'...")
    try:
        gdf = gpd.read_file(GPKG_PATH, layer=layer_name)
        # Ensure CRS is set to EPSG:32749 then reproject to EPSG:4326
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=32749)
        gdf_4326 = gdf.to_crs(epsg=4326)
        
        # Save to webgis/data
        out_web = os.path.join(WEBGIS_DATA_DIR, geojson_filename)
        gdf_4326.to_file(out_web, driver="GeoJSON")
        
        # Save to backend/data
        out_back = os.path.join(BACKEND_DATA_DIR, geojson_filename)
        gdf_4326.to_file(out_back, driver="GeoJSON")
        
        print(f"   [OK] Saved {len(gdf_4326)} features to {geojson_filename}")
    except Exception as e:
        print(f"   [ERROR] Failed to export layer {layer_name}: {e}")

print("=== ALL LAYERS SUCCESSFULLY EXPORTED TO WGS 84 GEOJSON ===")
