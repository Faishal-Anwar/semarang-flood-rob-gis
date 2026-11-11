# SEMARANG FLOOD & ROB GIS MONITORING
## PEMETAAN DAN ANALISIS RISIKO BANJIR DAN ROB SEMARANG UTARA
**Sistem Informasi Geografis (SIG) Terpadu: Desktop QGIS + Spatial GeoPackage + Analisis Spasial + WebGIS Interaktif + Dashboard Statistik + REST API FastAPI + Laporan Akademik + Presentasi**

---

### IDENTITAS PROYEK
- **Mata Kuliah**: Sistem Informasi Geografis (SIG)
- **Dosen Pengampu**: Ghufron, M.Kom
- **Kelompok**: Kelompok 3 (Teknik Informatika)
- **Wilayah Studi**: Kecamatan Semarang Utara, Kota Semarang, Jawa Tengah
- **Sistem Koordinat Proyek**: WGS 84 / UTM Zone 49S (EPSG:32749)
- **Sistem Koordinat WebGIS**: WGS 84 (EPSG:4326)

---

## 1. RINGKASAN EKSEKUTIF HASIL ANALISIS SPASIAL
Proyek ini memetakan dan menganalisis secara saintifik risiko kebencanaan banjir dan rob pasang air laut di wilayah Kecamatan Semarang Utara. Mengintegrasikan basis data spasial standar internasional (OGC GeoPackage) dengan 4 subsistem SIG:
1. **Luas Wilayah Total**: **1.194,65 Ha** yang mencakup 9 kelurahan pesisir.
2. **Kawasan Permukiman**: **171,68 Ha** yang tersebar dalam 15 klaster perumahan dan perkampungan nelayan.
3. **Analisis Sempadan Sungai (Buffer)**: Koridor 100m mencapai 341,91 Ha dan koridor 200m mencapai 314,28 Ha (Total sempadan sungai: **656,19 Ha / 54,93%** wilayah kecamatan). Kawasan hunian yang berada dalam koridor sempadan mencapai **81,99 Ha (47,76%)**.
4. **Eksposur Permukiman di Zona Rawan (statis)**: **120,31 Ha (70,08%)** permukiman berada dalam poligon zona rawan BPBD/InaRISK — bukan luas genangan saat ini:
   - *Bahaya Sangat Tinggi (Bencana Ganda: Rob & Luapan Kali)*: 18,18 Ha
   - *Bahaya Tinggi (Rob Pasang Laut Pesisir)*: 75,91 Ha
   - *Bahaya Sedang (Limpasan Drainase Hujan)*: 26,23 Ha
5. **Prioritas Penanganan Mendesak (Prioritas 1)**:
   - **Kelurahan Panggung Kidul**: 18,89 Ha (97,37% permukiman di zona rawan)
   - **Kelurahan Panggung Lor**: 60,58 Ha (95,76% permukiman di zona rawan)
6. **Survei Ground Truth**: 25 titik koordinat GPS lapangan dengan ketinggian genangan terukur antara 15 cm s/d 65 cm (rata-rata: 30,2 cm).

> **Audit data (5 November 2026):** Statistik lama (142,57 Ha / 83,04%) tidak konsisten dengan geometri layer. Overlay dihitung ulang dari `permukiman.geojson × area_genangan.geojson` pada EPSG:32749 dan menghasilkan **120,31 Ha / 70,08%**. Angka ini adalah **eksposur statis terhadap zona rawan BPBD/InaRISK**, bukan luas genangan atau kejadian banjir saat ini. Jumlah klaster dalam zona rawan menjadi **10**, area genangan **5 poligon**, buffer **2 poligon**. Survei 25 titik memiliki rata-rata genangan **30,2 cm**; 5 titik >40 cm, 2 di antaranya berada di dalam poligon genangan dan 3 di luar — batas model perlu validasi lapangan. Proses dapat direproduksi dengan `python scripts/recompute_analysis.py`.

---

---

## 2. STRUKTUR DIREKTORI PROYEK

