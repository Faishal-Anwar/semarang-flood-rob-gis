import os, zipfile
import xml.etree.ElementTree as ET

print("=== STEP 5: CREATING QGIS PROJECT (.QGZ) ===")

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"
QGIS_DIR = f"{BASE_DIR}/07_PROJECT_QGIS"
gpkg_rel = "../04_DATABASE/Database_SIG.gpkg"

# Create valid QGIS project XML (.qgs)
qgs_content = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="PEMETAAN DAN ANALISIS RISIKO BANJIR DAN ROB SEMARANG UTARA" version="3.28.0-Firenze">
  <homePath path=""/>
  <title>PEMETAAN DAN ANALISIS RISIKO BANJIR DAN ROB DI KOTA SEMARANG BAGIAN UTARA MENGGUNAKAN SISTEM INFORMASI GEOGRAFIS</title>
  <autotransaction active="0"/>
  <evaluateDefaultValues active="0"/>
  <trust active="0"/>
  <projectCrs>
    <spatialrefsys>
      <wkt>PROJCRS["WGS 84 / UTM zone 49S",BASEGEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4326]],CONVERSION["UTM zone 49S",METHOD["Transverse Mercator",ID["EPSG",9807]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",111,ANGLEUNIT["degree",0],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9996,SCALEUNIT["unity",1],ID["EPSG",8805]],PARAMETER["False easting",500000,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",10000000,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1]],USAGE[SCOPE["Engineering survey, topographic mapping."],AREA["Indonesia - onshore and offshore between 108°E and 114°E, southern hemisphere."],BBOX[-11,108,0,114]],ID["EPSG",32749]]</wkt>
      <proj4>+proj=utm +zone=49 +south +datum=WGS84 +units=m +no_defs</proj4>
      <srsid>3199</srsid>
      <srid>32749</srid>
      <authid>EPSG:32749</authid>
      <description>WGS 84 / UTM zone 49S</description>
      <projectionacronym>utm</projectionacronym>
      <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
      <geographicflag>false</geographicflag>
    </spatialrefsys>
  </projectCrs>
  <layer-tree-group>
    <customproperties>
      <Option/>
    </customproperties>
    <layer-tree-group name="06_ANALISIS" expanded="1" checked="Qt::Checked">
      <layer-tree-layer id="Permukiman_Terdampak" name="Permukiman Terdampak (Hasil Overlay)" providerKey="ogr" source="{gpkg_rel}|layername=Permukiman_Terdampak" expanded="1" checked="Qt::Checked"/>
      <layer-tree-layer id="Buffer_Sungai" name="Buffer Sungai (100m &amp; 200m)" providerKey="ogr" source="{gpkg_rel}|layername=Buffer_Sungai" expanded="0" checked="Qt::Checked"/>
    </layer-tree-group>
    <layer-tree-group name="05_SURVEI" expanded="1" checked="Qt::Checked">
      <layer-tree-layer id="Titik_Survei_Lapangan" name="Titik Survei Lapangan &amp; Genangan (25 GPS)" providerKey="ogr" source="{gpkg_rel}|layername=Titik_Survei_Lapangan" expanded="1" checked="Qt::Checked"/>
    </layer-tree-group>
    <layer-tree-group name="04_PERMUKIMAN" expanded="1" checked="Qt::Checked">
      <layer-tree-layer id="Permukiman" name="Kawasan Permukiman Penduduk" providerKey="ogr" source="{gpkg_rel}|layername=Permukiman" expanded="1" checked="Qt::Checked"/>
    </layer-tree-group>
    <layer-tree-group name="03_GENANGAN" expanded="1" checked="Qt::Checked">
      <layer-tree-layer id="Area_Genangan_Banjir_Rob" name="Area Genangan Banjir &amp; Rob" providerKey="ogr" source="{gpkg_rel}|layername=Area_Genangan_Banjir_Rob" expanded="1" checked="Qt::Checked"/>
    </layer-tree-group>
    <layer-tree-group name="02_SUNGAI_DRAINASE" expanded="1" checked="Qt::Checked">
      <layer-tree-layer id="Sungai_dan_Drainase" name="Jaringan Sungai &amp; Saluran Drainase" providerKey="ogr" source="{gpkg_rel}|layername=Sungai_dan_Drainase" expanded="1" checked="Qt::Checked"/>
    </layer-tree-group>
    <layer-tree-group name="01_ADMINISTRASI" expanded="1" checked="Qt::Checked">
      <layer-tree-layer id="Batas_Administrasi_Kelurahan" name="Batas Administrasi Kelurahan" providerKey="ogr" source="{gpkg_rel}|layername=Batas_Administrasi_Kelurahan" expanded="1" checked="Qt::Checked"/>
    </layer-tree-group>
    <customproperties/>
  </layer-tree-group>
  <projectlayers>
    <maplayer type="vector" id="Batas_Administrasi_Kelurahan" name="Batas Administrasi Kelurahan" autoRefreshEnabled="0" readOnly="0">
      <datasource>{gpkg_rel}|layername=Batas_Administrasi_Kelurahan</datasource>
      <keywordList><value></value></keywordList>
      <layername>Batas Administrasi Kelurahan</layername>
      <srs>
        <spatialrefsys>
          <authid>EPSG:32749</authid>
          <description>WGS 84 / UTM zone 49S</description>
          <projectionacronym>utm</projectionacronym>
          <ellipsoidacronym>EPSG:7030</ellipsoidacronym>
          <geographicflag>false</geographicflag>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="fill" name="0" alpha="1" clip_to_extent="1">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="251,250,245,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="outline_color" v="127,140,141,255"/>
              <prop k="outline_style" v="dash"/>
              <prop k="outline_width" v="0.6"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
    <maplayer type="vector" id="Sungai_dan_Drainase" name="Jaringan Sungai &amp; Saluran Drainase" autoRefreshEnabled="0" readOnly="0">
      <datasource>{gpkg_rel}|layername=Sungai_dan_Drainase</datasource>
      <keywordList><value></value></keywordList>
      <layername>Jaringan Sungai &amp; Saluran Drainase</layername>
      <srs>
        <spatialrefsys>
          <authid>EPSG:32749</authid>
          <description>WGS 84 / UTM zone 49S</description>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="line" name="0" alpha="1">
            <layer pass="0" class="SimpleLine" locked="0">
              <prop k="line_color" v="25,118,210,255"/>
              <prop k="line_width" v="0.8"/>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
    <maplayer type="vector" id="Permukiman" name="Kawasan Permukiman Penduduk" autoRefreshEnabled="0" readOnly="0">
      <datasource>{gpkg_rel}|layername=Permukiman</datasource>
      <keywordList><value></value></keywordList>
      <layername>Kawasan Permukiman Penduduk</layername>
      <srs>
        <spatialrefsys>
          <authid>EPSG:32749</authid>
          <description>WGS 84 / UTM zone 49S</description>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="fill" name="0" alpha="0.8">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="color" v="215,204,200,255"/>
              <prop k="outline_color" v="141,110,99,255"/>
              <prop k="outline_width" v="0.4"/>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
    <maplayer type="vector" id="Area_Genangan_Banjir_Rob" name="Area Genangan Banjir &amp; Rob" autoRefreshEnabled="0" readOnly="0">
      <datasource>{gpkg_rel}|layername=Area_Genangan_Banjir_Rob</datasource>
      <keywordList><value></value></keywordList>
      <layername>Area Genangan Banjir &amp; Rob</layername>
      <srs>
        <spatialrefsys>
          <authid>EPSG:32749</authid>
          <description>WGS 84 / UTM zone 49S</description>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="fill" name="0" alpha="0.5">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="color" v="230,126,34,255"/>
              <prop k="outline_color" v="211,84,0,255"/>
              <prop k="outline_width" v="0.5"/>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
    <maplayer type="vector" id="Titik_Survei_Lapangan" name="Titik Survei Lapangan &amp; Genangan (25 GPS)" autoRefreshEnabled="0" readOnly="0">
      <datasource>{gpkg_rel}|layername=Titik_Survei_Lapangan</datasource>
      <keywordList><value></value></keywordList>
      <layername>Titik Survei Lapangan &amp; Genangan (25 GPS)</layername>
      <srs>
        <spatialrefsys>
          <authid>EPSG:32749</authid>
          <description>WGS 84 / UTM zone 49S</description>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="marker" name="0" alpha="1">
            <layer pass="0" class="SimpleMarker" locked="0">
              <prop k="color" v="192,57,43,255"/>
              <prop k="outline_color" v="255,255,255,255"/>
              <prop k="outline_width" v="0.4"/>
              <prop k="size" v="3.5"/>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
    <maplayer type="vector" id="Buffer_Sungai" name="Buffer Sungai (100m &amp; 200m)" autoRefreshEnabled="0" readOnly="0">
      <datasource>{gpkg_rel}|layername=Buffer_Sungai</datasource>
      <keywordList><value></value></keywordList>
      <layername>Buffer Sungai (100m &amp; 200m)</layername>
      <srs>
        <spatialrefsys>
          <authid>EPSG:32749</authid>
          <description>WGS 84 / UTM zone 49S</description>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="fill" name="0" alpha="0.4">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="color" v="129,212,250,255"/>
              <prop k="outline_color" v="41,182,246,255"/>
              <prop k="outline_width" v="0.4"/>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
    <maplayer type="vector" id="Permukiman_Terdampak" name="Permukiman Terdampak (Hasil Overlay)" autoRefreshEnabled="0" readOnly="0">
      <datasource>{gpkg_rel}|layername=Permukiman_Terdampak</datasource>
      <keywordList><value></value></keywordList>
      <layername>Permukiman Terdampak (Hasil Overlay)</layername>
      <srs>
        <spatialrefsys>
          <authid>EPSG:32749</authid>
          <description>WGS 84 / UTM zone 49S</description>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <renderer-v2 type="singleSymbol" symbollevels="0">
        <symbols>
          <symbol type="fill" name="0" alpha="0.85">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="color" v="183,28,28,255"/>
              <prop k="outline_color" v="50,50,50,255"/>
              <prop k="outline_width" v="0.6"/>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
    </maplayer>
  </projectlayers>
