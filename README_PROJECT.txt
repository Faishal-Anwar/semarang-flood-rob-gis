========================================================================================
TUGAS BESAR SISTEM INFORMASI GEOGRAFIS (SIG) - PROYEK KELOMPOK
========================================================================================
Judul Proyek  : Pemetaan dan Analisis Risiko Banjir dan Rob di Kota Semarang Bagian Utara
                Menggunakan Sistem Informasi Geografis (QGIS & GeoPackage)
Mata Kuliah   : Sistem Informasi Geografis (Bobot 25% Nilai Akhir)
Dosen Pengampu: Ghufron, M.Kom
Tahun Akademik: Semester Genap 2025/2026
Sistem CRS    : WGS 84 / UTM Zone 49S (EPSG:32749) - Terproyeksi Metrik
Format Data   : OGC GeoPackage (.gpkg) & Relasional Spasial SQLite

========================================================================================
IDENTITAS KELOMPOK 3
========================================================================================
1. Faishal Anwar   (NIM: 202401001) - Project Manager, Spatial Analyst & Lead Compiler
2. Budi Santoso    (NIM: 202401002) - Field Surveyor GPS (25 Titik Ground Truth)
3. Dimas Prasetyo  (NIM: 202401003) - Digitizing & Georeferencing Specialist (RMSE 0.84m)
4. Siti Aisyah     (NIM: 202401004) - Spatial Database Analyst & Topology Validator
5. Rina Marlina    (NIM: 202401005) - Cartographer & Visual Layout Specialist (300 DPI)

========================================================================================
STRUKTUR DIREKTORI STANDAR PROYEK
========================================================================================
PROJECT_SIG_SEMARANG_UTARA/
├── 01_PROPOSAL/
│   └── Proposal_SIG.pdf                  <- Dokumen proposal lengkap (3 hal, Bab 1-10)
├── 02_DATA_MENTAH/
│   ├── Batas_Administrasi/               <- Raw GeoJSON batas 9 kelurahan
│   ├── Sungai_Drainase/                  <- Raw GeoJSON 12 segmen hidrologi
│   ├── Permukiman/                       <- Raw GeoJSON 15 klaster perumahan
│   ├── Genangan/                         <- Raw GeoJSON 5 zona bahaya genangan
│   └── DEM/                              <- Metadata elevasi dan DEM digital
├── 03_DATA_HASIL_DIGITASI/
│   ├── Sungai.gpkg                       <- Layer garis sungai didigitasi (EPSG:32749)
│   ├── Permukiman.gpkg                   <- Layer poligon permukiman (EPSG:32749)
│   ├── Genangan.gpkg                     <- Layer poligon bahaya rob (EPSG:32749)
│   └── Survei.gpkg                       <- Layer titik 25 GPS lapangan (EPSG:32749)
├── 04_DATABASE/
│   ├── Database_SIG.gpkg                 <- Master Database OGC GeoPackage (8 tabel/layer)
│   ├── Kamus_Data.xlsx                   <- Kamus data atribut seluruh field & tipe data
│   └── Metadata.xlsx                     <- Standar metadata ISO 19115 lengkap
├── 05_ANALISIS/
│   ├── Buffer_Sungai/                    <- Layer buffer sungai 100m dan 200m
│   ├── Overlay_Genangan/                 <- Layer perpotongan bahaya rob
│   ├── Permukiman_Terdampak/             <- Layer permukiman di zona rawan terklasifikasi
│   └── Statistik/                        <- Rekapitulasi CSV luas zona rawan per kelurahan
├── 06_PETA/
│   ├── Peta_1.pdf                        <- Peta Tematik 1: Persebaran Banjir & Rob (Vektor)
│   ├── Peta_1.jpg                        <- Peta Tematik 1: Resolusi Tinggi 300 DPI (Cetak)
│   ├── Peta_2.pdf                        <- Peta Tematik 2: Analisis Keterpaparan (Vektor)
│   └── Peta_2.jpg                        <- Peta Tematik 2: Resolusi Tinggi 300 DPI (Cetak)
├── 07_PROJECT_QGIS/
│   ├── Project_SIG.qgz                   <- Proyek QGIS terkompresi (buka di QGIS 3.x)
│   ├── Project_SIG.qgs                   <- Proyek QGIS XML dengan relative paths
│   └── README.txt                        <- Panduan membuka & verifikasi simbologi
├── 08_LAPORAN/
│   └── Laporan_Akhir.pdf                 <- Laporan akademik komprehensif Bab I-VII (18 hal)
├── 09_PRESENTASI/
│   └── Presentasi_SIG.pptx               <- Slide presentasi 15 slide + speaker notes
├── 10_LOGBOOK/
│   └── Logbook.xlsx                      <- Logbook aktivitas 8 minggu (5 anggota)
├── 11_DOKUMENTASI/
│   ├── Georeferencing/                   <- Laporan GCP, kalkulasi residu & plot RMSE (0.84m)
│   ├── Digitasi/                         <- Rekaman digitasi snapping & vertex editing
│   ├── Survei/                           <- Laporan 25 GPS, tabel koordinat & foto lapangan
│   └── Topologi/                         <- Laporan validasi 4 aturan topologi (0 error)
└── README_PROJECT.txt                    <- File ringkasan ini

