# DOKUMENTASI TEKNIS SISTEM INFORMASI GEOGRAFIS (SIG)
## SISTEM MONITORING RISIKO BANJIR DAN ROB SEMARANG UTARA
**Sistem Terintegrasi: QGIS + OGC GeoPackage + Python GeoPandas + WebGIS Leaflet + FastAPI REST API**

---

## 1. SPESIFIKASI BASIS DATA SPASIAL (OGC GEOPACKAGE)
- **Nama File Basis Data**: `Database_SIG.gpkg`
- **Format**: OGC GeoPackage (SQLite 3 + WKB Geometries + RTree Spatial Index)
- **Sistem Koordinat Proyek (Desktop GIS)**: **WGS 84 / UTM Zone 49S (EPSG:32749)**
  - Satuan Unit: Meter (Proyeksi Konformal Transverse Mercator)
  - Akurasi Komputasi Luas: Metrik 2D Planar
- **Sistem Koordinat WebGIS & API**: **WGS 84 (EPSG:4326)**
  - Satuan Unit: Derajat Desimal (Lat/Lng)
  - Reproyeksi Otomatis: Transformasi datum via PROJ/GDAL

### Daftar Layer Spasial & Skema Atribut
1. **`Batas_Administrasi_Kelurahan`** (Poligon - 9 Fitur)
   - `id_kel` (TEXT, PK): Kode unik kelurahan (KEL-01 s/d KEL-09)
   - `nama_kel` (TEXT): Nama kelurahan resmi (BPS)
   - `kecamatan` (TEXT): "Semarang Utara"
   - `luas_ha` (REAL): Luas wilayah hasil kalkulasi geometri UTM (Ha)
   - `populasi` (INTEGER): Jumlah penduduk terkini (Jiwa)
   - `kepadatan_` (REAL): Kepadatan penduduk (Jiwa/Ha)
   - `tingkat_ke` (TEXT): Tingkat kerentanan wilayah
   - `pompa_pold` (TEXT): Nama fasilitas polder/pompa pengendali

2. **`Sungai_dan_Drainase`** (LineString - 12 Fitur)
   - `id_sungai` (TEXT, PK): Kode segmen saluran
   - `nama_sunga` (TEXT): Nama sungai (Banjir Kanal Barat, Kali Semarang, Kali Baru, Kali Asin, dll.)
   - `tipe_salur` (TEXT): Klasifikasi saluran (Primer / Sekunder / Kolektor Drainase)
   - `lebar_m` (REAL): Lebar penampang basah (meter)
   - `panjang_m` (REAL): Panjang segmen terdigitasi (meter)
   - `debit_m3s` (REAL): Estimasi kapasitas debit rencana (m³/s)
   - `kondisi_fi` (TEXT): Kondisi fisik tanggul & sedimentasi

3. **`Permukiman`** (Poligon - 15 Fitur)
   - `id_permuki` (TEXT, PK): Kode klaster hunian
   - `nama_pemuk` (TEXT): Nama klaster permukiman / perumahan
   - `kelurahan` (TEXT, FK): Relasi ke `Batas_Administrasi_Kelurahan`
   - `luas_ha` (REAL): Luas klaster (Ha)
   - `tipe_permu` (TEXT): Hunian Padat Nelayan / Teratur / Campuran
   - `kepadatan` (TEXT): Sangat Padat / Padat / Sedang

4. **`Area_Genangan_Banjir_Rob`** (Poligon - 5 Fitur)
   - `id_genanga` (TEXT, PK): Kode zona bahaya
   - `nama_zona` (TEXT): Nama wilayah genangan
   - `tipe_banji` (TEXT): Rob Pasang Laut / Limpasan Kali / Bencana Ganda
   - `kedalaman_` (TEXT): Kategori genangan (15-30 cm, 30-60 cm, >60 cm)
   - `luas_ha` (REAL): Luas genangan (Ha)
   - `frekuensi` (TEXT): Frekuensi kejadian (Harian Saat Pasang Purnama / Hujan Lebat)
   - `sumber_dat` (TEXT): BPBD Kota Semarang & Survei Lapangan

5. **`Titik_Survei_Lapangan`** (Point - 25 Fitur)
   - `id_survei` (TEXT, PK): Kode titik GPS (SRV-001 s/d SRV-025)
   - `kelurahan` (TEXT, FK): Lokasi kelurahan
   - `lokasi_sur` (TEXT): Alamat / nama jalan spesifik
   - `x_utm` (REAL): Koordinat X UTM Zone 49S (meter)
   - `y_utm` (REAL): Koordinat Y UTM Zone 49S (meter)
   - `elevasi_m` (REAL): Elevasi permukaan tanah (m dpl)
   - `tinggi_air` (REAL): Ketinggian genangan air terukur (cm)
   - `durasi_jam` (REAL): Durasi genangan surut (jam)
   - `penyebab_u` (TEXT): Faktor pemicu genangan
   - `foto_dokum` (TEXT): Path dokumentasi survei lapangan

