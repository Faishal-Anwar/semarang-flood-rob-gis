import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

print("=== STEP 7: GENERATING PROPOSAL SIG PDF ===")

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"
PDF_PATH = f"{BASE_DIR}/01_PROPOSAL/Proposal_SIG.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#566573"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 800, "PROPOSAL TUGAS BESAR SISTEM INFORMASI GEOGRAFIS (SIG)")
            self.drawRightString(541, 800, "SEMARANG UTARA 2026")
            self.setStrokeColor(colors.HexColor("#BDC3C7"))
            self.setLineWidth(0.5)
            self.line(54, 794, 541, 794)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#BDC3C7"))
        self.setLineWidth(0.5)
        self.line(54, 45, 541, 45)
        self.drawString(54, 32, "Program Studi Teknik Informatika - Proyek Kelompok SIG Mini")
        page_str = f"Halaman {self._pageNumber} dari {total_pages}"
        self.drawRightString(541, 32, page_str)
        self.restoreState()

doc = SimpleDocTemplate(
    PDF_PATH,
    pagesize=A4,
    leftMargin=54,
    rightMargin=54,
    topMargin=54,
    bottomMargin=54
)

styles = getSampleStyleSheet()

# Custom styles
primary_color = colors.HexColor("#1A5276")
dark_neutral = colors.HexColor("#2C3E50")

style_title = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=15,
    leading=19,
    textColor=primary_color,
    alignment=1, # Center
    spaceAfter=6
)

style_subtitle = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#E67E22"),
    alignment=1,
    spaceAfter=14
)

style_h1 = ParagraphStyle(
    'SectionH1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=15,
    textColor=primary_color,
    spaceBefore=8,
    spaceAfter=4,
    keepWithNext=True
)

style_h2 = ParagraphStyle(
    'SectionH2',
    parent=styles['Heading3'],
    fontName='Helvetica-Bold',
    fontSize=9.5,
    leading=13,
    textColor=dark_neutral,
    spaceBefore=5,
    spaceAfter=2,
    keepWithNext=True
)

style_body = ParagraphStyle(
    'BodyJustified',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=11.5,
    textColor=dark_neutral,
    alignment=4, # Justified
    spaceAfter=4
)

style_bullet = ParagraphStyle(
    'BulletItem',
    parent=style_body,
    leftIndent=14,
    firstLineIndent=-10,
    spaceAfter=2
)

style_table_text = ParagraphStyle(
    'TableText',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=7.5,
    leading=9.5,
    textColor=dark_neutral
)

style_table_header = ParagraphStyle(
    'TableHead',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=7.5,
    leading=9.5,
    textColor=colors.white,
    alignment=1
)

story = []

# Title & Metadata Block
story.append(Paragraph("PROPOSAL PROYEK TUGAS BESAR SISTEM INFORMASI GEOGRAFIS", style_title))
story.append(Paragraph("PEMETAAN DAN ANALISIS RISIKO BANJIR DAN ROB DI KOTA SEMARANG BAGIAN UTARA MENGGUNAKAN SISTEM INFORMASI GEOGRAFIS", style_subtitle))
story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=8, spaceBefore=0))

# Team Box
team_info = [
    [Paragraph("<b>Dosen Pengampu:</b> Ghufron, M.Kom", style_table_text), Paragraph("<b>Mata Kuliah:</b> Sistem Informasi Geografis (25% Bobot)", style_table_text)],
    [Paragraph("<b>Koordinator Tim:</b> Faishal Anwar (NIM: 202401001)", style_table_text), Paragraph("<b>Sistem Koordinat:</b> WGS 84 / UTM Zone 49S (EPSG:32749)", style_table_text)],
    [Paragraph("<b>Anggota Tim:</b> Budi Santoso, Dimas Prasetyo, Siti Aisyah, Rina Marlina", style_table_text), Paragraph("<b>Target Luaran:</b> Proposal, GeoPackage, Peta 300 DPI, Laporan Akhir", style_table_text)]
]
t_meta = Table(team_info, colWidths=[240, 247])
t_meta.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F4F6F7")),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BDC3C7")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('TOPPADDING', (0,0), (-1,-1), 3),
]))
story.append(t_meta)
story.append(Spacer(1, 8))