========================================================================================
JAWABAN EMPAT PERTANYAAN SPASIAL KUNCI (RUJUKAN HASIL ANALISIS)
========================================================================================
1. Pertanyaan Spasial 1 (Buffer Sungai 200m):
   - Luas sempadan sungai total (0-200m) : 656,19 Hektar (54,93% dari luas kecamatan).
   - Luas permukiman dalam buffer 200m  : 81,99 Hektar (47,76% dari total permukiman).

2. Pertanyaan Spasial 2 (Permukiman dalam Zona Genangan Rob):
   - Klaster dengan luas zona rawan terbesar: Tanah Mas/Puri Anjasmoro (Panggung Lor, 60,58 Ha),
     Lodan/Layur Lor (Bandarharjo, 21,28 Ha), Hasanudin/Brotojoyo (Panggung Kidul, 18,89 Ha),
     dan Tambak Lorok (Tanjung Mas, 18,18 Ha).

3. Pertanyaan Spasial 3 (Total Permukiman Terdampak / Overlay Intersect):
   - Total luas permukiman eksisting    : 171,68 Hektar (100%).
   - Total permukiman di zona rawan bahaya   : 120,31 Hektar (70,08% dari seluruh permukiman).
   - Rincian zonasi bahaya permukiman:
     * Bahaya Sangat Tinggi (Bencana Ganda: Rob & Fluvial): 18,18 Ha
     * Bahaya Tinggi (Rob Pasang Laut Pesisir): 75,91 Ha
     * Bahaya Sedang (Limpasan Saluran Drainase): 26,23 Ha

   - Catatan audit: nilai di atas adalah hasil overlay geometri terbaru (EPSG:32749).
     Angka 120,31 Ha/70,08% adalah eksposur statis terhadap zona rawan BPBD/InaRISK,
     bukan luas genangan atau kejadian banjir saat ini. Statistik lama 142,57 Ha/83,04%
     tidak konsisten dengan layer dan telah diganti.

4. Pertanyaan Spasial 4 (Kelurahan Paling Kritis / Prioritas Intervensi):
   - Peringkat 1 : Kelurahan Panggung Kidul (97,37% permukiman di zona rawan, 18,89 Ha)
   - Peringkat 2 : Kelurahan Panggung Lor   (95,76% permukiman di zona rawan, 60,58 Ha)
   - Peringkat 3 : Kelurahan Bandarharjo    (69,81% permukiman di zona rawan, 21,28 Ha)
   - Catatan: Tanjung Mas memiliki 18,18 Ha di zona rawan (52,20%); Panggung Lor luas zona rawan terbesar.

========================================================================================
PANDUAN MEMBUKA PROYEK DI QGIS
========================================================================================
1. Buka aplikasi QGIS (versi 3.22, 3.28, atau lebih baru).
2. Pilih menu Project -> Open, arahkan ke:
   `07_PROJECT_QGIS/Project_SIG.qgz` (atau `Project_SIG.qgs`).
3. Semua layer akan termuat secara otomatis dengan sistem koordinat EPSG:32749.
4. Simbologi telah diatur sesuai tema:
   - Batas Kelurahan (Garis batas putus-putus transparan)
   - Jaringan Sungai (Garis biru tegas dengan label nama)
   - Permukiman Terdampak (Gradasi warna Merah/Oranye/Kuning)
   - Titik Survei Lapangan (Simbol titik berkategori tinggi air)
5. Untuk memeriksa Print Layout peta:
   Buka menu Project -> Layouts -> pilih "Layout Peta 1" atau "Layout Peta 2".
========================================================================================
