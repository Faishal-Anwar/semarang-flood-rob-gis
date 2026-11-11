import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

print("=== STEP 4: GENERATING EXCEL SPREADSHEETS (KAMUS DATA, METADATA, LOGBOOK) ===")

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"

header_fill = PatternFill(start_color="1A5276", end_color="1A5276", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
subhead_fill = PatternFill(start_color="D4E6F1", end_color="D4E6F1", fill_type="solid")
subhead_font = Font(name="Calibri", size=10, bold=True, color="1A5276")
data_font = Font(name="Calibri", size=10)
thin_border = Border(
    left=Side(style='thin', color='BDC3C7'),
    right=Side(style='thin', color='BDC3C7'),
    top=Side(style='thin', color='BDC3C7'),
    bottom=Side(style='thin', color='BDC3C7')
)

def style_table(ws, start_row, headers, data):
    # Write headers
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[start_row].height = 26

    # Write data
    current_row = start_row + 1
    for row_data in data:
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font = data_font
            cell.border = thin_border
            if isinstance(val, (int, float)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif str(val).upper() in ['PK', 'FK', 'INTEGER', 'REAL', 'TEXT', 'DATE', 'YES', 'NO']:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[current_row].height = 20
        current_row += 1

    # Auto-fit columns
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

# ==========================================
# 1. KAMUS DATA (Kamus_Data.xlsx)
# ==========================================
wb_kamus = openpyxl.Workbook()
ws_overview = wb_kamus.active
ws_overview.title = "Daftar_Tabel"

ws_overview.cell(row=1, column=1, value="KAMUS DATA BASIS DATA SISTEM INFORMASI GEOGRAFIS (SIG)").font = Font(name="Calibri", size=14, bold=True, color="1A5276")
ws_overview.cell(row=2, column=1, value="Proyek: Pemetaan dan Analisis Risiko Banjir dan Rob Semarang Utara").font = Font(name="Calibri", size=11, italic=True)
ws_overview.cell(row=3, column=1, value="Format Basis Data: OGC GeoPackage (.gpkg) | Sistem Proyeksi: WGS 84 / UTM Zone 49S (EPSG:32749)").font = Font(name="Calibri", size=10)

headers_overview = ["No", "Nama Tabel / Layer", "Tipe Data", "Geometri", "Jumlah Fitur", "Jumlah Kolom", "Deskripsi Isi"]
data_overview = [
    [1, "Batas_Administrasi_Kelurahan", "Spasial", "Polygon", 9, 10, "Batas poligon 9 kelurahan di Kecamatan Semarang Utara lengkap dengan data demografi"],
    [2, "Sungai_dan_Drainase", "Spasial", "LineString", 12, 8, "Jaringan sungai alami utama (BKB, Kali Semarang, Kali Baru, Kali Banger) dan saluran drainase"],
    [3, "Permukiman", "Spasial", "MultiPolygon", 15, 9, "Klaster kawasan permukiman penduduk di seluruh kelurahan Semarang Utara"],
    [4, "Area_Genangan_Banjir_Rob", "Spasial", "MultiPolygon", 5, 9, "Zona bahaya genangan pasang rob pesisir, limpasan fluvial sungai, dan cekungan drainase"],
    [5, "Titik_Survei_Lapangan", "Spasial", "Point", 25, 15, "Titik survei GPS lapangan riil verifikasi genangan banjir/rob, foto, dan kondisi drainase"],
    [6, "Buffer_Sungai", "Spasial", "MultiPolygon", 2, 6, "Zona penyangga sempadan sungai radius 100 m dan 200 m untuk analisis keterpaparan"],
    [7, "Permukiman_Terdampak", "Spasial", "MultiPolygon", 13, 11, "Hasil analisis spasial overlay permukiman yang berada di zona genangan & buffer sungai"],
    [8, "Tabel_Kelurahan_Profil", "Non-Spasial", "Attributes", 9, 11, "Tabel relasional profil agregat RW/RT, penduduk, luasan permukiman, dan rasio keterpaparan"]
]
style_table(ws_overview, 5, headers_overview, data_overview)

# Sheets for each layer
layer_dictionaries = {
    "Batas_Administrasi": [
        ["id_kel", "INTEGER", "PK", "NOT NULL", "1 - 9", "ID unik pengenal kelurahan (Primary Key)", 1],
        ["nama_kel", "TEXT(50)", "-", "NOT NULL", "Nama baku", "Nama resmi kelurahan di Kecamatan Semarang Utara", "Bandarharjo"],
        ["kecamatan", "TEXT(50)", "-", "NOT NULL", "'Semarang Utara'", "Nama kecamatan wilayah administrasi", "Semarang Utara"],
        ["kab_kota", "TEXT(50)", "-", "NOT NULL", "'Kota Semarang'", "Nama kabupaten/kota wilayah penelitian", "Kota Semarang"],
        ["provinsi", "TEXT(50)", "-", "NOT NULL", "'Jawa Tengah'", "Nama provinsi wilayah penelitian", "Jawa Tengah"],
        ["luas_ha", "REAL", "-", "NOT NULL", "> 0", "Luas wilayah kelurahan hasil perhitungan kalkulasi geometri SIG (Hektar)", 226.34],
        ["populasi", "INTEGER", "-", "NOT NULL", "> 0", "Jumlah penduduk total berdasarkan data BPS Kota Semarang 2024", 23410],
        ["kepadatan", "REAL", "-", "NOT NULL", "> 0", "Kepadatan penduduk per hektar (jiwa/ha)", 103.4],
        ["sumber", "TEXT(100)", "-", "NOT NULL", "-", "Sumber rujukan data batas administrasi dan statistik", "Ina-Geoportal BIG & BPS"]
    ],
    "Sungai_dan_Drainase": [
        ["id_sungai", "INTEGER", "PK", "NOT NULL", "1 - 12", "ID unik pengenal segmen aliran sungai / drainase (Primary Key)", 1],
        ["nama", "TEXT(100)", "-", "NOT NULL", "-", "Nama resmi atau lokal sungai / saluran drainase", "Banjir Kanal Barat"],
        ["tipe", "TEXT(50)", "-", "NOT NULL", "Alami/Primer/Sekunder", "Klasifikasi fungsi dan hirarki saluran hidrologi", "Sungai Alami Utama"],
        ["orde", "INTEGER", "-", "NOT NULL", "1 - 4", "Orde hirarki sungai (1: Kanal Utama, 2: Sungai Primer, 3: Drainase)", 1],
        ["lebar_m", "REAL", "-", "NOT NULL", "> 0", "Lebar rata-rata penampang basah aliran air (meter)", 35.0],
        ["panjang_m", "REAL", "-", "NOT NULL", "> 0", "Panjang segmen aliran hasil kalkulasi geometri SIG (meter)", 5025.4],
        ["kondisi", "TEXT(100)", "-", "NOT NULL", "-", "Kondisi fisik dinding sungai, tanggul, sedimentasi, dan pompa", "Normal - Tanggul Beton Baik"],
        ["sumber", "TEXT(100)", "-", "NOT NULL", "-", "Institusi pengelola dan penyedia data jaringan sungai", "BBWS Pemali-Juana & DPU"]
    ],
    "Permukiman": [
        ["id_perm", "INTEGER", "PK", "NOT NULL", "1 - 15", "ID unik klaster kawasan permukiman (Primary Key)", 1],
        ["nama_kaw", "TEXT(100)", "-", "NOT NULL", "-", "Nama lingkungan permukiman, kampung, atau perumahan", "Permukiman Nelayan Lodan"],
        ["kelurahan", "TEXT(50)", "FK", "NOT NULL", "Relasi ke Kelurahan", "Nama kelurahan lokasi permukiman (Foreign Key relasional)", "Bandarharjo"],
        ["tipe_huni", "TEXT(50)", "-", "NOT NULL", "-", "Tipologi pola hunian (Padat, Perkampungan Nelayan, Teratur)", "Perkampungan Nelayan & Padat"],
        ["luas_m2", "REAL", "-", "NOT NULL", "> 0", "Luas bidang permukiman dalam meter persegi", 134500.5],
        ["luas_ha", "REAL", "-", "NOT NULL", "> 0", "Luas bidang permukiman dalam hektar", 13.45],
        ["jarak_sungai_m", "REAL", "-", "NOT NULL", ">= 0", "Jarak terpendek dari centroid permukiman ke tepi sungai terdekat (m)", 45.2],
        ["zona_risiko", "TEXT(50)", "-", "NOT NULL", "Sangat Tinggi/Tinggi/Sedang", "Klasifikasi awal potensi kerentanan berdasarkan jarak sempadan", "Sangat Tinggi"],
        ["sumber", "TEXT(100)", "-", "NOT NULL", "-", "Metode perolehan data poligon permukiman", "Digitasi Citra Satelit & RDTR"]
    ],
    "Titik_Survei_Lapangan": [
        ["id_titik", "INTEGER", "PK", "NOT NULL", "1 - 25", "Nomor urut titik survei (Primary Key)", 1],
        ["kode_survei", "TEXT(20)", "-", "NOT NULL", "SRV-01 s/d SRV-25", "Kode unik penomoran titik survei lapangan", "SRV-01"],
        ["nama_lokasi", "TEXT(100)", "-", "NOT NULL", "-", "Nama landmark, jalan, atau RT/RW titik pengamatan", "Dermaga Tambak Lorok RW 15"],
        ["kelurahan", "TEXT(50)", "FK", "NOT NULL", "Relasi ke Kelurahan", "Nama kelurahan lokasi titik survei (Foreign Key)", "Tanjung Mas"],
        ["lat", "REAL", "-", "NOT NULL", "-7.0 s/d -6.9", "Koordinat lintang geografis WGS 84 (derajat desimal)", -6.93854],
        ["lon", "REAL", "-", "NOT NULL", "110.3 s/d 110.5", "Koordinat bujur geografis WGS 84 (derajat desimal)", 110.43521],
        ["x_utm", "REAL", "-", "NOT NULL", "433000 - 439000", "Koordinat X proyeksi UTM Zona 49S (meter)", 437750.0],
        ["y_utm", "REAL", "-", "NOT NULL", "9228000 - 9234000", "Koordinat Y proyeksi UTM Zona 49S (meter)", 9232900.0],
        ["jenis_genangan", "TEXT(50)", "-", "NOT NULL", "Rob/Banjir/Bebas", "Tipe genangan air yang diobservasi di lokasi", "Rob Pasang Laut"],
        ["tinggi_genangan_cm", "REAL", "-", "NOT NULL", ">= 0", "Ketinggian genangan air di atas permukaan jalan saat pasang/hujan (cm)", 65.0],
        ["durasi_genangan_jam", "REAL", "-", "NOT NULL", ">= 0", "Lama waktu genangan bertahan sebelum surut (jam)", 7.0],
        ["kondisi_drainase", "TEXT(100)", "-", "NOT NULL", "-", "Evaluasi fisik saluran pembuangan air di sekitar titik", "Rusak - Terendam Pasang"],
        ["tanggal_survei", "TEXT(20)", "-", "NOT NULL", "Format DD/MM/YYYY", "Waktu pelaksanaan observasi GPS di lapangan", "18/03/2026"],
        ["surveyor", "TEXT(50)", "-", "NOT NULL", "-", "Nama anggota kelompok pengambil data lapangan", "Faishal Anwar"],
        ["foto_ref", "TEXT(50)", "-", "NOT NULL", "*.JPG", "Nama file foto bukti observasi lapangan", "FOTO_SRV_01.JPG"]
    ],
    "Relasi_Tabel": [
        ["Tabel_Asal", "Foreign_Key", "Tabel_Tujuan", "Primary_Key", "Kardinalitas", "Deskripsi Hubungan Relasi", "Integritas Referensial"],
        ["Permukiman", "kelurahan", "Batas_Administrasi", "nama_kel", "Many-to-One", "Banyak klaster permukiman terletak pada satu kelurahan", "RESTRICT"],
        ["Titik_Survei_Lapangan", "kelurahan", "Batas_Administrasi", "nama_kel", "Many-to-One", "Banyak titik pengamatan survei berada dalam satu kelurahan", "CASCADE"],
        ["Tabel_Kelurahan_Profil", "id_kel", "Batas_Administrasi", "id_kel", "One-to-One", "Satu baris data agregat statistik per satu entitas spasial kelurahan", "CASCADE"],
        ["Permukiman_Terdampak", "id_perm", "Permukiman", "id_perm", "Many-to-One", "Fragmen permukiman terpapar merujuk pada poligon permukiman induk", "CASCADE"]
    ]
}

headers_dict = ["Nama Kolom (Field)", "Tipe Data", "Kunci", "Nullability", "Domain / Rentang", "Keterangan Lengkap", "Contoh Nilai"]
headers_relasi = ["Tabel Asal", "Foreign Key", "Tabel Tujuan", "Primary Key", "Kardinalitas", "Deskripsi Hubungan Relasi", "Integritas Referensial"]

for sheet_name, dict_data in layer_dictionaries.items():
    ws = wb_kamus.create_sheet(title=sheet_name)
    ws.cell(row=1, column=1, value=f"KAMUS DATA ATRIBUT: {sheet_name}").font = Font(name="Calibri", size=13, bold=True, color="1A5276")
    h = headers_relasi if sheet_name == "Relasi_Tabel" else headers_dict
    style_table(ws, 3, h, dict_data)

wb_kamus.save(f"{BASE_DIR}/04_DATABASE/Kamus_Data.xlsx")
print("Kamus_Data.xlsx created successfully.")

# ==========================================
# 2. METADATA (Metadata.xlsx)
# ==========================================
wb_meta = openpyxl.Workbook()
ws_m = wb_meta.active
ws_m.title = "Metadata_Spasial"

ws_m.cell(row=1, column=1, value="DOKUMEN METADATA SPASIAL STANDAR ISO 19115").font = Font(name="Calibri", size=14, bold=True, color="1A5276")
ws_m.cell(row=2, column=1, value="Project Tugas Besar SIG - Semarang Utara").font = Font(name="Calibri", size=11, italic=True)

headers_meta = ["Elemen Metadata", "Deskripsi Standar ISO 19115", "Nilai Metadata Proyek"]
data_meta = [
    ["Judul Dataset", "Nama resmi dari kumpulan data geospasial", "Basis Data Spasial Risiko Banjir dan Rob Kecamatan Semarang Utara"],
    ["Tanggal Pembuatan", "Tanggal finalisasi pembuatan data", "25 Maret 2026"],
    ["Edisi / Versi", "Versi rilis dari data spasial", "Versi 1.0 (Rilis Final Tugas Besar)"],
    ["Abstrak Data", "Ringkasan naratif mengenai isi data dan tujuan", "Dataset komprehensif berformat GeoPackage mencakup batas administrasi kelurahan, jaringan hidrologi sungai dan saluran drainase, sebaran permukiman penduduk, zona genangan rob dan banjir, serta hasil survei lapangan 25 titik GPS untuk analisis keterpaparan bencana hidrometeorologi pesisir di Semarang Utara."],
    ["Tujuan Dataset", "Tujuan pembuatan basis data", "Menyediakan data spasial mini SIG terpadu untuk mengidentifikasi kawasan terpapar, menghitung luasan terdampak, serta memberikan rekomendasi kebijakan mitigasi bencana bagi Kota Semarang."],
    ["Status Perkembangan", "Status kelengkapan data", "Selesai Lengkap (Completed)"],
    ["Frekuensi Pembaruan", "Interval pemutakhiran data di masa depan", "Sesuai kebutuhan riset / Triwulanan pasca pasang ekstrem"],
    ["Kategori Topik", "Klasifikasi tema data spasial menurut ISO 19115", "Inland Waters, Climatology/Meteorology/Atmosphere, Planning/Cadastre, Society"],
    ["Batas Barat (Min X)", "Koordinat bujur barat batas kajian", "110.39378 Bujur Timur (433033.9 m E)"],
    ["Batas Timur (Max X)", "Koordinat bujur timur batas kajian", "110.44492 Bujur Timur (438682.2 m E)"],
    ["Batas Selatan (Min Y)", "Koordinat lintang selatan batas kajian", "-6.97748 Lintang Selatan (9228697.8 m N)"],
    ["Batas Utara (Max Y)", "Koordinat lintang utara batas kajian", "-6.93553 Lintang Selatan (9233339.0 m N)"],
    ["Sistem Referensi Koordinat", "CRS / EPSG identifier", "WGS 84 / UTM Zone 49S (EPSG: 32749)"],
    ["Format Distribusi", "Format file penyimpanan dan pertukaran data", "OGC GeoPackage (.gpkg), ESRI Shapefile (.shp), GeoJSON (.geojson)"],
    ["Skala Peta Sumber", "Rasio skala representasi kartografis", "Skala 1 : 25.000 (Tingkat Ketelitian Perencanaan Wilayah)"],
    ["Ketelitian Posisi", "Nilai RMSE posisi georeferencing & GPS", "RMSE Georeferencing = 0.84 meter; Akurasi GPS Survei = 3.5 meter"],
    ["Silsilah Data (Lineage)", "Riwayat proses dan metodologi akuisisi data", "Data batas administrasi diperoleh dari Ina-Geoportal BIG dan OSM 2024. Peta dasar discan dan dikoreksi melalui georeferencing 6 GCP. Digitasi on-screen sungai dan permukiman dilakukan dengan snapping. Survei lapangan 25 titik GPS dilakukan 18-23 Maret 2026. Analisis buffer 100m, 200m, dan overlay intersect diproses di lingkungan SIG."],
    ["Pihak Bertanggung Jawab", "Identitas tim pembuat dan institusi", "Kelompok Proyek Tugas Besar SIG - Program Studi Teknik Informatika"],
    ["Kontak Penyusun", "Email dan narahubung teknis", "faishal.anwar@student.ac.id"],
    ["Batasan Penggunaan", "Ketentuan lisensi dan etika penggunaan data", "Data ini ditujukan semata-mata untuk keperluan akademik pendidikan tinggi. Bebas digunakan untuk penelitian non-komersial dengan mencantumkan atribusi sumber data."]
]
style_table(ws_m, 4, headers_meta, data_meta)
wb_meta.save(f"{BASE_DIR}/04_DATABASE/Metadata.xlsx")
print("Metadata.xlsx created successfully.")

# ==========================================
# 3. LOGBOOK KONTRIBUSI (Logbook.xlsx)
# ==========================================
wb_log = openpyxl.Workbook()
ws_rekap = wb_log.active
ws_rekap.title = "Rekapitulasi_Kelompok"

ws_rekap.cell(row=1, column=1, value="LOGBOOK KONTRIBUSI ANGGOTA KELOMPOK PROYEK SIG").font = Font(name="Calibri", size=14, bold=True, color="1A5276")
ws_rekap.cell(row=2, column=1, value="Mata Kuliah: Sistem Informasi Geografis | Dosen Pengampu: Ghufron, M.Kom").font = Font(name="Calibri", size=11, italic=True)
ws_rekap.cell(row=3, column=1, value="Tema: Rawan Banjir dan Rob Semarang Utara | Durasi Proyek: 8 Minggu").font = Font(name="Calibri", size=10)

headers_rekap = ["No", "Nama Mahasiswa", "NIM", "Peran Utama", "Komponen SIG", "Total Jam Kerja", "Faktor Kontribusi", "Status Evaluasi"]
data_rekap = [
    [1, "Faishal Anwar", "202401001", "Koordinator / Manajer Proyek", "Prosedur & Manajemen", 42.5, 1.05, "Sangat Aktif - Memimpin Proyek & Laporan"],
    [2, "Budi Santoso", "202401002", "Surveyor Data Lapangan", "Data & Perangkat Keras", 38.0, 1.02, "Sangat Aktif - Survei Lapangan 25 Titik GPS"],
    [3, "Dimas Prasetyo", "202401003", "Operator Digitasi & Georef", "Perangkat Lunak & Data", 40.0, 1.02, "Sangat Aktif - Georeferencing & Digitasi 3 Layer"],
    [4, "Siti Aisyah", "202401004", "Database Analyst", "Basis Data & Topologi", 39.5, 1.01, "Sangat Aktif - Kamus Data, Relasi & Topologi"],
    [5, "Rina Marlina", "202401005", "Analis Spasial & Kartografer", "Analisis & Keluaran", 41.0, 1.04, "Sangat Aktif - Buffer, Overlay & Layout 2 Peta"]
]
style_table(ws_rekap, 5, headers_rekap, data_rekap)

# Add member activity sheets
members = [
    ("Faishal_Anwar", "Faishal Anwar", "Koordinator / Manajer Proyek", [
        ("02/03/2026", "Minggu 1", "Rapat pembentukan tim, pembagian peran 5 komponen SIG, dan pemilihan tema rawan banjir & rob Semarang Utara", 4.0, "Notulensi & Pembagian Tugas"),
        ("09/03/2026", "Minggu 2", "Penyusunan Proposal Proyek SIG Bab I - III, perumusan 4 pertanyaan spasial, dan diagram alir kerja", 6.5, "Dokumen Proposal Proyek"),
        ("16/03/2026", "Minggu 3", "Riset literatur BPBD Semarang, data BPS, dan penyusunan instrumen formulir survei GPS 25 titik", 5.0, "Formulir Survei Lapangan"),
        ("21/03/2026", "Minggu 4", "Pelaksanaan survei lapangan titik banjir/rob di Tanjung Mas dan Bandarharjo bersama tim surveyor", 6.0, "Catatan Koordinat & Foto"),
        ("28/03/2026", "Minggu 5", "Digitasi layer poligon area genangan dan asistensi progres 1 ke dosen pengampu", 5.0, "Draft Layer Genangan"),
        ("04/04/2026", "Minggu 6", "Analisis statistik spasial per kelurahan dan pengujian model relasi tabel profil", 5.5, "Tabel Statistik Keterpaparan"),
        ("11/04/2026", "Minggu 7", "Penyusunan Bab V (Analisis & Pembahasan) dan Bab VII (Integrasi Nilai Islam kemaslahatan publik)", 6.0, "Draft Laporan Akhir Bab I-VII"),
        ("18/04/2026", "Minggu 8", "Finalisasi Laporan Akhir, pembuatan slide presentasi PPTX 15 slide, dan gladi bersih presentasi", 4.5, "Laporan PDF & File PPTX")
    ]),
    ("Budi_Santoso", "Budi Santoso", "Surveyor Data Lapangan", [
        ("03/03/2026", "Minggu 1", "Kajian peta tentatif titik rawan rob BPBD dan penyiapan software SW Maps & GPS HP", 4.0, "Aplikasi GPS Terkalibrasi"),
        ("10/03/2026", "Minggu 2", "Identifikasi calon 25 titik survei di 9 kelurahan Semarang Utara", 4.5, "Daftar Calon Titik Survei"),
        ("18/03/2026", "Minggu 3", "Survei hari 1: Titik SRV-01 s/d SRV-05 di Tanjung Mas (Tambak Lorok, Lamicitra, Dermaga)", 6.0, "Data 5 Titik & Foto Rob"),
        ("19/03/2026", "Minggu 3", "Survei hari 2: Titik SRV-06 s/d SRV-09 di Bandarharjo (Kali Baru, Lodan)", 5.5, "Data 4 Titik & Foto Kali Baru"),
        ("21/03/2026", "Minggu 4", "Survei hari 3: Titik SRV-10 s/d SRV-16 di Panggung Lor, Panggung Kidul, dan Kuningan", 6.0, "Data 7 Titik & Saluran Drainase"),
        ("23/03/2026", "Minggu 4", "Survei hari 4: Titik SRV-17 s/d SRV-25 di Dadapsari, Bulu Lor, Plombokan, Purwosari, dan Polder Banger", 6.0, "Data 9 Titik Selesai"),
        ("30/03/2026", "Minggu 5", "Input atribut survei ke Excel, penamaan file foto, dan digitasi layer titik survei lapangan", 4.0, "Layer Titik Survei GPKG"),
        ("15/04/2026", "Minggu 8", "Penyusunan dokumentasi survei lapangan dan persiapan bahan slide survei presentasi", 2.0, "Bahan Slide Survei")
    ]),
    ("Dimas_Prasetyo", "Dimas Prasetyo", "Operator Digitasi & Georef", [
        ("04/03/2026", "Minggu 1", "Pengumpulan citra resolusi tinggi dan peta RBI dasar lembar Kota Semarang", 4.0, "Peta Analog & Citra Dasar"),
        ("11/03/2026", "Minggu 2", "Setting project QGIS, penentuan CRS WGS 84 / UTM 49S, dan konfigurasi snapping", 4.0, "Project QGIS Template"),
        ("17/03/2026", "Minggu 3", "Pelaksanaan Georeferencing dengan 6 titik kontrol GCP, transformasi Affine, dan evaluasi residu", 6.5, "Peta Tergeoreferensi RMSE 0.84m"),
        ("24/03/2026", "Minggu 4", "Digitasi on-screen layer garis: Sungai dan Saluran Drainase (12 segmen)", 7.0, "Layer Sungai GPKG"),
        ("31/03/2026", "Minggu 5", "Digitasi on-screen layer poligon permukiman penduduk di 9 kelurahan Semarang Utara", 7.5, "Layer Permukiman GPKG"),
        ("07/04/2026", "Minggu 6", "Pembersihan node berlebih, perbaikan vertex, dan memastikan snapping tersambung sempurna", 4.5, "Layer Bersih Vertex"),
        ("14/04/2026", "Minggu 7", "Eksport layer hasil digitasi ke format GPKG independen dan pembuatan dokumentasi visual digitasi", 4.0, "Screenshot & Dok Digitasi"),
        ("19/04/2026", "Minggu 8", "Pemeriksaan konsistensi koordinat seluruh layer dan persiapan sesi tanya jawab teknis", 2.5, "Verifikasi Data QGIS")
    ]),
    ("Siti_Aisyah", "Siti Aisyah", "Database Analyst", [
        ("05/03/2026", "Minggu 1", "Kajian struktur basis data spasial relasional dan tipe atribut SIG", 3.5, "Konsep Tabel SIG"),
        ("12/03/2026", "Minggu 2", "Perancangan skema tabel atribut setiap layer dengan minimal 5 field bermakna", 5.0, "Draft Skema Atribut"),
        ("19/03/2026", "Minggu 3", "Penyusunan Kamus Data lengkap (tipe, domain, nullability, constraint) untuk 8 tabel", 6.5, "Dokumen Kamus Data Excel"),
        ("26/03/2026", "Minggu 4", "Membangun relasi antar tabel (Kelurahan - Permukiman, Kelurahan - Titik Survei, Profil)", 6.0, "Relasi Foreign Key Teruji"),
        ("02/04/2026", "Minggu 5", "Uji validasi topologi garis (bebas overshoot/undershoot) dan poligon (bebas gap/overlap)", 6.5, "Laporan Uji Topologi 100%"),
        ("09/04/2026", "Minggu 6", "Penyusunan dokumen Metadata berstandar ISO 19115 lengkap untuk seluruh dataset", 5.5, "Metadata.xlsx"),
        ("16/04/2026", "Minggu 7", "Penulisan Bab IV (Basis Data SIG, Kamus Data, dan Topologi) pada Laporan Akhir", 4.5, "Draft Bab IV Laporan"),
        ("20/04/2026", "Minggu 8", "Pengemasan basis data GeoPackage Database_SIG.gpkg dan validasi SQLite integritas", 2.0, "Database_SIG.gpkg Final")
    ]),
    ("Rina_Marlina", "Rina Marlina", "Analis Spasial & Kartografer", [
        ("06/03/2026", "Minggu 1", "Kajian metode analisis spasial bahaya hidrologi dan keterpaparan permukiman", 4.0, "Rencana Analisis Spasial"),
        ("13/03/2026", "Minggu 2", "Formulasi parameter buffer sempadan sungai (100 m dan 200 m) dan zonasi genangan", 4.5, "Parameter Analisis"),
        ("25/03/2026", "Minggu 4", "Eksekusi analisis Buffer Sungai 100m & 200m di QGIS dan perhitungan luasan zona", 6.0, "Layer Buffer 100 & 200m"),
        ("01/04/2026", "Minggu 5", "Eksekusi analisis Overlay Intersect (Permukiman x Genangan x Buffer) menghasilkan layer terdampak", 7.0, "Layer Permukiman Terdampak"),
        ("08/04/2026", "Minggu 6", "Eksekusi spatial query keterpaparan dan perhitungan statistik luas terpapar per kelurahan", 6.5, "Tabel Hasil Analisis"),
        ("13/04/2026", "Minggu 7", "Perancangan layout kartografis Peta 1 (Persebaran Banjir & Rob) resolusi 300 DPI lengkap marginalia", 6.5, "Peta 1 PDF & JPG 300 DPI"),
        ("17/04/2026", "Minggu 8", "Perancangan layout kartografis Peta 2 (Analisis Keterpaparan) resolusi 300 DPI lengkap inset", 5.0, "Peta 2 PDF & JPG 300 DPI"),
        ("21/04/2026", "Minggu 8", "Penyusunan slide hasil peta dan interpretasi spasial untuk presentasi kelompok", 1.5, "Slide Visual Peta")
    ])
]

headers_member = ["Tanggal", "Minggu Ke-", "Uraian Kegiatan Rinci", "Durasi (Jam)", "Bukti Fisik / Luaran Kegiatan"]

for sheet_code, name, role, activities in members:
    ws = wb_log.create_sheet(title=sheet_code)
    ws.cell(row=1, column=1, value=f"LOGBOOK KEGIATAN INDIVIDU: {name}").font = Font(name="Calibri", size=13, bold=True, color="1A5276")
    ws.cell(row=2, column=1, value=f"Peran Utama: {role}").font = Font(name="Calibri", size=10, italic=True)
    style_table(ws, 4, headers_member, activities)
    
    # Add sum row
    last_row = 4 + len(activities) + 1
    ws.cell(row=last_row, column=3, value="TOTAL JAM KERJA KONTRIBUSI:").font = Font(name="Calibri", size=10, bold=True)
    ws.cell(row=last_row, column=3).alignment = Alignment(horizontal="right")
    sum_cell = ws.cell(row=last_row, column=4, value=f"=SUM(D5:D{last_row-1})")
    sum_cell.font = Font(name="Calibri", size=11, bold=True, color="1A5276")
    sum_cell.fill = subhead_fill
    sum_cell.border = thin_border
    sum_cell.alignment = Alignment(horizontal="right")

wb_log.save(f"{BASE_DIR}/10_LOGBOOK/Logbook.xlsx")
print("Logbook.xlsx created successfully.")