</qgis>
"""

# Save Project_SIG.qgs
qgs_path = f"{QGIS_DIR}/Project_SIG.qgs"
with open(qgs_path, "w", encoding="utf-8") as f:
    f.write(qgs_content)

# Package into Project_SIG.qgz (ZIP containing Project_SIG.qgs)
qgz_path = f"{QGIS_DIR}/Project_SIG.qgz"
with zipfile.ZipFile(qgz_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(qgs_path, arcname="Project_SIG.qgs")

# Write README in 07_PROJECT_QGIS
readme_qgis = """PETUNJUK MEMBUKA DAN MENJALANKAN PROYEK QGIS
Proyek Tugas Besar SIG: Pemetaan Risiko Banjir dan Rob Semarang Utara

FILE UTAMA:
- Project_SIG.qgz : File proyek QGIS standar terkompresi.
- Project_SIG.qgs : Dokumen XML proyek QGIS (uncompressed backup).

PERSYARATAN SISTEM:
1. Perangkat Lunak: QGIS versi 3.20, 3.22 (LTR), 3.28 (LTR), 3.34, atau lebih baru.
2. Sistem Operasi: Windows 10/11, macOS, atau Linux Ubuntu/Debian.
3. Basis Data: File Database_SIG.gpkg terletak di folder ../04_DATABASE/Database_SIG.gpkg.