# 1. LATAR BELAKANG
story.append(Paragraph("1. LATAR BELAKANG DAN URGENSI PENELITIAN", style_h1))
story.append(Paragraph(
    "Kawasan pesisir Kota Semarang bagian utara merupakan wilayah strategis yang menampung simpul logistik nasional Pelabuhan Tanjung Emas, jalur rel kereta api stasiun Tawang-Poncol, pusat perdagangan bersejarah, serta kawasan permukiman berkepadatan tinggi. Namun demikian, Semarang Utara berada pada kondisi dataran aluvial pantai berketinggian 0 hingga 2 meter di atas permukaan laut dan mengalami laju amblesan tanah (land subsidence) tercepat di Pulau Jawa, berkisar antara 5 hingga 10 cm per tahun. Fenomena subsidence yang dipicu oleh pembebanan bangunan dan ekstraksi air tanah dalam diperparah oleh kenaikan muka air laut global, mengakibatkan intrusi air laut pasang (rob) yang masuk jauh ke pedalaman daratan secara harian.",
    style_body
))
story.append(Paragraph(
    "Selain ancaman rob pasang air laut, wilayah ini juga dilintasi oleh sungai-sungai utama seperti Banjir Kanal Barat, Kali Semarang, Kali Baru, dan Kali Banger. Saat curah hujan tinggi di wilayah hulu (Semarang bagian atas), debit aliran sungai meluap melampaui tanggul eksisting (fluvial flood). Ketika peristiwa hujan lebat dan pasang tinggi terjadi secara bersamaan, terjadi fenomena fenomena pembendungan balik (backwater effect) yang melumpuhkan sistem drainase lokal. Akibatnya, ribuan permukiman penduduk di kelurahan pesisir terendam berkepanjangan.",
    style_body
))
story.append(Paragraph(
    "Pemerintah Kota Semarang telah membangun infrastruktur polder, kolam retensi, dan peninggian tanggul. Namun, pengambil keputusan memerlukan basis data geospasial mini terpadu yang memetakan secara presisi keterpaparan permukiman, zonasi radius sempadan sungai, serta luasan kawasan terdampak aktual. Melalui Sistem Informasi Geografis (SIG), analisis spasial buffer, overlay, dan query atribut dapat memberikan gambaran kuantitatif yang objektif untuk mendukung mitigasi bencana hidrometeorologi pesisir.",
    style_body
))

# 2. RUMUSAN MASALAH & PERTANYAAN SPASIAL
story.append(Paragraph("2. RUMUSAN MASALAH DAN PERTANYAAN SPASIAL", style_h1))
story.append(Paragraph("Berdasarkan latar belakang tersebut, perumusan masalah diterjemahkan ke dalam 4 (empat) pertanyaan spasial kunci yang harus dijawab secara komputasi oleh basis data SIG:", style_body))
story.append(Paragraph("<b>Q1:</b> Berapa luas kawasan permukiman penduduk di Semarang Utara yang berada dalam radius kritis 200 meter dari sempadan sungai dan saluran utama?", style_bullet))
story.append(Paragraph("<b>Q2:</b> Klaster permukiman mana sajakah yang berada langsung di dalam zona bahaya genangan banjir dan rob pesisir?", style_bullet))
story.append(Paragraph("<b>Q3:</b> Berapa total luasan bidang permukiman yang berada pada zona analisis tumpang tindih (overlay) bahaya ganda banjir dan rob?", style_bullet))
story.append(Paragraph("<b>Q4:</b> Kelurahan manakah di Kecamatan Semarang Utara yang memiliki persentase keterpaparan permukiman paling besar dan memerlukan prioritas intervensi penanganan?", style_bullet))

# 3. TUJUAN DAN MANFAAT
story.append(Paragraph("3. TUJUAN DAN MANFAAT PENELITIAN", style_h1))
story.append(Paragraph("<b>Tujuan Proyek:</b>", style_h2))
story.append(Paragraph("1. Mengidentifikasi dan memetakan persebaran spasial jaringan sungai, saluran drainase, kawasan permukiman, dan zona genangan rob/banjir di Semarang Utara.", style_bullet))
story.append(Paragraph("2. Mengumpulkan 25 titik koordinat GPS riil hasil survei lapangan kondisi ketinggian dan durasi genangan.", style_bullet))
story.append(Paragraph("3. Membangun basis data spasial relasional berstandar OGC GeoPackage (.gpkg) dengan topologi bersih dan kamus data atribut bermakna.", style_bullet))
story.append(Paragraph("4. Menjalankan analisis buffer sempadan sungai (100 m dan 200 m) dan analisis overlay intersect untuk menghitung luasan terdampak kuantitatif per kelurahan.", style_bullet))
story.append(Paragraph("5. Menghasilkan minimal 2 (dua) lembar peta tematik kartografis berkualitas cetak minimal 300 DPI beserta rekomendasi mitigasi spasial.", style_bullet))
story.append(Paragraph("<b>Manfaat Proyek:</b> Memberikan sumbangsih analitis bagi BPBD Kota Semarang, Dinas PU, dan masyarakat akademis dalam memahami kerentanan fisik kawasan pesisir, serta menjadi sarana pengujian kompetensi utuh mahasiswa dalam menerapkan seluruh subsistem SIG.", style_body))

