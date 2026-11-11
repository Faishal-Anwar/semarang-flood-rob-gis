# PANDUAN PENGGUNAAN LENGKAP
## SISTEM MONITORING RISIKO BANJIR DAN ROB SEMARANG UTARA
**QGIS • WebGIS Leaflet • Dashboard Statistik • REST API FastAPI**

---

## 1. CARA MENJALANKAN SISTEM WEBGIS & BACKEND

### A. Menjalankan Melalui FastAPI Backend (Direkomendasikan)
FastAPI akan menjalankan REST API sekaligus melayani seluruh antarmuka web WebGIS:
```bash
# 1. Pindah ke direktori backend
cd "PROJECT_SIG_SEMARANG_UTARA/backend"

# 2. Instal dependensi jika diperlukan
pip install -r requirements.txt

# 3. Jalankan server FastAPI
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
Buka peramban (browser) Anda pada alamat:
- **WebGIS Portal Utama**: [http://localhost:8000](http://localhost:8000)
- **Peta Interaktif WebGIS**: [http://localhost:8000/map.html](http://localhost:8000/map.html)
- **Dashboard Statistik**: [http://localhost:8000/dashboard.html](http://localhost:8000/dashboard.html)
- **Analisis Spasial**: [http://localhost:8000/analysis.html](http://localhost:8000/analysis.html)
- **Dokumentasi Interaktif API Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

### B. Menjalankan Sebagai Website Statis Murni
Jika tidak memerlukan API, WebGIS dapat langsung dijalankan tanpa backend:
```bash
# Pindah ke direktori webgis
cd "PROJECT_SIG_SEMARANG_UTARA/webgis"

# Jalankan HTTP server bawaan Python
python3 -m http.server 8080
```
Buka peramban pada alamat [http://localhost:8080](http://localhost:8080).

---

## 2. PANDUAN PENGOPERASIAN FITUR WEBGIS INTERAKTIF (`map.html`)

1. **Memilih Peta Dasar (Basemap)**
   - Pada panel sebelah kanan atas, pilih radio button:
     - **OpenStreetMap**: Tampilan jalan, kontur pemukiman, dan fasilitas perkotaan detail standar OSM resmi (tanpa watermark/API key).
     - **Satelit Esri**: Citra satelit resolusi tinggi untuk memverifikasi kondisi aktual pesisir dan vegetasi mangrove.
     - **Topografi**: Peta relief elevasi dan topografi OpenTopoMap untuk analisis kontur ketinggian lahan pesisir.

2. **Menghidupkan / Mematikan Layer Tematik**
   - Centang atau hilangkan centang switch pada daftar layer:
     - *Batas Administrasi Kelurahan* (garis batas 9 kelurahan)
     - *Sungai & Drainase* (jaringan hidrologi 12 segmen)
     - *Area Genangan Banjir Rob* (zona genangan resmi BPBD)
     - *Buffer Sempadan Sungai 100m/200m* (koridor perlindungan sungai)
     - *Permukiman Terdampak* (hasil overlay dengan warna merah, oranye, kuning)
     - *25 Titik Survei Lapangan GPS* (titik ground truth dengan warna kedalaman air)

3. **Mengatur Transparansi Poligon**
   - Geser slider **Transparansi Poligon** (10% s/d 100%) untuk menyesuaikan opasitas layer tematik terhadap basemap satelit.

4. **Navigasi Cepat per Kelurahan**
   - Pilih nama kelurahan pada dropdown di pojok kiri atas (misalnya: *Tanjung Mas* atau *Bandarharjo*). Peta akan otomatis melakukan zoom dan memusatkan pandangan ke batas kelurahan tersebut.

5. **Pengukuran Jarak di Peta (Measure Tool)**
   - Klik tombol **"Ukur Jarak"** di bilah alat kiri atas.
   - Klik pada titik awal di peta, lalu klik pada titik-titik berikutnya (misalnya mengukur jarak rumah warga ke bibir tanggul kali).
   - Jarak total dalam meter dan kilometer akan muncul secara instan pada kotak dialog.
   - Klik **"Stop Ukur"** untuk mengakhiri pengukuran.

6. **Melihat Informasi Detail (Popup Atribut)**
   - Klik pada sembarang poligon kelurahan, segmen sungai, area genangan, atau titik survei GPS.
   - Kotak informasi pop-up akan menampilkan seluruh atribut detail (luas, populasi, elevasi, tinggi genangan, durasi surut, rekomendasi).

7. **Mengunduh Layer GeoJSON**
   - Klik tombol unduh kecil pada bagian bawah panel layer (*Terdampak*, *25 GPS*, *Sungai*, *Buffer*) untuk menyimpan file GeoJSON WGS 84 langsung ke komputer Anda.

---

## 3. PANDUAN DASHBOARD STATISTIK (`dashboard.html`)

1. **Membaca Kartu Indikator Utama (KPI)**
   - Luas Wilayah Total: **1.194,65 Ha**
   - Total Permukiman: **171,68 Ha**
   - Permukiman di Zona Rawan (eksposur statis, bukan kejadian saat ini): **120,31 Ha (70,08%)**
   - Titik Survei GPS Lapangan: **25 Titik** (Rata-rata kedalaman: 30,2 cm).

2. **Grafik Interaktif Chart.js**
   - Arahkan kursor (*hover*) ke batang grafik atau segmen lingkaran untuk melihat nilai numerik presisi dalam persentase (%) dan Hektar (Ha).

3. **Pencarian dan Filter Tabel Peringkat Wilayah**
   - Ketikkan nama kelurahan pada kotak pencarian di atas tabel (*"Cari kelurahan..."*) untuk memfilter data secara dinamis tanpa perlu me-reload halaman.

---

## 3.1 PANDUAN MONITORING NEAR-REALTIME

1. **Jalankan backend** agar monitoring memakai API:
   ```bash
   cd backend
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```
2. Buka `http://localhost:8000`. Panel monitoring akan menampilkan:
   - Muka air laut — **Open-Meteo Marine** (model pasang).
   - Curah hujan — **Open-Meteo Forecast** (model cuaca).
   - Muka air sungai — observasi lapangan jika ada, atau **simulasi**.
   - Debit sungai — **Open-Meteo Flood/GloFAS**.
   - Gelombang laut — **Open-Meteo Marine**.
   - Laporan warga — **PetaBencana.id** (7 hari).
