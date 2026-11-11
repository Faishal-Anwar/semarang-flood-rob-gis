import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

gpkg = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA/04_DATABASE/Database_SIG.gpkg"
gdf = gpd.read_file(gpkg, layer="Permukiman_Terdampak")

def to_multipolygon(geom):
    if geom is None or geom.is_empty:
        return geom
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    elif isinstance(geom, MultiPolygon):
        return geom
    elif geom.geom_type == 'GeometryCollection':
        polys = [g for g in geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
        flat_polys = []
        for p in polys:
            if isinstance(p, Polygon):
                flat_polys.append(p)
            elif isinstance(p, MultiPolygon):
                flat_polys.extend(p.geoms)
        return MultiPolygon(flat_polys)
    return geom

gdf['geometry'] = gdf['geometry'].apply(to_multipolygon)
gdf = gdf[gdf['geometry'].notnull() & ~gdf['geometry'].is_empty]
gdf.to_file(gpkg, layer="Permukiman_Terdampak", driver="GPKG")
print("Standardized Permukiman_Terdampak to MultiPolygon.")