CARA MEMBUKA:
1. Buka aplikasi QGIS Desktop.
2. Klik menu Project -> Open... (atau tekan Ctrl + O).
3. Pilih file 'Project_SIG.qgz' di dalam folder 07_PROJECT_QGIS/.
4. Proyek akan memuat seluruh layer spasial secara otomatis tanpa broken path, dengan sistem koordinat WGS 84 / UTM Zone 49S (EPSG: 32749).

STRUKTUR GRUP LAYER DI QGIS:
- 06_ANALISIS         : Permukiman Terdampak (Overlay Intersect) & Buffer Sungai (100m, 200m)
- 05_SURVEI           : Titik Survei Lapangan & Genangan (25 Titik GPS)
- 04_PERMUKIMAN       : Kawasan Permukiman Penduduk
- 03_GENANGAN         : Area Genangan Banjir & Rob (Zonasi Bahaya)
- 02_SUNGAI_DRAINASE  : Jaringan Sungai Alami & Drainase
- 01_ADMINISTRASI     : Batas Administrasi Kelurahan (9 Kelurahan)
"""

with open(f"{QGIS_DIR}/README.txt", "w", encoding="utf-8") as f:
    f.write(readme_qgis)

print("Project_SIG.qgz, Project_SIG.qgs, and README.txt created successfully.")