6. **`Buffer_Sungai`** (Poligon - 2 Fitur)
   - `id_buffer` (TEXT, PK): Kode zona penyangga
   - `tipe_buffe` (TEXT): Buffer Sempadan Kritis 100m / Buffer Waspada 200m
   - `jarak_m` (REAL): Radius penyangga (100 / 200 meter)
   - `luas_ha` (REAL): Luas total zona penyangga (Ha)
   - `tingkat_ba` (TEXT): Klasifikasi bahaya luapan kali

7. **`Permukiman_Terdampak`** (Poligon - 13 Fitur)
   - Hasil operasi geoprocessing `Overlay Intersect` (Permukiman ∩ Area Genangan)
   - Memuat atribut gabungan hunian, kedalaman air aktual, jarak ke kali, dan status risiko.

8. **`Tabel_Kelurahan_Profil`** (Tabel Non-Spasial)
   - Tabel relasional yang dihubungkan ke layer spasial melalui Foreign Key `id_kel` (1-to-1 dan 1-to-many relationship).

---

## 2. METODOLOGI ANALISIS GEOSPASIAL
### A. Georeferencing & Uji Ketelitian Peta
- **Metode**: Transformasi Polinomial Orde 1 (Affine Transformation)
- **Jumlah Titik Kontrol (GCP)**: 6 Titik Kontrol Tanah di persimpangan jalan permanen dan muara sungai.
- **Root Mean Square Error (RMSE)**:
  $$\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n} (x_i' - x_i)^2 + (y_i' - y_i)^2} = 0,840 \text{ meter}$$
- Nilai 0,840 meter jauh melampaui standar ketelitian peta skala 1:25.000 (batas maksimum toleransi 2,50 meter).

### B. Pemodelan Proximity (Buffer Sempadan Sungai)
Mengacu pada Permen PUPR No. 28/PRT/M/2015 tentang Penetapan Garis Sempadan Sungai:
- Koridor Kritis: Radius 100 meter ($r = 100\text{ m}$)
- Koridor Pengawasan / Waspada: Radius 200 meter ($r = 200\text{ m}$)
Hasil komputasi: Luas sempadan 100m = 341,91 Ha; luas sempadan 200m = 314,28 Ha; total = 656,19 Ha (54,93% luas daratan Semarang Utara).

### C. Pemodelan Overlay Intersect & Eksposur Zona Rawan
Operasi Boolean AND Spasial:
$$\text{Permukiman Terdampak} = \text{Permukiman} \cap \text{Area Genangan}$$
- Total Permukiman: 171,68 Ha
- Total Permukiman dalam Zona Rawan (eksposur statis): 120,31 Ha (70,08%)
- Catatan: angka ini bukan luas genangan/kejadian saat ini.
- Klasifikasi Bahaya:
  - Sangat Tinggi (Bencana Ganda: Rob + Luapan Sungai): 18,18 Ha (10,59%)
  - Tinggi (Rob Pasang Laut Pesisir): 75,91 Ha (44,22%)
  - Sedang (Limpasan Saluran Drainase): 26,23 Ha (15,28%)
  - Di Luar Zona Rawan (BPBD): 51,36 Ha (29,91%)

---

## 3. ARSITEKTUR REST API FASTAPI
Backend RESTful API dibangun menggunakan framework Python **FastAPI** dengan spesifikasi:
- **Host**: `0.0.0.0`
- **Port Default**: `8000`
- **Format Respons**: GeoJSON RFC 7946 / Standard JSON
- **CORS**: Diaktifkan (`allow_origins=["*"]`) untuk integrasi lintas platform

