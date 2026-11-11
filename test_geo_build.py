import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union, voronoi_diagram

# Load the kelurahan layer we already created and saved
gdf_kel = gpd.read_file("/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA/02_DATA_MENTAH/Batas_Administrasi/Kelurahan_Semarang_Utara.geojson")
print("Loaded kelurahan count:", len(gdf_kel))
print(gdf_kel[['nama_kel', 'luas_ha', 'populasi']])