3. Mode ditampilkan transparan: **HYBRID**, **LIVE**, **SIMULASI**, atau **SIMULASI LOKAL**.
4. Layer tematik peta (genangan, permukiman, buffer) adalah **snapshot analisis QGIS**, bukan data sensor realtime.
5. Untuk mengirim observasi nyata:
   ```bash
   cd backend
   python post_observation.py --parameter water_level --value 66 \
     --station "Sensor Kali Baru" --unit cm --source field
   ```

---

## 4. PANDUAN MEMBUKA PROJECT QGIS DESKTOP

1. Pastikan perangkat Anda telah terinstal **QGIS versi 3.22 LTR ke atas** (rekomendasi: QGIS 3.28 LTR).
2. Masuk ke folder `PROJECT_SIG_SEMARANG_UTARA/qgis/`.
3. Buka file **`Project_SIG.qgz`**.
4. Seluruh layer spasial dari `Database_SIG.gpkg` akan otomatis termuat dengan simbolisasi tematik kartografis profesional, label dinamis, dan sistem koordinat terkalibrasi pada **WGS 84 / UTM Zone 49S (EPSG:32749)**.
5. Untuk melihat layout cetak peta, buka menu:
   - **Project** $\rightarrow$ **Layouts** $\rightarrow$ **Peta_Kerentanan_Banjir_Rob**
   - **Project** $\rightarrow$ **Layouts** $\rightarrow$ **Peta_Keterpaparan_Permukiman**
   - Layout siap diekspor ke PDF/JPG pada resolusi standar kartografi 300 DPI.

---

## 5. SKRIP OTOMASI PEMELIHARAAN DATA (`scripts/`)

Jika Anda memperbarui data pada QGIS atau GeoPackage, jalankan skrip otomatisasi:
```bash
# Pindah ke direktori scripts
cd "PROJECT_SIG_SEMARANG_UTARA/scripts"

# 1. Ekspor layer GeoPackage (EPSG:32749) ke GeoJSON WGS 84 (EPSG:4326)
python3 export_geojson.py

# 2. Rekalkulasi statistik spasial & perbarui statistik.json
python3 calculate_statistics.py

# 3. Validasi integritas geometri dan kelengkapan atribut
python3 validate_data.py
```

---

## 6. PANDUAN DEPLOYMENT KE INTERNET

### Opsi A: Deployment Frontend Statis ke GitHub Pages
1. Buat repositori baru di GitHub (misal: `semarang-flood-gis`).
2. Unggah seluruh isi folder `webgis/` ke branch `main` repositori tersebut.
3. Buka menu **Settings** $\rightarrow$ **Pages** pada repositori GitHub.
4. Pilih **Source**: `Deploy from a branch` $\rightarrow$ Branch: `main` $\rightarrow$ Folder: `/ (root)`.
5. Website WebGIS Anda akan aktif secara publik pada alamat: `https://[username].github.io/semarang-flood-gis/`.

### Opsi B: Deployment Backend FastAPI ke Cloud (Render / Railway / VPS)
1. Buat akun gratis di [Render.com](https://render.com).
2. Buat **New Web Service**, hubungkan dengan repositori GitHub proyek.
3. Tetapkan **Build Command**: `pip install -r backend/requirements.txt`.
4. Tetapkan **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`.
5. Layanan API dan WebGIS akan aktif secara online dengan protokol HTTPS aman.