### Dokumentasi Endpoint:
| Metode | Endpoint | Deskripsi | Format Output |
|---|---|---|---|
| GET | `/api` | Informasi sistem, metadata, dan daftar endpoint | JSON |
| GET | `/api/kelurahan` | Batas poligon administrasi 9 kelurahan | GeoJSON FeatureCollection |
| GET | `/api/sungai` | Jaringan garis 12 saluran sungai dan drainase | GeoJSON FeatureCollection |
| GET | `/api/genangan` | Poligon bahaya genangan rob dan banjir BPBD | GeoJSON FeatureCollection |
| GET | `/api/permukiman`| Poligon seluruh kawasan permukiman | GeoJSON FeatureCollection |
| GET | `/api/survei` | 25 titik survei GPS ground truth lapangan | GeoJSON FeatureCollection |
| GET | `/api/buffer` | Poligon koridor sempadan sungai 100m & 200m | GeoJSON FeatureCollection |
| GET | `/api/analisis` | Poligon permukiman di zona rawan hasil overlay | GeoJSON FeatureCollection |
| GET | `/api/statistik` | Data ringkasan KPI, agregasi luas, dan ranking | JSON |
| GET | `/api/kelurahan/{id}` | Detail profil, demografi, dan status kelurahan | JSON |
| GET | `/api/health` | Health check backend dan jumlah observasi | JSON |
| GET | `/api/monitoring/status` | Status near-realtime, nilai terbaru, mode, timestamp, `data_health`, dan `current_condition` | JSON |
| GET | `/api/monitoring/thresholds` | Ambang, dasar kalibrasi, sumber, dan status kalibrasi | JSON |
| GET | `/api/monitoring/history` | Riwayat observasi/demo 24 jam untuk sparkline | JSON |
| GET | `/api/monitoring/stations` | Daftar stasiun, parameter, dan ambang batas | JSON |
| GET | `/api/monitoring/observations` | Riwayat observasi tersimpan | JSON |
| GET | `/api/monitoring/external` | Data model Open-Meteo untuk transparansi | JSON |
| POST | `/api/monitoring/observations` | Menerima observasi lapangan/sensor (rate limit + API key opsional) | JSON |
| GET | `/api/monitoring/reports` | Laporan warga PetaBencana.id dalam 7 hari | JSON/GeoJSON |
| GET | `/` | Antarmuka pengguna WebGIS interaktif utama | HTML/CSS/JS |

### Monitoring Near-Realtime
- Observasi disimpan di `backend/monitoring.db` (SQLite, dibuat otomatis).
- Mode UI: **LIVE** (observasi <30 menit), **HYBRID**, **SIMULASI**, dan **SIMULASI LOKAL** saat backend tidak terhubung.
- Endpoint POST menerima `station_id`, `parameter` (`tide_level` / `water_level` / `rainfall`), `value`, `unit`, `source`, dan opsional `recorded_at`, `lat`, `lon`.
- Jika `MONITORING_API_KEY` diatur, header `X-API-Key` wajib dikirim.
- Frontend memanggil endpoint setiap 30 detik dan menampilkan timestamp, sumber, serta status koneksi secara transparan.
- Sumber eksternal: Open-Meteo Forecast/Marine/Flood (GloFAS) dan PetaBencana.id; atribusi ditampilkan pada dokumentasi dan UI.

---

## 4. INTEGRASI NILAI-NILAI ISLAM
Proyek ini mengintegrasikan 3 pilar etika Islam dalam rekayasa geospasial:
1. **Prinsip Khilafah & Larangan Kerusakan Lingkungan (QS. Al-A'raf: 56)**
   Menjaga kelestarian daratan dan sempadan sungai sebagai titipan Allah SWT, menolak konversi lahan semena-mena yang memicu kerentanan banjir.
2. **Koreksi Terhadap Perbuatan Manusia (QS. Ar-Rum: 41)**
   Banjir rob dan amblesan tanah di Semarang Utara merupakan bukti empiris perbuatan tangan manusia akibat eksploitasi air tanah berlebih dan perusakan sabuk mangrove.
3. **Integritas, Kejujuran Ilmiah & Amanah Spasial (QS. An-Nisa: 58)**
   Menjaga validitas dan akurasi komputasi data spasial tanpa rekayasa angka (zero falsification), agar hasil kebijakan perlindungan masyarakat pesisir tepat sasaran demi kemaslahatan umat (*hifz an-nafs & hifz al-mal*).


## Kalibrasi Ambang dan Keamanan Operasional

- **Hujan**: kategori BMKG 10/20 mm/jam.
- **Pasang laut**: persentil 95/99 Open-Meteo Marine 30 hari melalui `scripts/review_thresholds.py --write`; bersifat anomali model, bukan ambang resmi BMKG/BPBD.
- **Muka air sungai**: tidak ada sensor TMA lokal, sehingga ambang operasional tidak ditetapkan dan nilai simulasi disembunyikan secara default.
- **API key**: `MONITORING_API_KEY`; header `X-API-Key` untuk POST.
- **CORS**: `ALLOWED_ORIGINS`.
- **Rate limit**: `RATE_LIMIT_PER_MINUTE` (default 30 POST per IP per menit).
- **Backup**: `scripts/backup_db.py --keep 14`.
- **Audit**: `scripts/check_consistency.py`, `scripts/check_links.py`.
