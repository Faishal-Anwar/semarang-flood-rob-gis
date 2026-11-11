PETUNJUK MEMBUKA DAN MENJALANKAN PROYEK QGIS
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