```text
PROJECT_SIG_SEMARANG_UTARA/
├── qgis/                         # Project QGIS Desktop (.qgz) dan file proyek
│   ├── Project_SIG.qgz
│   ├── data/
│   └── layouts/
├── database/                     # Spatial Database OGC GeoPackage & Metadata
│   ├── Database_SIG.gpkg
│   ├── metadata_iso19115.xml
│   └── kamus_data.txt
├── webgis/                       # Website WebGIS Interaktif & Dashboard
│   ├── index.html                # Beranda & Ringkasan Geospasial
│   ├── dashboard.html            # Dashboard Statistik & Grafik Chart.js
│   ├── map.html                  # Peta Interaktif Leaflet (7 Layer & Filter)
│   ├── analysis.html             # Dokumentasi Hasil Analisis Geoprocessing
│   ├── methodology.html          # Metodologi, Tim, Nilai Islam & Pusat Unduhan
│   ├── about.html                # Redirect ke methodology.html (menjaga link lama)
│   ├── assets/vendor/           # Bootstrap, FontAwesome, Leaflet, Chart.js lokal
│   ├── css/style.css            # Design system & komponen antarmuka
│   ├── js/app.js                # Navigasi cepat, reveal, counter, toast
│   ├── js/live-monitor.js       # Polling monitoring, sparkline, fallback simulasi
│   └── data/                     # Data GeoJSON WGS 84 & JSON Statistik
├── backend/                      # RESTful Geospatial API (FastAPI)
│   ├── app.py                    # API spasial + monitoring near-realtime
│   ├── post_observation.py       # Helper kirim observasi lapangan/sensor
│   ├── requirements.txt
│   └── data/
├── scripts/                      # Skrip Otomasi Pemeliharaan & Ekspor Spasial
│   ├── export_geojson.py         # Ekspor GPKG (EPSG:32749) ke GeoJSON (EPSG:4326)
│   ├── recompute_analysis.py     # Audit & recomputasi overlay eksposur zona rawan
│   ├── calculate_statistics.py   # Komputasi statistik spasial
│   └── validate_data.py          # Validasi integritas geometri & atribut
├── maps/                         # Peta Tematik Standar BIG (Resolusi Tinggi 300 DPI)
│   ├── Peta_1.pdf                # Peta Kerentanan Banjir dan Rob (PDF Cetak)
│   ├── Peta_1.jpg                # Peta Kerentanan Banjir dan Rob (JPG 300 DPI)
│   ├── Peta_2.pdf                # Peta Analisis Keterpaparan Permukiman (PDF Cetak)
│   └── Peta_2.jpg                # Peta Analisis Keterpaparan Permukiman (JPG 300 DPI)
├── proposal/                     # Proposal Proyek SIG Lengkap
│   └── Proposal_SIG.pdf          # 3 Halaman Sesuai Format Pedoman
├── report/                       # Laporan Akhir Ilmiah Komprehensif
│   └── Laporan_Akhir.pdf         # 18 Halaman (Bab I s/d VII + Lampiran)
├── presentation/                 # Bahan Paparan Sidang / Presentasi Dosen
│   └── Presentasi_SIG.pptx       # 15 Slide Widescreen + Presenter Notes
├── logbook/                      # Catatan Kontribusi Kerja Tim Mahasiswa
│   └── Logbook.xlsx              # Catatan Pembagian Tugas 5 Anggota
├── documentation/                # Dokumentasi Teknis & Panduan
│   ├── README.md
│   ├── Dokumentasi_Teknis.md
│   └── Panduan_Penggunaan.md
└── PROJECT_SIG_SEMARANG_UTARA.zip # Arsip ZIP Lengkap Seluruh Berkas
```

---

## 3. CARA MENJALANKAN WEBGIS & REST API

> Ingin publikasi online cepat? Ikuti panduan **[DEPLOY.md](DEPLOY.md)** — satu Web Service Render untuk WebGIS + API + monitoring.

### Menjalankan Backend FastAPI:
```bash
cd backend
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
Akses di browser:
- WebGIS Portal: [http://localhost:8000](http://localhost:8000)
- Peta Interaktif WebGIS: [http://localhost:8000/map.html](http://localhost:8000/map.html)
- Dashboard Statistik: [http://localhost:8000/dashboard.html](http://localhost:8000/dashboard.html)
- Form Observasi Lapangan: [http://localhost:8000/observasi.html](http://localhost:8000/observasi.html)
- API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

### Menjalankan WebGIS Statis:
```bash
cd webgis
python3 -m http.server 8765
```
Buka browser di `http://localhost:8765`.

> Catatan: server statis tidak memiliki endpoint `/api`. Halaman akan menampilkan **Mode Simulasi Lokal** yang diberi label jelas; nilai simulasi disembunyikan secara default dan dapat ditampilkan lewat tombol “Tampilkan simulasi”. Untuk data observasi nyata, jalankan FastAPI seperti di atas.

### Monitoring Near-Realtime (FastAPI)
Backend menyimpan observasi ke `backend/monitoring.db` (SQLite) dan menyajikan status monitoring:

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/monitoring/status` | Nilai terbaru, mode, timestamp, ambang batas, `data_health`, `current_condition` |
| GET | `/api/monitoring/history?hours=24` | Riwayat untuk sparkline 24 jam |
| GET | `/api/monitoring/stations` | Daftar stasiun dan parameter |
| GET | `/api/monitoring/thresholds` | Ambang, dasar kalibrasi, sumber, dan status kalibrasi |
| GET | `/api/monitoring/observations` | Riwayat observasi tersimpan |
| GET | `/api/monitoring/external` | Data model Open-Meteo (debug/transparansi) |
| GET | `/api/monitoring/reports` | Laporan warga PetaBencana.id 7 hari |
| POST | `/api/monitoring/observations` | Menerima observasi lapangan/sensor |

Contoh mengirim observasi:

```bash
curl -X POST http://localhost:8000/api/monitoring/observations \
  -H "Content-Type: application/json" \
  -d '{"station_id":"Tide Gauge Tambak Lorok","parameter":"tide_level","value":1.82,"unit":"m","source":"field"}'
