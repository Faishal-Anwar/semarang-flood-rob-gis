import requests, json
import geopandas as gpd
from shapely.geometry import shape

headers = {'User-Agent': 'SIG_Semarang_Utara/1.0'}
url = 'https://nominatim.openstreetmap.org/search?q=Kota+Semarang&format=geojson&polygon_geojson=1'
r = requests.get(url, headers=headers).json()
if r.get('features'):
    geom = shape(r['features'][0]['geometry'])
    gdf_semarang = gpd.GeoDataFrame([{'nama': 'Kota Semarang', 'geometry': geom}], crs="EPSG:4326").to_crs("EPSG:32749")
    gdf_semarang.to_file("/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA/02_DATA_MENTAH/Batas_Administrasi/Kota_Semarang_Inset.geojson", driver="GeoJSON")
    print("Kota Semarang inset boundary saved successfully!")