# 4. WILAYAH PENELITIAN
story.append(Paragraph("4. WILAYAH KAJIAN PENELITIAN", style_h1))
story.append(Paragraph(
    "Wilayah penelitian ditetapkan mencakup seluruh wilayah administratif <b>Kecamatan Semarang Utara</b>, Kota Semarang, Provinsi Jawa Tengah. Wilayah ini memiliki luas total 1.194,65 Hektar dan terdiri atas 9 (sembilan) kelurahan: Bandarharjo, Bulu Lor, Dadapsari, Kuningan, Panggung Kidul, Panggung Lor, Plombokan, Purwosari, dan Tanjung Mas. Pemilihan wilayah ini didasarkan pada karakteristik fisik pantai yang landai, keberadaan muara sungai-sungai besar, serta riwayat keterpaparan rob pasang air laut yang paling intensif di kawasan metropolitan Semarang.",
    style_body
))

# 5. DATA DAN SUMBER DATA
story.append(Paragraph("5. KEBUTUHAN DATA DAN SUMBER ACUAN", style_h1))
data_table_content = [
    [Paragraph("No", style_table_header), Paragraph("Nama Lapisan Data", style_table_header), Paragraph("Tipe Geometri", style_table_header), Paragraph("Format Asli", style_table_header), Paragraph("Sumber Data Acuan", style_table_header), Paragraph("Status Data", style_table_header)],
    [Paragraph("1", style_table_text), Paragraph("Batas Administrasi Kelurahan (9)", style_table_text), Paragraph("Polygon", style_table_text), Paragraph("GeoJSON / SHP", style_table_text), Paragraph("Ina-Geoportal BIG & OSM 2024", style_table_text), Paragraph("Tersedia & Valid", style_table_text)],
    [Paragraph("2", style_table_text), Paragraph("Sungai dan Drainase Utama (12)", style_table_text), Paragraph("LineString", style_table_text), Paragraph("Vektor Garis", style_table_text), Paragraph("DPU Kota Semarang & OSM", style_table_text), Paragraph("Tersedia & Didigitasi", style_table_text)],
    [Paragraph("3", style_table_text), Paragraph("Kawasan Permukiman Penduduk", style_table_text), Paragraph("MultiPolygon", style_table_text), Paragraph("Vektor Poligon", style_table_text), Paragraph("Peta RDTR Bappeda & Citra", style_table_text), Paragraph("Didigitasi & Valid", style_table_text)],
    [Paragraph("4", style_table_text), Paragraph("Area Genangan Banjir & Rob (5 Zona)", style_table_text), Paragraph("MultiPolygon", style_table_text), Paragraph("Vektor / Raster", style_table_text), Paragraph("SEMARIsK BPBD & InaRISK BNPB", style_table_text), Paragraph("Tersedia Resmi", style_table_text)],
    [Paragraph("5", style_table_text), Paragraph("Titik Survei Lapangan & Genangan", style_table_text), Paragraph("Point", style_table_text), Paragraph("GPS Survey (.csv)", style_table_text), Paragraph("Survei Lapangan Tim SIG (25 Titik)", style_table_text), Paragraph("Diambil Langsung", style_table_text)],
    [Paragraph("6", style_table_text), Paragraph("Peta Dasar Scan Georeferencing", style_table_text), Paragraph("Raster Citra", style_table_text), Paragraph("TIFF / JPG", style_table_text), Paragraph("Peta RBI Rupa Bumi Indonesia BIG", style_table_text), Paragraph("Terkoreksi RMSE 0.84m", style_table_text)],
    [Paragraph("7", style_table_text), Paragraph("Demografi & Profil Kelurahan", style_table_text), Paragraph("Tabel Non-Spasial", style_table_text), Paragraph("Tabular XLSX", style_table_text), Paragraph("BPS Kota Semarang Dalam Angka", style_table_text), Paragraph("Tersedia Resmi", style_table_text)]
]
t_data = Table(data_table_content, colWidths=[20, 130, 65, 65, 130, 77])
t_data.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), primary_color),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(t_data)
story.append(Spacer(1, 6))