```

Sumber eksternal yang terintegrasi:
- **Open-Meteo Forecast** — curah hujan (model cuaca global, diperbarui berkala).
- **Open-Meteo Marine** — muka air laut dan tinggi gelombang (model pasang global).
- **Open-Meteo Flood / GloFAS** — debit sungai model global (m³/s).
- **PetaBencana.id** — laporan banjir urun-daya warga untuk wilayah Semarang Utara (7 hari).
- Atribusi: <https://open-meteo.com/> dan <https://petabencana.id/>. Data ini adalah **model/laporan eksternal**, bukan sensor lokal.
- **Muka air sungai** belum memiliki sensor; nilainya berasal dari observasi lapangan jika tersedia, atau simulasi yang diberi label. Debit GloFAS ditampilkan sebagai indikator fluvial, bukan pengganti sensor TMA.

Mode yang ditampilkan UI:
- **LIVE** — semua parameter memiliki observasi dalam 30 menit terakhir.
- **HYBRID** — sebagian parameter sudah observasi nyata.
- **SIMULASI** — belum ada observasi; nilai demo deterministik.
- **SIMULASI LOKAL** — backend tidak terhubung saat halaman dibuka lewat server statis.

> `current_condition` adalah status indikatif dari pasang laut, curah hujan, dan laporan warga PetaBencana. Pada server statis tanpa backend, status ini ditampilkan **belum tersedia** — bukan diklaim normal. Angka **70,08%** pada halaman tematik adalah **eksposur statis** terhadap zona rawan BPBD/InaRISK, bukan luas genangan saat ini.

### Kalibrasi Ambang, Kualitas Data, dan Keamanan

- **Hujan**: ambang 10/20 mm/jam mengikuti kategori intensitas BMKG (lebat/sangat lebat).
- **Pasang laut**: ambang dihitung dari persentil 95/99 model Open-Meteo Marine 30 hari. Ini **anomali model, bukan ambang rob resmi**. Jalankan `python scripts/review_thresholds.py --write` untuk meninjau ulang.
- **Muka air sungai**: belum ada sensor TMA lokal, sehingga ambang operasional **tidak ditetapkan**.
- **Data health**: `/api/monitoring/status` mengirim `data_health` berisi status Open-Meteo, PetaBencana, sensor TMA, parameter simulasi, dan peringatan.
- **Simulasi**: nilai simulasi disembunyikan secara default; gunakan tombol “Tampilkan simulasi” pada panel monitoring untuk melihatnya.
- **Form observasi**: buka `observasi.html` (tautan juga tersedia di halaman Metodologi).
- **API key**: set `MONITORING_API_KEY` untuk mewajibkan header `X-API-Key` pada POST observasi.
- **CORS**: set `ALLOWED_ORIGINS` (dipisah koma) untuk membatasi origin. Default: localhost 8000 dan 8765.
- **Rate limit**: `RATE_LIMIT_PER_MINUTE` (default 30) membatasi POST per IP per menit.
- **Backup**: `python scripts/backup_db.py --keep 14` membuat backup SQLite konsisten di `backend/backups/`.
- **Audit otomatis**: `python scripts/check_consistency.py` dan `python scripts/check_links.py`.

Atau gunakan helper CLI:

```bash
cd backend
python post_observation.py --parameter tide_level --value 1.82 \
  --station "Tide Gauge Tambak Lorok" --unit m --source field
```

Jika ingin mewajibkan API key, set `MONITORING_API_KEY` sebelum menjalankan backend dan kirim header `X-API-Key`.

---

## 4. INTEGRASI NILAI-NILAI ISLAM
Proyek ini mengimplementasikan prinsip tauhid ekologis dan keadilan spasial:
- **QS. Al-A'raf: 56**: Larangan berbuat kerusakan di muka bumi pasca penataannya yang harmonis.
- **QS. Ar-Rum: 41**: Fenomena banjir rob dan amblesan tanah merupakan peringatan atas perbuatan eksploitasi tangan manusia yang tidak bertanggung jawab.
- **QS. An-Nisa: 58**: Prinsip amanah keilmuan geospasial tanpa rekayasa data untuk menjamin keadilan mitigasi bagi masyarakat marjinal di pesisir utara Semarang.