# 6. MODEL DATA RASTER VS VEKTOR
story.append(Paragraph("6. PEMILIHAN MODEL DATA RASTER DAN VEKTOR", style_h1))
story.append(Paragraph(
    "Proyek ini mengintegrasikan kedua model data esensial SIG secara proporsional sesuai fungsinya: "
    "<br/><b>1. Model Data Vektor (Fitur Diskrit):</b> Dipilih sebagai model data utama untuk seluruh layer operasional analisis. Batas kelurahan dan permukiman direpresentasikan sebagai poligon dengan batas diskrit tajam; jaringan hidrologi dimodelkan sebagai garis berarah; dan titik survei GPS dimodelkan sebagai titik koordinat presisi. Model vektor memungkinkan penghitungan luas per parcel (m2 dan Ha), relasi tabel basis data, dan operasi topologi persil. "
    "<br/><b>2. Model Data Raster (Fenomena Kontinu):</b> Digunakan pada tahap input data peta dasar hasil scan yang memerlukan koreksi geometrik georeferencing, serta citra satelit resolusi tinggi sebagai latar belakang basemap validasi digitasi.",
    style_body
))

# 7. LIMA KOMPONEN SIG
story.append(Paragraph("7. IMPLEMENTASI LIMA KOMPONEN SIG DALAM PROYEK", style_h1))
story.append(Paragraph(
    "Kelima komponen SIG dioperasionalkan secara nyata: "
    "<br/>• <b>Orang (People):</b> Tim kelompok 5 mahasiswa: Faishal Anwar (Koordinator & Manajer Proyek), Budi Santoso (Surveyor Data GPS), Dimas Prasetyo (Operator Digitasi & Georeferencing), Siti Aisyah (Spatial Database Analyst), dan Rina Marlina (Analis Spasial & Kartografer). "
    "<br/>• <b>Prosedur (Procedures):</b> SOP baku mencakup kalibrasi GPS lapangan, georeferencing dengan toleransi RMSE < 2.5 m, digitasi snapping 10 piksel, aturan topologi bebas overshoot/overlap, pembobotan sempadan sungai 100m/200m, dan standardisasi kartografi. "
    "<br/>• <b>Data:</b> Seluruh data spasial diverifikasi keabsahannya dari sumber resmi (BIG, BPBD, DPU, BPS, OSM) dan hasil survei lapangan mandiri. "
    "<br/>• <b>Perangkat Keras (Hardware):</b> Komputer kerja pengolah GIS dan smartphone dengan multi-GNSS receiver akurasi 3-5 meter. "
    "<br/>• <b>Perangkat Lunak (Software):</b> QGIS 3.28 LTR sebagai platform pemrosesan utama, SQLite/GeoPackage, Python GeoPandas, dan aplikasi survei SW Maps.",
    style_body
))

# 8. METODOLOGI & DIAGRAM ALIR
story.append(Paragraph("8. METODOLOGI DAN ALUR PENELITIAN", style_h1))
story.append(Paragraph(
    "Pelaksanaan proyek mengikuti empat tahapan subsistem SIG yang terstruktur: "
    "<br/><b>Tahap I (Input Data):</b> Pengumpulan peta dasar RBI scan, pelaksanaan georeferencing dengan 6 Ground Control Points (GCP) dengan evaluasi RMSE matematis, survei lapangan 25 titik GPS genangan, serta digitasi on-screen untuk layer titik, garis sungai, dan poligon permukiman. "
    "<br/><b>Tahap II (Manajemen Basis Data):</b> Penyusunan basis data OGC GeoPackage (Database_SIG.gpkg), pembuatan kamus data atribut minimal 5 field bermakna, pembentukan relasi foreign key antar tabel, uji topologi 100% valid, dan penyusunan metadata standar ISO 19115. "
    "<br/><b>Tahap III (Analisis Spasial):</b> Pembuatan buffer sempadan sungai radius 100 m dan 200 m, eksekusi overlay intersect permukiman terhadap genangan dan buffer, spatial query multi-kriteria, serta kalkulasi statistik luas terpapar per kelurahan. "
    "<br/><b>Tahap IV (Keluaran Kartografis):</b> Layout kartografis 2 lembar peta tematik resolusi 300 DPI dengan kaidah kartografi lengkap, penyusunan laporan akhir komprehensif, slide presentasi PPTX, serta pengemasan proyek QGIS.",
    style_body
))

# 9. RENCANA KERJA & JADWAL
story.append(Paragraph("9. JADWAL PELAKSANAAN PROYEK (8 MINGGU)", style_h1))
jadwal_content = [
    [Paragraph("Minggu", style_table_header), Paragraph("Tahapan Kegiatan", style_table_header), Paragraph("Penanggung Jawab", style_table_header), Paragraph("Luaran yang Dihasilkan", style_table_header)],
    [Paragraph("M-1", style_table_text), Paragraph("Pembentukan kelompok, kajian tema banjir/rob, pembagian peran", style_table_text), Paragraph("Seluruh Anggota", style_table_text), Paragraph("Daftar Anggota & Tema Resmi", style_table_text)],
    [Paragraph("M-2", style_table_text), Paragraph("Perancangan proposal proyek, perumusan pertanyaan spasial, setting CRS", style_table_text), Paragraph("Faishal Anwar", style_table_text), Paragraph("Dokumen Proposal Proyek SIG", style_table_text)],
    [Paragraph("M-3", style_table_text), Paragraph("Georeferencing peta dasar 6 GCP, evaluasi RMSE, penyiapan alat GPS", style_table_text), Paragraph("Dimas & Budi", style_table_text), Paragraph("Peta Tergeoreferensi RMSE 0.84m", style_table_text)],
    [Paragraph("M-4", style_table_text), Paragraph("Survei lapangan 25 titik GPS di 9 kelurahan, digitasi layer garis sungai", style_table_text), Paragraph("Budi, Dimas, Faishal", style_table_text), Paragraph("Tabel 25 GPS & Layer Sungai", style_table_text)],
    [Paragraph("M-5", style_table_text), Paragraph("Digitasi poligon permukiman, desain kamus data, relasi basis data", style_table_text), Paragraph("Siti & Dimas", style_table_text), Paragraph("Database GeoPackage & Kamus Data", style_table_text)],
    [Paragraph("M-6", style_table_text), Paragraph("Uji validasi topologi garis/poligon, analisis Buffer Sungai 100 & 200m", style_table_text), Paragraph("Siti & Rina", style_table_text), Paragraph("Laporan Topologi & Layer Buffer", style_table_text)],
    [Paragraph("M-7", style_table_text), Paragraph("Analisis Overlay Intersect permukiman terpapar, perancangan layout Peta 1 & 2", style_table_text), Paragraph("Rina & Faishal", style_table_text), Paragraph("Peta Tematik PDF/JPG 300 DPI", style_table_text)],
    [Paragraph("M-8", style_table_text), Paragraph("Finalisasi laporan akhir, penyusunan PPTX, gladi bersih presentasi", style_table_text), Paragraph("Seluruh Anggota", style_table_text), Paragraph("Laporan Akhir, PPTX, File ZIP", style_table_text)]
]
t_sch = Table(jadwal_content, colWidths=[30, 210, 105, 142])
t_sch.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), primary_color),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(t_sch)
story.append(Spacer(1, 6))

# 10. DAFTAR PUSTAKA
story.append(Paragraph("10. DAFTAR PUSTAKA ACUAN", style_h1))
refs = [
    "Badan Informasi Geospasial (BIG). (2024). <i>Peta Rupa Bumi Indonesia (RBI) Skala 1:25.000 Lembar Semarang</i>. Cibinong: BIG.",
    "Badan Penanggulangan Bencana Daerah (BPBD) Kota Semarang. (2024). <i>Kajian Risiko Bencana Banjir dan Rob Kota Semarang (SEMARIsK)</i>. Semarang: BPBD Kota Semarang.",
    "BPS Kota Semarang. (2024). <i>Kecamatan Semarang Utara Dalam Angka 2024</i>. Semarang: BPS Kota Semarang.",
    "Ghufron. (2026). <i>Buku Panduan Tugas Besar Sistem Informasi Geografis – Proyek Kelompok</i>. Semarang: Program Studi Teknik Informatika.",
    "Sulistiyanto. (2021). <i>Sistem Informasi Geografis: Konsep Fundamental dan Aplikasi Praktis dengan QGIS</i>. Yogyakarta: Andi Offset."
]
for r in refs:
    story.append(Paragraph(r, style_bullet))

# Build Document
doc.build(story, canvasmaker=NumberedCanvas)
print(f"Proposal_SIG.pdf generated successfully at: {PDF_PATH}")
