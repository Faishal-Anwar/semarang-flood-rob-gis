import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

print("=== STEP 8: GENERATING COMPREHENSIVE FINAL REPORT (LAPORAN AKHIR PDF) ===")

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"
PDF_PATH = f"{BASE_DIR}/08_LAPORAN/Laporan_Akhir.pdf"

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
        
        # Don't draw header/footer on cover page (page 1)
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 802, "LAPORAN AKHIR TUGAS BESAR SISTEM INFORMASI GEOGRAFIS (SIG)")
            self.drawRightString(541, 802, "KECAMATAN SEMARANG UTARA")
            self.setStrokeColor(colors.HexColor("#BDC3C7"))
            self.setLineWidth(0.5)
            self.line(54, 796, 541, 796)
            
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

# Colors
C_PRIMARY = colors.HexColor("#1A5276")    # Deep Navy
C_SECONDARY = colors.HexColor("#E67E22")  # Warm Amber/Orange
C_DARK = colors.HexColor("#2C3E50")       # Dark Charcoal
C_LIGHT = colors.HexColor("#F8F9FA")      # Off-white
C_BORDER = colors.HexColor("#BDC3C7")     # Light gray

style_cover_title = ParagraphStyle(
    'CoverTitle',
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=23,
    textColor=C_PRIMARY,
    alignment=1,
    spaceAfter=12
)

style_cover_subtitle = ParagraphStyle(
    'CoverSubtitle',
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=15,
    textColor=C_SECONDARY,
    alignment=1,
    spaceAfter=20
)

style_bab_title = ParagraphStyle(
    'BabTitle',
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=17,
    textColor=C_PRIMARY,
    spaceBefore=12,
    spaceAfter=8,
    keepWithNext=True
)

style_sub_title = ParagraphStyle(
    'SubTitle',
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=14,
    textColor=C_DARK,
    spaceBefore=8,
    spaceAfter=4,
    keepWithNext=True
)

style_body = ParagraphStyle(
    'Body',
    fontName='Helvetica',
    fontSize=8.5,
    leading=12,
    textColor=C_DARK,
    alignment=4,
    spaceAfter=5
)

style_bullet = ParagraphStyle(
    'Bullet',
    parent=style_body,
    leftIndent=14,
    firstLineIndent=-10,
    spaceAfter=3
)

style_tbl_cell = ParagraphStyle(
    'TblCell',
    fontName='Helvetica',
    fontSize=7.5,
    leading=9.5,
    textColor=C_DARK
)

style_tbl_head = ParagraphStyle(
    'TblHead',
    fontName='Helvetica-Bold',
    fontSize=7.5,
    leading=9.5,
    textColor=colors.white,
    alignment=1
)

story = []

# =========================================================================
# COVER PAGE (Page 1)
# =========================================================================
story.append(Spacer(1, 40))
story.append(Paragraph("LAPORAN AKHIR PROYEK KELOMPOK<br/>TUGAS BESAR SISTEM INFORMASI GEOGRAFIS (SIG)", style_cover_title))
story.append(Paragraph("PEMETAAN DAN ANALISIS RISIKO BANJIR DAN ROB<br/>DI KOTA SEMARANG BAGIAN UTARA MENGGUNAKAN QGIS", style_cover_subtitle))
story.append(HRFlowable(width="80%", thickness=2, color=C_PRIMARY, spaceAfter=30, spaceBefore=0))

story.append(Paragraph("Diajukan untuk Memenuhi Syarat Evaluasi Akhir Mata Kuliah Sistem Informasi Geografis (25% Bobot Penilaian)", ParagraphStyle('CoverDesc', fontName='Helvetica-Oblique', fontSize=9, leading=13, alignment=1, textColor=C_DARK)))
story.append(Spacer(1, 40))

# Cover Box with Members
cover_box_data = [
    [Paragraph("<b>Dosen Pengampu:</b>", style_tbl_cell), Paragraph("Ghufron, M.Kom", style_tbl_cell)],
    [Paragraph("<b>Program Studi:</b>", style_tbl_cell), Paragraph("Teknik Informatika", style_tbl_cell)],
    [Paragraph("<b>Tahun Akademik:</b>", style_tbl_cell), Paragraph("Genap 2025/2026", style_tbl_cell)],
    [Paragraph("<b>Sistem Proyeksi / CRS:</b>", style_tbl_cell), Paragraph("WGS 84 / UTM Zone 49S (EPSG:32749)", style_tbl_cell)],
    [Paragraph("<b>Disusun oleh Kelompok 3:</b>", style_tbl_cell), Paragraph(
        "1. Faishal Anwar (NIM: 202401001) - <i>Project Manager & Lead Analyst</i><br/>"
        "2. Budi Santoso (NIM: 202401002) - <i>Field Surveyor GPS</i><br/>"
        "3. Dimas Prasetyo (NIM: 202401003) - <i>Digitizing & Georeferencing Specialist</i><br/>"
        "4. Siti Aisyah (NIM: 202401004) - <i>Spatial Database Analyst</i><br/>"
        "5. Rina Marlina (NIM: 202401005) - <i>Cartographer & Visual Designer</i>", style_tbl_cell)]
]
t_cov = Table(cover_box_data, colWidths=[140, 310])
t_cov.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), C_LIGHT),
    ('BOX', (0,0), (-1,-1), 1.5, C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(t_cov)

story.append(Spacer(1, 80))
story.append(Paragraph("PROGRAM STUDI TEKNIK INFORMATIKA<br/>FAKULTAS SAINS DAN TEKNOLOGI<br/>2026", ParagraphStyle('CoverUniv', fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=1, textColor=C_PRIMARY)))
story.append(PageBreak())

# =========================================================================
# KATA PENGANTAR & RINGKASAN EKSEKUTIF (Page 2)
# =========================================================================
story.append(Paragraph("KATA PENGANTAR", style_bab_title))
story.append(Paragraph(
    "Puji syukur ke hadirat Allah SWT atas limpahan rahmat, taufik, dan hidayah-Nya, sehingga tim penulis dapat menyelesaikan Laporan Akhir Tugas Besar Sistem Informasi Geografis (SIG) yang berjudul <i>\"Pemetaan dan Analisis Risiko Banjir dan Rob di Kota Semarang Bagian Utara Menggunakan Sistem Informasi Geografis\"</i> dengan tepat waktu dan memenuhi seluruh kriteria akademik yang dipersyaratkan.",
    style_body
))
story.append(Paragraph(
    "Laporan ini disusun sebagai pemenuhan beban 25% nilai akhir mata kuliah SIG. Penulis menyampaikan ucapan terima kasih yang tulus kepada Bapak <b>Ghufron, M.Kom</b> selaku dosen pengampu atas bimbingan teknis, koreksi substantif, dan arahan metodologis selama satu semester perkuliahan. Penulis menyadari karya ini tidak lepas dari kekurangan dan senantiasa terbuka atas masukan yang membangun.",
    style_body
))
story.append(Spacer(1, 8))

story.append(Paragraph("RINGKASAN EKSEKUTIF (EXECUTIVE SUMMARY)", style_bab_title))
story.append(Paragraph(
    "Bencana hidrometeorologi banjir dan genangan rob pasang surut air laut merupakan ancaman eksistensial bagi keberlangsungan wilayah pesisir Kecamatan Semarang Utara. Penelitian ini mengintegrasikan seluruh subsistem SIG (Input Data, Manajemen Basis Data, Analisis Spasial, dan Keluaran Kartografis) dalam membedah kerentanan fisik kawasan permukiman di 9 (sembilan) kelurahan Semarang Utara seluas 1.194,65 Hektar.",
    style_body
))
story.append(Paragraph(
    "Data spasial disusun secara terpadu dalam format standar OGC GeoPackage (Database_SIG.gpkg) pada proyeksi WGS 84 / UTM Zone 49S (EPSG:32749). Proses input diawali georeferencing peta dasar 6 titik kontrol tanah (GCP) dengan ketelitian posisi tinggi bernilai RMSE 0,840 meter, survei lapangan 25 titik koordinat GPS genangan, serta digitasi on-screen bersnapping presisi untuk jaringan hidrologi (12 segmen) dan permukiman (15 klaster). Basis data dilengkapi 4 relasi foreign key fungsional, kamus data atribut bermakna, serta lolos validasi topologi 100% bebas error.",
    style_body
))
story.append(Paragraph(
    "Analisis spasial multikriteria menggabungkan teknik Buffer Sungai ganda (100 m dan 200 m) dan Overlay Intersect permukiman terhadap zona rawan genangan. Temuan analitis menunjukkan bahwa dari 171,68 Ha total luas kawasan permukiman eksisting, seluas 120,31 Ha (70,08%) berada di dalam poligon zona rawan BPBD/InaRISK — eksposur statis, bukan luas genangan atau kejadian banjir saat ini. Kelurahan Panggung Kidul (97,37%) dan Panggung Lor (95,76%) teridentifikasi sebagai kawasan dengan rasio eksposur zona rawan tertinggi. Hasil analisis diwujudkan ke dalam 2 lembar peta tematik kartografis 300 DPI dan dirumuskan ke dalam rekomendasi struktural polder terpadu serta kebijakan penataan sempadan sungai.",
    style_body
))
story.append(PageBreak())

# =========================================================================
# DAFTAR ISI, TABEL, DAN GAMBAR (Page 3)
# =========================================================================
story.append(Paragraph("DAFTAR ISI DAN STRUKTUR DOKUMEN", style_bab_title))
doc_structure = [
    ("Halaman Sampul / Judul Proyek", "1"),
    ("Kata Pengantar & Ringkasan Eksekutif", "2"),
    ("Daftar Isi, Daftar Tabel, dan Daftar Gambar", "3"),
    ("BAB I PENDAHULUAN (Latar Belakang, Rumusan, Pertanyaan Spasial, Tujuan, Wilayah)", "4"),
    ("BAB II KONSEP DAN KOMPONEN SIG (5 Komponen, Vektor vs Raster, Konsep Analisis)", "6"),
    ("BAB III METODOLOGI DAN INPUT DATA (Sumber Data, Georeferencing, Digitasi, 25 GPS)", "8"),
    ("BAB IV BASIS DATA SPASIAL GEOPACKAGE (Struktur GPKG, Kamus Data, Relasi, Topologi)", "11"),
    ("BAB V ANALISIS SPASIAL DAN PEMBAHASAN (Buffer Sungai, Overlay, Statistik, Kebijakan)", "13"),
    ("BAB VI KESIMPULAN DAN SARAN (Jawaban 4 Pertanyaan Spasial, Saran Tindak Lanjut)", "17"),
    ("BAB VII INTEGRASI NILAI ISLAM DALAM PENGELOLAAN SPASIAL", "18"),
    ("DAFTAR PUSTAKA ACUAN", "19"),
    ("LAMPIRAN 1: Logbook Kontribusi Anggota Tim (8 Minggu)", "20"),
    ("LAMPIRAN 2: Kamus Data Atribut & Skema Basis Data", "21"),
    ("LAMPIRAN 3: Dokumentasi Teknis Georeferencing, Topologi, dan 25 Titik GPS", "22"),
    ("LAMPIRAN 4: Hasil Kartografis Peta Tematik 1 & Peta Tematik 2 (Resolusi Penuh)", "23")
]
t_toc_data = [[Paragraph(f"<b>{item[0]}</b>", style_tbl_cell), Paragraph(item[1], ParagraphStyle('TR', parent=style_tbl_cell, alignment=2))] for item in doc_structure]
t_toc = Table(t_toc_data, colWidths=[420, 67])
t_toc.setStyle(TableStyle([
    ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#EAEDED")),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(t_toc)
story.append(Spacer(1, 10))

story.append(Paragraph("DAFTAR TABEL & GAMBAR KUNCI", style_sub_title))
tbl_list = [
    ("Tabel 1.1", "Profil Luas dan Demografi 9 Kelurahan Semarang Utara", "Hal 5"),
    ("Tabel 3.1", "Spesifikasi 6 Titik Kontrol GCP Georeferencing dan Evaluasi Residu RMSE", "Hal 9"),
    ("Tabel 3.2", "Rekapitulasi 25 Titik Koordinat GPS Hasil Survei Lapangan", "Hal 10"),
    ("Tabel 4.1", "Struktur Basis Data OGC GeoPackage (Database_SIG.gpkg)", "Hal 11"),
    ("Tabel 5.1", "Hasil Pengukuran Luas Buffer Sempadan Sungai 100m dan 200m", "Hal 13"),
    ("Tabel 5.2", "Statistik Luas Keterpaparan Permukiman per Kelurahan Hasil Overlay", "Hal 15"),
    ("Gambar 3.1", "Plot Sebaran 6 GCP Georeferencing & Vektor Error Residu", "Hal 9"),
    ("Gambar 5.1", "Diagram Alur Subsistem Analisis Spasial Multikriteria", "Hal 14"),
    ("Gambar 7.1", "Peta Tematik 1: Persebaran Banjir, Rob, Sungai, dan Permukiman", "Hal 23"),
    ("Gambar 7.2", "Peta Tematik 2: Analisis Keterpaparan Permukiman Terhadap Banjir & Rob", "Hal 24")
]
t_items = [[Paragraph(f"<b>{i[0]}</b>: {i[1]}", style_tbl_cell), Paragraph(i[2], ParagraphStyle('TR2', parent=style_tbl_cell, alignment=2))] for i in tbl_list]
t_it = Table(t_items, colWidths=[410, 77])
t_it.setStyle(TableStyle([
    ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#EAEDED")),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(t_it)
story.append(PageBreak())

# =========================================================================
# BAB I PENDAHULUAN (Page 4 - 5)
# =========================================================================
story.append(Paragraph("BAB I. PENDAHULUAN", style_bab_title))
story.append(Paragraph("1.1 Latar Belakang dan Urgensi Masalah", style_sub_title))
story.append(Paragraph(
    "Kota Semarang merupakan ibukota Provinsi Jawa Tengah yang secara geomorfologis terbagi menjadi dua bentang alam kontras: perbukitan di selatan dan dataran pantai aluvial di utara. Wilayah Kecamatan Semarang Utara berada tepat di garis terdepan pantai Laut Jawa dengan elevasi daratan rata-rata berkisar antara 0,0 hingga 2,0 meter di atas permukaan laut rata-rata (Mean Sea Level/MSL). Posisi topografi yang sangat rendah ini menjadikan Semarang Utara sebagai kawasan dengan tingkat kerentanan hidrometeorologi tertinggi di Kota Semarang.",
    style_body
))
story.append(Paragraph(
    "Terdapat dua fenomena fisik utama yang mendorong krisis banjir di kawasan ini: "
    "<br/><b>1. Amblesan Tanah (Land Subsidence):</b> Hasil studi geodesi Badan Informasi Geospasial (BIG) dan para peneliti ITB menunjukkan bahwa laju amblesan tanah di kawasan pesisir Semarang berkisar 5–10 cm per tahun. Penurunan ini dipicu oleh konsolidasi alami sedimen aluvial muda, pembebanan bangunan industri dan perumahan padat, serta ekstraksi air tanah artesis dalam yang berlebihan. Penurunan elevasi tanah menyebabkan sebagian besar daratan kini berada di bawah muka air laut pasang tertinggi (Highest Astronomical Tide). "
    "<br/><b>2. Limpasan Sungai (Fluvial Flooding) dan Efek Pembendungan Balik (Backwater):</b> Semarang Utara menjadi muara hilir bagi sistem hidrologi DAS Garang melalui Banjir Kanal Barat (BKB), DAS Kali Semarang, dan DAS Kali Banger. Saat hujan intensitas tinggi terjadi di kawasan atas, aliran debit sungai bertemu dengan tekanan pasang air laut di muara. Fenomena ini memicu penahanan aliran (backwater effect) yang mengakibatkan tanggul sungai meluap dan menjebol dinding penahan air.",
    style_body
))
story.append(Paragraph(
    "Dampak limpasan rob dan banjir fluvial bukan sekadar genangan periodik, melainkan kerusakan struktural permukiman, penurunan sanitasi lingkungan akibat pencemaran tinja dan limbah domestik, kerugian ekonomi nelayan dan industri di Pelabuhan Tanjung Emas, serta disrupsi jalur transportasi utama kereta api dan jalan arteri nasional. Oleh sebab itu, diperlukan pendekatan analitis spasial objektif berbasis Sistem Informasi Geografis (SIG) untuk memetakan risiko bencana, menghitung luas kawasan terbangun yang berada di zona rawan, dan menyediakan data penanganan darurat yang akurat.",
    style_body
))

story.append(Paragraph("1.2 Rumusan Masalah dan 4 Pertanyaan Spasial", style_sub_title))
story.append(Paragraph(
    "Meskipun data tabular terkait banjir kerap dihimpun oleh dinas terkait, informasi tersebut seringkali tidak memiliki referensi spasial eksplisit. Pemerintah daerah dan masyarakat membutuhkan jawaban kuantitatif berbasis peta yang tidak dapat dijawab hanya dengan membaca tabel biasa. Rumusan masalah dalam proyek ini dirumuskan ke dalam 4 (empat) pertanyaan spasial kunci:",
    style_body
))
story.append(Paragraph("<b>Pertanyaan Spasial 1 (Q1):</b> Berapakah luas total kawasan permukiman penduduk di Semarang Utara yang berada dalam radius kritis 200 meter dari sempadan sungai dan saluran hidrologi utama?", style_bullet))
story.append(Paragraph("<b>Pertanyaan Spasial 2 (Q2):</b> Klaster-klaster permukiman mana sajakah yang berada langsung di dalam batas zona genangan banjir rob pasang surut air laut pesisir?", style_bullet))
story.append(Paragraph("<b>Pertanyaan Spasial 3 (Q3):</b> Berapakah luas bidang permukiman yang berada pada zona tumpang tindih (overlay) bahaya ganda, yaitu berada di zona rawan rob sekaligus di sempadan sungai?", style_bullet))
story.append(Paragraph("<b>Pertanyaan Spasial 4 (Q4):</b> Kelurahan manakah di Kecamatan Semarang Utara yang memiliki persentase eksposur zona rawan permukiman tertinggi dan harus menjadi prioritas penanganan penataan ruang?", style_bullet))

story.append(Paragraph("1.3 Tujuan dan Manfaat Proyek", style_sub_title))
story.append(Paragraph(
    "<b>Tujuan Penelitian:</b>"
    "<br/>1. Mengumpulkan, merektifikasi (georeferencing), dan mendigitasi data geospasial jaringan sungai, batas wilayah, permukiman, dan sebaran genangan di Semarang Utara."
    "<br/>2. Melaksanakan survei lapangan GPS untuk memvalidasi ketinggian dan durasi genangan aktual pada 25 titik koordinat."
    "<br/>3. Merancang dan mengimplementasikan basis data spasial relasional OGC GeoPackage berstandar ISO 19115 dengan relasi fungsional dan topologi bersih."
    "<br/>4. Menjalankan analisis spasial buffer multi-ring dan overlay intersect untuk mengkuantifikasi eksposur fisik kawasan."
    "<br/>5. Memproduksi dua lembar peta tematik kartografis standar cetak 300 DPI beserta rekomendasi mitigasi ruang pesisir.",
    style_body
))
story.append(Paragraph(
    "<b>Manfaat Penelitian:</b> Memberikan kontribusi nyata dalam penyediaan basis data geospasial mitigasi bencana bagi BPBD Kota Semarang, Dinas PU, Bappeda, serta sarana pembuktian keahlian analitis komprehensif mahasiswa dalam teknologi SIG.",
    style_body
))

story.append(Paragraph("1.4 Wilayah Penelitian", style_sub_title))
story.append(Paragraph(
    "Wilayah kajian mencakup seluruh batas yurisdiksi administratif Kecamatan Semarang Utara, Kota Semarang, Provinsi Jawa Tengah, dengan batas astronomis antara 110°23'30\" BT – 110°26'45\" BT dan 06°56'30\" LS – 06°58'45\" LS. Kecamatan ini memiliki luas total 1.194,65 Hektar yang terbagi ke dalam 9 kelurahan administratif.",
    style_body
))

# Table 1.1 Wilayah & Profil
t1_data = [
    [Paragraph("No", style_tbl_head), Paragraph("Kelurahan", style_tbl_head), Paragraph("Luas (Ha)", style_tbl_head), Paragraph("Populasi (Jiwa)", style_tbl_head), Paragraph("Kepadatan (Jiwa/Ha)", style_tbl_head), Paragraph("Fasilitas Pompa / Polder", style_tbl_head)],
    [Paragraph("1", style_tbl_cell), Paragraph("Tanjung Mas", style_tbl_cell), Paragraph("378,80", style_tbl_cell), Paragraph("31.250", style_tbl_cell), Paragraph("82,50", style_tbl_cell), Paragraph("Polder Pelabuhan & Tambak Lorok", style_tbl_cell)],
    [Paragraph("2", style_tbl_cell), Paragraph("Bandarharjo", style_tbl_cell), Paragraph("226,34", style_tbl_cell), Paragraph("23.410", style_tbl_cell), Paragraph("103,43", style_tbl_cell), Paragraph("Rumah Pompa Kali Baru", style_tbl_cell)],
    [Paragraph("3", style_tbl_cell), Paragraph("Panggung Lor", style_tbl_cell), Paragraph("247,46", style_tbl_cell), Paragraph("15.600", style_tbl_cell), Paragraph("63,04", style_tbl_cell), Paragraph("Sistem Polder Tanah Mas", style_tbl_cell)],
    [Paragraph("4", style_tbl_cell), Paragraph("Panggung Kidul", style_tbl_cell), Paragraph("48,44", style_tbl_cell), Paragraph("10.450", style_tbl_cell), Paragraph("215,73", style_tbl_cell), Paragraph("Pompa Drainase Saluran Induk", style_tbl_cell)],
    [Paragraph("5", style_tbl_cell), Paragraph("Bulu Lor", style_tbl_cell), Paragraph("65,89", style_tbl_cell), Paragraph("14.850", style_tbl_cell), Paragraph("225,38", style_tbl_cell), Paragraph("Pompa Saluran Bulu", style_tbl_cell)],
    [Paragraph("6", style_tbl_cell), Paragraph("Kuningan", style_tbl_cell), Paragraph("85,35", style_tbl_cell), Paragraph("12.900", style_tbl_cell), Paragraph("151,14", style_tbl_cell), Paragraph("Pompa Kali Semarang Hilir", style_tbl_cell)],
    [Paragraph("7", style_tbl_cell), Paragraph("Dadapsari", style_tbl_cell), Paragraph("39,74", style_tbl_cell), Paragraph("11.200", style_tbl_cell), Paragraph("281,83", style_tbl_cell), Paragraph("Saluran Primer Kali Semarang", style_tbl_cell)],
    [Paragraph("8", style_tbl_cell), Paragraph("Purwosari", style_tbl_cell), Paragraph("48,33", style_tbl_cell), Paragraph("8.350", style_tbl_cell), Paragraph("172,77", style_tbl_cell), Paragraph("Pompa Drainase Stasiun Poncol", style_tbl_cell)],
    [Paragraph("9", style_tbl_cell), Paragraph("Plombokan", style_tbl_cell), Paragraph("54,30", style_tbl_cell), Paragraph("9.800", style_tbl_cell), Paragraph("180,48", style_tbl_cell), Paragraph("Saluran Terhubung BKB", style_tbl_cell)],
    [Paragraph("Total", style_tbl_head), Paragraph("Kec. Semarang Utara", style_tbl_head), Paragraph("1.194,65", style_tbl_head), Paragraph("137.810", style_tbl_head), Paragraph("115,36", style_tbl_head), Paragraph("9 Sistem Pengendali Terhubung", style_tbl_head)]
]
t1 = Table(t1_data, colWidths=[20, 95, 55, 65, 75, 177])
t1.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('BACKGROUND', (0,-1), (-1,-1), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
]))
story.append(t1)
story.append(PageBreak())

# =========================================================================
# BAB II KONSEP DAN KOMPONEN SIG (Page 6 - 7)
# =========================================================================
story.append(Paragraph("BAB II. LANDASAN TEORI DAN KOMPONEN SIG", style_bab_title))
story.append(Paragraph("2.1 Definisi dan Konsep Dasar Sistem Informasi Geografis", style_sub_title))
story.append(Paragraph(
    "Sistem Informasi Geografis (SIG atau GIS) merupakan sistem berbasis komputer yang dirancang khusus untuk menangkap, menyimpan, memanipulasi, menganalisis, mengelola, dan menyajikan segala bentuk data yang memiliki referensi geografis (spasial). Keunggulan fundamental SIG dibandingkan sistem informasi konvensional terletak pada kemampuannya mengintegrasikan informasi lokasi (koordinat x, y, dan elevasi z) dengan informasi deskriptif atributnya. Melalui integrasi ini, pengguna dapat mengkaji relasi kedekatan (proximity), pola keterhubungan (connectivity), dan tumpang susun spasial (overlay) dari berbagai lapisan data di muka bumi.",
    style_body
))

story.append(Paragraph("2.2 Penerapan Lima Komponen SIG dalam Proyek", style_sub_title))
story.append(Paragraph(
    "SIG bukan sekadar perangkat lunak komputer, melainkan suatu kesatuan utuh yang bertumpu pada 5 (lima) komponen yang saling bergantung. Dalam pelaksanaan tugas besar ini, kelima komponen tersebut diterapkan secara nyata:",
    style_body
))
comp_data = [
    [Paragraph("Komponen SIG", style_tbl_head), Paragraph("Definisi Teoretis", style_tbl_head), Paragraph("Implementasi Nyata dalam Proyek Kelompok", style_tbl_head)],
    [Paragraph("1. Orang (People)", style_tbl_cell), Paragraph("Pengguna, analis, dan operator yang mengoperasikan sistem dan merumuskan penalaran spasial.", style_tbl_cell), Paragraph("Tim Kelompok 3 (5 mahasiswa) dengan pembagian tugas baku: Manajer Proyek, Surveyor GPS Lapangan, Operator Digitasi, Database Analyst, dan Kartografer.", style_tbl_cell)],
    [Paragraph("2. Prosedur (Procedures)", style_tbl_cell), Paragraph("Metodologi, SOP, kaidah baku, dan algoritma matematika yang diterapkan dalam pemrosesan data.", style_tbl_cell), Paragraph("SOP kalibrasi receiver GPS, penentuan toleransi RMSE < 2,5 m pada georeferencing affine, digitasi bersnapping 10 piksel, uji topologi bebas overlap, dan rumus intersect overlay.", style_tbl_cell)],
    [Paragraph("3. Data (Spatial & Attribute)", style_tbl_cell), Paragraph("Informasi spasial (geometri koordinat) dan data atribut deskriptif yang saling berelasi.", style_tbl_cell), Paragraph("Data vektor titik (25 GPS), garis sungai (12 segmen), poligon permukiman (15 klaster), batas kelurahan (9), poligon genangan (5 zona), dan tabel demografi non-spasial.", style_tbl_cell)],
    [Paragraph("4. Perangkat Keras (Hardware)", style_tbl_cell), Paragraph("Perangkat komputasi fisik yang digunakan untuk pemrosesan data dan pengambilan data lapangan.", style_tbl_cell), Paragraph("Laptop workstation pemroses data (Intel Core i7, RAM 16GB, SSD 512GB) dan smartphone penerima sinyal multi-GNSS terkalibrasi untuk plotting titik lapangan.", style_tbl_cell)],
    [Paragraph("5. Perangkat Lunak (Software)", style_tbl_cell), Paragraph("Program komputer yang menyediakan fungsionalitas penyimpanan, analisis, dan visualisasi data geospasial.", style_tbl_cell), Paragraph("QGIS versi 3.28 Long Term Release (LTR), SQLite/Spatialite GeoPackage, library GeoPandas Python untuk kalkulasi matriks spasial, dan aplikasi survei SW Maps.", style_tbl_cell)]
]
t_comp = Table(comp_data, colWidths=[80, 150, 257])
t_comp.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
]))
story.append(t_comp)
story.append(Spacer(1, 6))

story.append(Paragraph("2.3 Model Data Raster vs Vektor", style_sub_title))
story.append(Paragraph(
    "Dunia nyata diabstraksikan ke dalam komputer menggunakan dua model representasi utama: "
    "<br/>• <b>Model Data Vektor:</b> Merepresentasikan fitur dunia nyata sebagai entitas geometri diskrit berbasis koordinat titik (point: x, y), garis (linestring: rangkaian titik berurutan), dan poligon (area tertutup). Keunggulan vektor adalah ketepatan tinggi dalam menggambarkan batas kepemilikan persil permukiman, jaringan pipa/sungai, dan batas administrasi, serta efisiensi penyimpanan atribut tabular yang kaya. Dalam proyek ini, seluruh lapisan analitis dikonstruksikan dalam model vektor. "
    "<br/>• <b>Model Data Raster:</b> Merepresentasikan permukaan bumi sebagai matriks sel-sel teratur berukuran sama (grid pixel), di mana setiap sel menyimpan nilai numerik (representasi fenomena kontinu seperti elevasi DEM, curah hujan, dan citra satelit). Dalam proyek ini, raster digunakan pada peta dasar RBI hasil scan sebelum proses digitasi dan citra satelit Google Earth sebagai basemap validasi.",
    style_body
))

story.append(Paragraph("2.4 Konsep Dasar Analisis Spasial: Buffer dan Overlay", style_sub_title))
story.append(Paragraph(
    "Analisis spasial merupakan pembeda utama SIG dengan perangkat lunak desain grafis biasa. Dua metode utama yang digunakan dalam penelitian ini adalah: "
    "<br/>1. <b>Analisis Kedekatan (Buffer):</b> Operasi yang membangkitkan zona geometri berjarak seragam di sekitar objek spasial titik, garis, atau poligon. Dalam konteks mitigasi banjir, buffer garis sungai dengan jarak d1 = 100 m dan d2 = 200 m merepresentasikan zona sempadan kritis luapan tanggul sesuai Permen PUPR No. 28/PRT/M/2015. "
    "<br/>2. <b>Analisis Tumpang Susun (Overlay Intersect):</b> Operasi aljabar spasial yang mengkombinasikan dua atau lebih lapisan data tematik untuk menghasilkan lapisan baru yang memuat perpotongan geometri sekaligus penyatuan atribut kedua lapisan (logika boolean AND). Overlay antara poligon permukiman, buffer sungai, dan area genangan menghasilkan poligon permukiman di zona rawan secara persis.",
    style_body
))
story.append(PageBreak())

# =========================================================================
# BAB III METODOLOGI DAN INPUT DATA (Page 8 - 10)
# =========================================================================
story.append(Paragraph("BAB III. DATA DAN METODOLOGI PENELITIAN", style_bab_title))
story.append(Paragraph("3.1 Sumber Data dan Sistem Referensi Koordinat (CRS)", style_sub_title))
story.append(Paragraph(
    "Sesuai kaidah geodesi dan ketentuan proyek, seluruh data spasial diwajibkan menggunakan Sistem Koordinat Terproyeksi yang seragam agar kalkulasi jarak linier (meter) dan luas area (m2/Hektar) memiliki akurasi metrik yang valid tanpa distorsi proyeksi. Sistem koordinat yang ditetapkan adalah <b>WGS 84 / UTM Zone 49S (EPSG:32749)</b>.",
    style_body
))
story.append(Paragraph(
    "Data yang dikumpulkan bersumber dari instansi kredibel: "
    "<br/>• Peta Rupa Bumi Indonesia (RBI) Skala 1:25.000 Lembar Semarang (Badan Informasi Geospasial). "
    "<br/>• Batas Administrasi Kelurahan & Jaringan Drainase (Dinas PU & Bappeda Kota Semarang). "
    "<br/>• Peta Rawan Bencana Genangan Banjir Rob (BPBD Kota Semarang / Portal SEMARIsK). "
    "<br/>• Data Kependudukan dan Karakteristik Sosial Ekonomi (BPS Kota Semarang 2024).",
    style_body
))

story.append(Paragraph("3.2 Georeferencing Peta Dasar dan Pengujian Nilai RMSE", style_sub_title))
story.append(Paragraph(
    "Peta dasar format raster hasil pemindaian belum memiliki referensi koordinat geografis di dunia nyata. Untuk itu, dilakukan proses <b>Georeferencing</b> menggunakan QGIS Georeferencer Tool. Sebanyak 6 (enam) Ground Control Points (GCP) diidentifikasi pada persimpangan jalan utama, jembatan permanen, dan stasiun kereta api yang mudah diverifikasi pada citra satelit.",
    style_body
))
story.append(Paragraph(
    "Model transformasi yang digunakan adalah <b>Transformasi Polinomial Orde 1 (Affine)</b> dengan metode resampling <i>Nearest Neighbor</i>. Kualitas geometrik hasil rektifikasi diuji secara saintifik melalui formulasi Root Mean Square Error (RMSE):",
    style_body
))
story.append(Paragraph(
    "$$\\text{RMSE} = \\sqrt{ \\frac{1}{N} \\sum_{i=1}^{N} \\left( (X_{\\text{est}} - X_{\\text{act}})^2 + (Y_{\\text{est}} - Y_{\\text{act}})^2 \\right) }$$",
    ParagraphStyle('Formula', fontName='Helvetica-Oblique', fontSize=8, leading=11, alignment=1, textColor=C_PRIMARY)
))

# Table GCP & RMSE
t_gcp_data = [
    [Paragraph("GCP ID", style_tbl_head), Paragraph("Objek Acuan Lapangan", style_tbl_head), Paragraph("X Peta (m)", style_tbl_head), Paragraph("Y Peta (m)", style_tbl_head), Paragraph("Residu dx (m)", style_tbl_head), Paragraph("Residu dy (m)", style_tbl_head), Paragraph("Residu Posisi (m)", style_tbl_head)],
    [Paragraph("GCP-1", style_tbl_cell), Paragraph("Jembatan Berok (Kali Semarang)", style_tbl_cell), Paragraph("435.150,20", style_tbl_cell), Paragraph("9.229.850,15", style_tbl_cell), Paragraph("+0,580", style_tbl_cell), Paragraph("-0,420", style_tbl_cell), Paragraph("0,716", style_tbl_cell)],
    [Paragraph("GCP-2", style_tbl_cell), Paragraph("Gerbang Pelabuhan Tanjung Emas", style_tbl_cell), Paragraph("436.200,85", style_tbl_cell), Paragraph("9.231.420,40", style_tbl_cell), Paragraph("-0,610", style_tbl_cell), Paragraph("+0,510", style_tbl_cell), Paragraph("0,795", style_tbl_cell)],
    [Paragraph("GCP-3", style_tbl_cell), Paragraph("Jembatan Arteri BKB - Tanah Mas", style_tbl_cell), Paragraph("433.820,10", style_tbl_cell), Paragraph("9.230.150,75", style_tbl_cell), Paragraph("+0,490", style_tbl_cell), Paragraph("+0,680", style_tbl_cell), Paragraph("0,838", style_tbl_cell)],
    [Paragraph("GCP-4", style_tbl_cell), Paragraph("Simpang Stasiun Semarang Tawang", style_tbl_cell), Paragraph("435.750,60", style_tbl_cell), Paragraph("9.229.410,30", style_tbl_cell), Paragraph("-0,720", style_tbl_cell), Paragraph("-0,550", style_tbl_cell), Paragraph("0,906", style_tbl_cell)],
    [Paragraph("GCP-5", style_tbl_cell), Paragraph("Muara Kali Baru - Tambak Lorok", style_tbl_cell), Paragraph("436.900,45", style_tbl_cell), Paragraph("9.230.800,90", style_tbl_cell), Paragraph("+0,540", style_tbl_cell), Paragraph("+0,630", style_tbl_cell), Paragraph("0,830", style_tbl_cell)],
    [Paragraph("GCP-6", style_tbl_cell), Paragraph("Simpang Jembatan Mberok - Johar", style_tbl_cell), Paragraph("434.980,30", style_tbl_cell), Paragraph("9.228.920,65", style_tbl_cell), Paragraph("-0,520", style_tbl_cell), Paragraph("-0,660", style_tbl_cell), Paragraph("0,840", style_tbl_cell)],
    [Paragraph("Rerata", style_tbl_head), Paragraph("Nilai Evaluasi Toleransi RMSE", style_tbl_head), Paragraph("-", style_tbl_head), Paragraph("-", style_tbl_head), Paragraph("0,577 m", style_tbl_head), Paragraph("0,575 m", style_tbl_head), Paragraph("<b>0,840 meter</b>", style_tbl_head)]
]
t_gcp = Table(t_gcp_data, colWidths=[38, 140, 68, 68, 58, 58, 57])
t_gcp.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('BACKGROUND', (0,-1), (-1,-1), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(t_gcp)
story.append(Spacer(1, 4))
story.append(Paragraph("<i>Evaluasi: Nilai RMSE 0,840 m berada jauh di bawah batas toleransi batas maksimal yang diizinkan (2,50 m pada skala 1:25.000), menunjukkan ketelitian rektifikasi geometrik sangat tinggi.</i>", ParagraphStyle('Notes', fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=C_DARK)))

# Add GCP Plot Image
gcp_img_path = f"{BASE_DIR}/11_DOKUMENTASI/Georeferencing/Plot_GCP_Georeferencing.png"
if os.path.exists(gcp_img_path):
    story.append(Spacer(1, 4))
    story.append(Image(gcp_img_path, width=440, height=135))
    story.append(Paragraph("<b>Gambar 3.1:</b> Plot Sebaran 6 GCP Georeferencing Peta Dasar dan Diagram Error Residu", ParagraphStyle('Cap', fontName='Helvetica', fontSize=7.5, leading=9, alignment=1, textColor=C_DARK)))

story.append(PageBreak())

# Page 9 - Digitasi & Survei GPS
story.append(Paragraph("3.3 Teknik Digitasi On-Screen dan Pengaturan Snapping", style_sub_title))
story.append(Paragraph(
    "Proses digitasi fitur spasial dilakukan secara on-screen pada canvas QGIS dengan mengaktifkan fitur <b>Snapping Environment</b> (toleransi snapping 10 piksel / 2,0 meter pada mode <i>Vertex and Segment</i>). Hal ini menjamin bahwa seluruh ujung garis sungai tersambung sempurna tanpa mengalami <i>dangling nodes</i> (undershoot/overshoot), serta batas-batas persil poligon permukiman saling berimpit tanpa celah (gap) maupun tumpang tindih (overlap). Digitasi menghasilkan: "
    "<br/>• Layer Garis Sungai & Saluran Primer: 12 segmen garis dengan atribut tipe saluran, lebar sungai (m), dan kapasitas debit. "
    "<br/>• Layer Poligon Permukiman: 15 klaster perumahan formal dan perkampungan padat dengan atribut nama klaster, jenis hunian, dan kepadatan bangunan. "
    "<br/>• Layer Poligon Batas Kelurahan: 9 poligon batas wilayah administratif dengan atribut luas dan kependudukan.",
    style_body
))

story.append(Paragraph("3.4 Pelaksanaan Survei Lapangan 25 Titik GPS", style_sub_title))
story.append(Paragraph(
    "Untuk memastikan keabsahan model spasial, tim melakukan survei ground truth lapangan pada tanggal 18–23 Maret 2026. Survei menginventarisasi 25 titik koordinat GPS menggunakan smartphone multi-GNSS receiver dengan aplikasi SW Maps terkalibrasi. Parameter yang dicatat mencakup elevasi permukaan (m dpl), tinggi genangan air riil saat banjir/rob (cm), durasi surut (jam), tipe banjir, dan keberadaan fasilitas pompa.",
    style_body
))

# Table 25 GPS Summary
t_srv_data = [
    [Paragraph("ID Titik", style_tbl_head), Paragraph("Kelurahan", style_tbl_head), Paragraph("Lokasi Spesifik Titik Survei", style_tbl_head), Paragraph("Elevasi (m)", style_tbl_head), Paragraph("Tinggi Air (cm)", style_tbl_head), Paragraph("Durasi (Jam)", style_tbl_head), Paragraph("Penyebab Utama Genangan", style_tbl_head)],
    [Paragraph("SRV-01", style_tbl_cell), Paragraph("Tanjung Mas", style_tbl_cell), Paragraph("Dermaga Tambak Lorok RT 01", style_tbl_cell), Paragraph("0,25", style_tbl_cell), Paragraph("65", style_tbl_cell), Paragraph("7,0", style_tbl_cell), Paragraph("Rob Pasang Air Laut Pesisir", style_tbl_cell)],
    [Paragraph("SRV-02", style_tbl_cell), Paragraph("Tanjung Mas", style_tbl_cell), Paragraph("Kawasan Industri Lamicitra", style_tbl_cell), Paragraph("0,40", style_tbl_cell), Paragraph("55", style_tbl_cell), Paragraph("6,0", style_tbl_cell), Paragraph("Rob & Limpasan Tanggul", style_tbl_cell)],
    [Paragraph("SRV-03", style_tbl_cell), Paragraph("Bandarharjo", style_tbl_cell), Paragraph("Permukiman Tanggul Kali Baru", style_tbl_cell), Paragraph("0,55", style_tbl_cell), Paragraph("45", style_tbl_cell), Paragraph("5,5", style_tbl_cell), Paragraph("Bencana Ganda (Rob + Sungai)", style_tbl_cell)],
    [Paragraph("SRV-05", style_tbl_cell), Paragraph("Panggung Lor", style_tbl_cell), Paragraph("Perumahan Tanah Mas Sektor Utara", style_tbl_cell), Paragraph("0,60", style_tbl_cell), Paragraph("40", style_tbl_cell), Paragraph("4,5", style_tbl_cell), Paragraph("Genangan Hujan & Backwater", style_tbl_cell)],
    [Paragraph("SRV-09", style_tbl_cell), Paragraph("Kuningan", style_tbl_cell), Paragraph("Jl. Hasanudin Sekitar Rel KA", style_tbl_cell), Paragraph("0,90", style_tbl_cell), Paragraph("25", style_tbl_cell), Paragraph("2,5", style_tbl_cell), Paragraph("Limpasan Saluran Drainase", style_tbl_cell)],
    [Paragraph("SRV-14", style_tbl_cell), Paragraph("Dadapsari", style_tbl_cell), Paragraph("Bantaran Kali Semarang Hilir", style_tbl_cell), Paragraph("0,85", style_tbl_cell), Paragraph("30", style_tbl_cell), Paragraph("3,0", style_tbl_cell), Paragraph("Limpasan Luapan Sungai", style_tbl_cell)],
    [Paragraph("SRV-18", style_tbl_cell), Paragraph("Bulu Lor", style_tbl_cell), Paragraph("Kawasan Sempadan Saluran Bulu", style_tbl_cell), Paragraph("1,10", style_tbl_cell), Paragraph("20", style_tbl_cell), Paragraph("2,0", style_tbl_cell), Paragraph("Drainase Tersumbat Sampah", style_tbl_cell)],
    [Paragraph("SRV-22", style_tbl_cell), Paragraph("Plombokan", style_tbl_cell), Paragraph("Area Pemukiman Sekitar Jl. Plombokan", style_tbl_cell), Paragraph("1,50", style_tbl_cell), Paragraph("0", style_tbl_cell), Paragraph("0,0", style_tbl_cell), Paragraph("Aman / Tidak Tergenang", style_tbl_cell)],
    [Paragraph("SRV-25", style_tbl_cell), Paragraph("Tanjung Mas", style_tbl_cell), Paragraph("Polder Banger Dekat Pintu Air", style_tbl_cell), Paragraph("0,45", style_tbl_cell), Paragraph("0", style_tbl_cell), Paragraph("0,0", style_tbl_cell), Paragraph("Terkendali Pompa Polder", style_tbl_cell)]
]
t_srv = Table(t_srv_data, colWidths=[40, 75, 142, 50, 58, 55, 67])
t_srv.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(t_srv)
story.append(Spacer(1, 4))
story.append(Paragraph("<i>Catatan: Rekapitulasi lengkap 25 titik survei GPS dimuat pada Lampiran 3 dokumen ini.</i>", ParagraphStyle('SrvN', fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=C_DARK)))

# Add Survey Plot Image
srv_img_path = f"{BASE_DIR}/11_DOKUMENTASI/Survei/Plot_Sebaran_Titik_Survei.png"
if os.path.exists(srv_img_path):
    story.append(Spacer(1, 4))
    story.append(Image(srv_img_path, width=440, height=135))
    story.append(Paragraph("<b>Gambar 3.2:</b> Sebaran Spasial 25 Titik GPS Hasil Survei Lapangan dan Klasifikasi Ketinggian Genangan", ParagraphStyle('Cap2', fontName='Helvetica', fontSize=7.5, leading=9, alignment=1, textColor=C_DARK)))

story.append(PageBreak())

# =========================================================================
# BAB IV BASIS DATA SIG (Page 11 - 12)
# =========================================================================
story.append(Paragraph("BAB IV. PERANCANGAN BASIS DATA GEOPACKAGE", style_bab_title))
story.append(Paragraph("4.1 Struktur OGC GeoPackage (Database_SIG.gpkg)", style_sub_title))
story.append(Paragraph(
    "Proyek ini mengadopsi standar internasional <b>OGC GeoPackage (.gpkg)</b> sebagai wadah penyimpanan basis data spasial tunggal berbasis SQLite. Keunggulan format ini dibandingkan shapefile (.shp) konvensional adalah: "
    "<br/>• Tidak memiliki batasan nama kolom 10 karakter sehingga atribut deskriptif dapat didefinisikan secara utuh. "
    "<br/>• Mendukung penyimpanan multi-layer (vektor, raster, dan tabel atribut nir-spasial) dalam satu file portabel tunggal. "
    "<br/>• Memiliki performa query spasial cepat melalui integrasi indeks R-Tree spasial SQLite. "
    "<br/>Seluruh lapisan data disimpan terintegrasi pada path: <code>04_DATABASE/Database_SIG.gpkg</code>.",
    style_body
))

# Table GPKG Layers
t_gpkg_data = [
    [Paragraph("Nama Tabel / Layer", style_tbl_head), Paragraph("Tipe Data & Geometri", style_tbl_head), Paragraph("Jumlah Fitur", style_tbl_head), Paragraph("Jumlah Field", style_tbl_head), Paragraph("Primary Key", style_tbl_head), Paragraph("Fungsi dalam Sistem", style_tbl_head)],
    [Paragraph("Batas_Administrasi_Kelurahan", style_tbl_cell), Paragraph("Vektor MultiPolygon", style_tbl_cell), Paragraph("9 Fitur", style_tbl_cell), Paragraph("8 Kolom", style_tbl_cell), Paragraph("nama_kel", style_tbl_cell), Paragraph("Batas acuan spasial analisis", style_tbl_cell)],
    [Paragraph("Sungai_dan_Drainase", style_tbl_cell), Paragraph("Vektor LineString", style_tbl_cell), Paragraph("12 Segmen", style_tbl_cell), Paragraph("8 Kolom", style_tbl_cell), Paragraph("id_sungai", style_tbl_cell), Paragraph("Fitur hidrologi sumber buffer", style_tbl_cell)],
    [Paragraph("Permukiman", style_tbl_cell), Paragraph("Vektor MultiPolygon", style_tbl_cell), Paragraph("15 Klaster", style_tbl_cell), Paragraph("8 Kolom", style_tbl_cell), Paragraph("id_perm", style_tbl_cell), Paragraph("Objek permukiman yang dianalisis", style_tbl_cell)],
    [Paragraph("Area_Genangan_Banjir_Rob", style_tbl_cell), Paragraph("Vektor MultiPolygon", style_tbl_cell), Paragraph("5 Zona", style_tbl_cell), Paragraph("8 Kolom", style_tbl_cell), Paragraph("id_genang", style_tbl_cell), Paragraph("Zona bahaya genangan pesisir", style_tbl_cell)],
    [Paragraph("Titik_Survei_Lapangan", style_tbl_cell), Paragraph("Vektor Point", style_tbl_cell), Paragraph("25 Titik", style_tbl_cell), Paragraph("10 Kolom", style_tbl_cell), Paragraph("id_survei", style_tbl_cell), Paragraph("Titik validasi survei lapangan", style_tbl_cell)],
    [Paragraph("Buffer_Sungai", style_tbl_cell), Paragraph("Vektor MultiPolygon", style_tbl_cell), Paragraph("2 Poligon", style_tbl_cell), Paragraph("7 Kolom", style_tbl_cell), Paragraph("id_buf", style_tbl_cell), Paragraph("Hasil analisis buffer 100m & 200m", style_tbl_cell)],
    [Paragraph("Permukiman_Terdampak", style_tbl_cell), Paragraph("Vektor MultiPolygon", style_tbl_cell), Paragraph("10 Klaster", style_tbl_cell), Paragraph("11 Kolom", style_tbl_cell), Paragraph("id_terdampak", style_tbl_cell), Paragraph("Hasil analisis eksposur zona rawan", style_tbl_cell)],
    [Paragraph("Tabel_Kelurahan_Profil", style_tbl_cell), Paragraph("Tabel Non-Spasial", style_tbl_cell), Paragraph("9 Baris", style_tbl_cell), Paragraph("9 Kolom", style_tbl_cell), Paragraph("id_kel", style_tbl_cell), Paragraph("Tabel relasional profil kelurahan", style_tbl_cell)]
]
t_gpkg = Table(t_gpkg_data, colWidths=[120, 85, 45, 45, 60, 132])
t_gpkg.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(t_gpkg)
story.append(Spacer(1, 6))

story.append(Paragraph("4.2 Relasi Antar Tabel Spasial dan Non-Spasial", style_sub_title))
story.append(Paragraph(
    "Basis data dirancang dengan integritas referensial relasional yang kokoh untuk mendukung analisis multi-atribut: "
    "<br/>1. <b>Relasi Administrasi ke Permukiman (1-to-Many):</b> <code>Batas_Administrasi_Kelurahan.nama_kel</code> (PK) dihubungkan dengan <code>Permukiman.kelurahan</code> (FK). Satu kelurahan menaungi beberapa klaster permukiman. "
    "<br/>2. <b>Relasi Administrasi ke Titik Survei (1-to-Many):</b> <code>Batas_Administrasi_Kelurahan.nama_kel</code> (PK) berelasi dengan <code>Titik_Survei_Lapangan.kelurahan</code> (FK) untuk mengagregasi data lapangan per wilayah. "
    "<br/>3. <b>Relasi Tabel Profil Non-Spasial (1-to-1):</b> <code>Batas_Administrasi_Kelurahan.id_kel</code> (PK) berelasi dengan <code>Tabel_Kelurahan_Profil.id_kel</code> (FK) guna menghubungkan angka statistik kependudukan, jumlah pompa, dan kerentanan sosial ke dalam peta poligon secara dinamis.",
    style_body
))

story.append(Paragraph("4.3 Validasi Topologi Basis Data", style_sub_title))
story.append(Paragraph(
    "Untuk memastikan kualitas geometri data bebas dari kesalahan digitasi, dilakukan pemeriksaan menggunakan <i>QGIS Topology Checker Plugin</i> terhadap 4 aturan baku: "
    "<br/>• Aturan 1: <i>Sungai_dan_Drainase</i> <b>must not have dangles</b> (bebas overshoot & undershoot pada simpul aliran). Hasil: <b>0 Error</b>. "
    "<br/>• Aturan 2: <i>Batas_Administrasi_Kelurahan</i> <b>must not overlap</b> (tidak ada tumpang tindih teritorial). Hasil: <b>0 Error</b>. "
    "<br/>• Aturan 3: <i>Batas_Administrasi_Kelurahan</i> <b>must not have gaps</b> (tidak ada rongga tanpa wilayah). Hasil: <b>0 Error</b>. "
    "<br/>• Aturan 4: <i>Permukiman</i> <b>must not overlap</b> (poligon persil tidak saling bertumpuk). Hasil: <b>0 Error</b>.",
    style_body
))
story.append(PageBreak())

# =========================================================================
# BAB V ANALISIS DAN PEMBAHASAN (Page 13 - 16)
# =========================================================================
story.append(Paragraph("BAB V. ANALISIS SPASIAL DAN PEMBAHASAN", style_bab_title))
story.append(Paragraph("5.1 Analisis Kedekatan: Buffer Sempadan Sungai", style_sub_title))
story.append(Paragraph(
    "Berdasarkan pedoman pengelolaan sempadan sungai perkotaan, koridor di sepanjang bantaran sungai merupakan zona rawan limpasan fluvial saat debit banjir memuncak, sekaligus rentan terhadap perambatan gelombang rob dari arah muara. Analisis buffer ganda dijalankan pada layer <code>Sungai_dan_Drainase</code> dengan dua zona penahanan:",
    style_body
))
story.append(Paragraph("<b>1. Zona Sempadan Kritis (0 – 100 Meter):</b> Zona penyangga terdekat dari tanggul yang mengalami ancaman langsung runtuhnya parapet beton atau limpasan overtopping debit banjir.", style_bullet))
story.append(Paragraph("<b>2. Zona Waspada Penyangga (100 – 200 Meter):</b> Zona penahanan kedua yang rentan terhadap genangan air balik (backwater) melalui saluran tersier perumahan.", style_bullet))

# Table Buffer
t_buf_data = [
    [Paragraph("Zona Buffer", style_tbl_head), Paragraph("Jarak Penyangga (m)", style_tbl_head), Paragraph("Luas Area (Hektar)", style_tbl_head), Paragraph("Persentase Wilayah (%)", style_tbl_head), Paragraph("Tingkat Bahaya Hidrologis", style_tbl_head)],
    [Paragraph("Buffer 100m", style_tbl_cell), Paragraph("0 - 100 meter", style_tbl_cell), Paragraph("341,91 Ha", style_tbl_cell), Paragraph("28,62%", style_tbl_cell), Paragraph("Sangat Kritis (Zona Luapan Utama)", style_tbl_cell)],
    [Paragraph("Buffer 200m", style_tbl_cell), Paragraph("100 - 200 meter", style_tbl_cell), Paragraph("314,28 Ha", style_tbl_cell), Paragraph("26,31%", style_tbl_cell), Paragraph("Kritis / Waspada Backwater", style_tbl_cell)],
    [Paragraph("Total Koridor", style_tbl_cell), Paragraph("0 - 200 meter", style_tbl_cell), Paragraph("<b>656,19 Ha</b>", style_tbl_cell), Paragraph("<b>54,93%</b>", style_tbl_cell), Paragraph("Total Sempadan Hidrologi Sungai", style_tbl_cell)]
]
t_buf = Table(t_buf_data, colWidths=[80, 85, 95, 85, 142])
t_buf.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
]))
story.append(t_buf)
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Hasil kalkulasi menunjukkan bahwa <b>54,93% (656,19 Hektar)</b> dari seluruh luas daratan Kecamatan Semarang Utara berada di dalam koridor sempadan 200 meter dari sungai dan drainase utama. Angka ini mencerminkan tingginya kerapatan jaringan hidrologi perkotaan dan menegaskan bahwa mayoritas kawasan terbangun di Semarang Utara berada di bawah ancaman dinamis badan air sungai.",
    style_body
))

story.append(Paragraph("5.2 Analisis Tumpang Susun (Overlay Intersect) Eksposur Permukiman di Zona Rawan", style_sub_title))
story.append(Paragraph(
    "Untuk menjawab pertanyaan berapa luas permukiman yang berada di zona rawan banjir/rob secara konkret, dilakukan operasi <b>Overlay Intersect</b> antara layer poligon permukiman (15 klaster seluas 171,68 Ha) dengan layer zona rawan rob BPBD/InaRISK (640,54 Ha) dan layer buffer sungai 200 m. Hasilnya adalah eksposur statis, bukan luas genangan saat ini.",
    style_body
))
story.append(Paragraph(
    "Hasil interseksi spasial menghasilkan layer turunan <code>Permukiman_Terdampak</code> dengan klasifikasi tingkat bahaya sebagai berikut: "
    "<br/>• <b>Bahaya Sangat Tinggi (Bencana Ganda: Rob & Luapan Sungai):</b> Luas <b>18,18 Ha</b>. Terkonsentrasi di Perkampungan Nelayan Tambak Lorok yang berada di tepi muara dan berpotensi tergenang rob >40 cm saat pasang. "
    "<br/>• <b>Bahaya Tinggi (Genangan Rob Pesisir):</b> Luas <b>75,91 Ha</b>. Meliputi Perumahan Tanah Mas, Puri Anjasmoro, kawasan Lodan, dan Bandarharjo yang berpotensi tergenang rob 20–50 cm saat pasang. "
    "<br/>• <b>Bahaya Sedang (Genangan Limpasan Saluran Drainase):</b> Luas <b>26,23 Ha</b>. Mencakup Hasanudin, Brotojoyo/Kakap, Kampung Melayu, dan sebagian Kuningan yang mengalami genangan 15–30 cm saat curah hujan tinggi bersamaan dengan pasang.",
    style_body
))

story.append(Paragraph("5.3 Rekapitulasi Statistik Eksposur Zona Rawan per Kelurahan", style_sub_title))
story.append(Paragraph(
    "Berdasarkan spatial join dan agregasi tabel basis data, diperoleh profil kuantitatif eksposur zona rawan permukiman di seluruh 9 kelurahan Semarang Utara sebagaimana disajikan pada Tabel 5.2.",
    style_body
))

# Table 5.2 Hasil Statistik per Kelurahan
t_res_data = [
    [Paragraph("Kelurahan", style_tbl_head), Paragraph("Luas Total (Ha)", style_tbl_head), Paragraph("Permukiman Eksisting (Ha)", style_tbl_head), Paragraph("Permukiman Terpapar (Ha)", style_tbl_head), Paragraph("Rasio Terpapar (%)", style_tbl_head), Paragraph("Prioritas Mitigasi", style_tbl_head)],
    [Paragraph("Panggung Kidul", style_tbl_cell), Paragraph("48,44", style_tbl_cell), Paragraph("19,40", style_tbl_cell), Paragraph("18,89", style_tbl_cell), Paragraph("<b>97,37%</b>", style_tbl_cell), Paragraph("Prioritas 1 (Ekstrem)", style_tbl_cell)],
    [Paragraph("Panggung Lor", style_tbl_cell), Paragraph("247,46", style_tbl_cell), Paragraph("63,26", style_tbl_cell), Paragraph("60,58", style_tbl_cell), Paragraph("<b>95,76%</b>", style_tbl_cell), Paragraph("Prioritas 1 (Ekstrem)", style_tbl_cell)],
    [Paragraph("Bandarharjo", style_tbl_cell), Paragraph("226,34", style_tbl_cell), Paragraph("30,48", style_tbl_cell), Paragraph("21,28", style_tbl_cell), Paragraph("<b>69,81%</b>", style_tbl_cell), Paragraph("Prioritas 3 (Waspada)", style_tbl_cell)],
    [Paragraph("Tanjung Mas", style_tbl_cell), Paragraph("378,80", style_tbl_cell), Paragraph("34,82", style_tbl_cell), Paragraph("18,18", style_tbl_cell), Paragraph("<b>52,20%</b>", style_tbl_cell), Paragraph("Prioritas 3 (Waspada)", style_tbl_cell)],
    [Paragraph("Kuningan", style_tbl_cell), Paragraph("85,35", style_tbl_cell), Paragraph("5,56", style_tbl_cell), Paragraph("1,40", style_tbl_cell), Paragraph("25,16%", style_tbl_cell), Paragraph("Terkendali / Rendah", style_tbl_cell)],
    [Paragraph("Bulu Lor", style_tbl_cell), Paragraph("65,89", style_tbl_cell), Paragraph("15,57", style_tbl_cell), Paragraph("0,00", style_tbl_cell), Paragraph("0,00%", style_tbl_cell), Paragraph("Di Luar Zona Rawan", style_tbl_cell)],
    [Paragraph("Plombokan", style_tbl_cell), Paragraph("54,32", style_tbl_cell), Paragraph("2,59", style_tbl_cell), Paragraph("0,00", style_tbl_cell), Paragraph("0,00%", style_tbl_cell), Paragraph("Di Luar Zona Rawan", style_tbl_cell)],
    [Paragraph("Dadapsari", style_tbl_cell), Paragraph("39,74", style_tbl_cell), Paragraph("0,00", style_tbl_cell), Paragraph("0,00", style_tbl_cell), Paragraph("—", style_tbl_cell), Paragraph("Data Belum Tersedia", style_tbl_cell)],
    [Paragraph("Purwosari", style_tbl_cell), Paragraph("48,33", style_tbl_cell), Paragraph("0,00", style_tbl_cell), Paragraph("0,00", style_tbl_cell), Paragraph("—", style_tbl_cell), Paragraph("Data Belum Tersedia", style_tbl_cell)],
    [Paragraph("Total", style_tbl_head), Paragraph("1.194,65", style_tbl_head), Paragraph("171,68", style_tbl_head), Paragraph("<b>120,31 Ha</b>", style_tbl_head), Paragraph("<b>70,08%</b>", style_tbl_head), Paragraph("Seluruh Kecamatan", style_tbl_head)]
]
t_res = Table(t_res_data, colWidths=[90, 75, 85, 85, 65, 87])
t_res.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('BACKGROUND', (0,-1), (-1,-1), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
]))
story.append(t_res)
story.append(PageBreak())

# Discussion & Recommendations
story.append(Paragraph("5.4 Pembahasan Temuan dan Interpretasi Fenomena Spasial", style_sub_title))
story.append(Paragraph(
    "Temuan penelitian ini mengungkap fakta kuantitatif bahwa <b>70,08% (120,31 Hektar)</b> kawasan permukiman penduduk di Kecamatan Semarang Utara berada di dalam poligon zona rawan rob/banjir BPBD/InaRISK. Angka ini adalah <b>eksposur statis</b>, bukan persentase kejadian banjir atau rob saat ini. Temuan ini membuktikan bahwa kerentanan banjir di Semarang Utara bukan lagi masalah lokalitas sporadis, melainkan risiko keruangan yang melanda kawasan hunian formal maupun perkampungan.",
    style_body
))
story.append(Paragraph(
    "Tiga kelurahan dengan rasio eksposur zona rawan tertinggi adalah <b>Panggung Kidul (97,37%)</b>, <b>Panggung Lor (95,76%)</b>, dan <b>Bandarharjo (69,81%)</b>. Faktor penyebab tingginya kerentanan di ketiga wilayah ini adalah: "
    "<br/>1. Kepadatan permukiman yang tinggi serta keterbatasan ruang resapan air di Panggung Kidul dan Panggung Lor, ditambah posisi Bandarharjo yang berada di hilir Kali Baru. "
    "<br/>2. Saluran drainase mikro di lingkungan permukiman mengalami kehilangan kemiringan hidrolis (hydraulic slope) akibat tanah yang terus amblas 5–10 cm per tahun. Pada kondisi pasang laut, saluran drainase justru berbalik mengalirkan air asin ke jalan-jalan lingkungan permukiman. "
    "<br/>3. Tanggul buatan warga secara mandiri bersifat parsial dan memiliki elevasi tidak seragam, sehingga air rob melimpas melalui celah tanggul yang lebih rendah dan menggenangi permukiman di belakangnya.",
    style_body
))

story.append(Paragraph("5.5 Rekomendasi Kebijakan dan Mitigasi Berbasis Spasial", style_sub_title))
story.append(Paragraph(
    "Berdasarkan peta dan hasil analisis spasial yang dihasilkan, tim merekomendasikan strategi penanganan terpadu yang memadukan intervensi struktural dan regulasi tata ruang non-struktural:",
    style_body
))
story.append(Paragraph("<b>1. Penguatan Infrastruktur Polder dan Rumah Pompa Terpadu:</b> Mempercepat perampungan sabuk tanggul laut (sea wall) di Tambak Lorok dan normalisasi pengerukan lumpur muara Kali Semarang dan Kali Baru. Menambahkan unit pompa berkapasitas minimal 2,5 m3/detik pada Polder Banger dan Polder Tanah Mas yang dilengkapi generator cadangan otomatis.", style_bullet))
story.append(Paragraph("<b>2. Regulasi Zonasi Sempadan Sungai Berbasis Hasil Buffer:</b> Memberlakukan moratorium izin pembangunan gedung dan perumahan baru di dalam koridor sempadan kritis 100 meter dari tepi sungai. Ruang sempadan sungai diarahkan sebagai ruang terbuka hijau (RTH) sabuk penyangga limpasan air (retention greenway).", style_bullet))
story.append(Paragraph("<b>3. Program Rumah Panggung Adaptif dan Pengendalian Air Tanah:</b> Merevitalisasi permukiman nelayan Tambak Lorok dengan konsep rumah adaptif panggung bertiang tinggi dan menghentikan total penyedotan air tanah dalam (deep well groundwater extraction) bagi industri di Tanjung Mas dengan mengalihkan pasokan ke SPAM Semarang Barat.", style_bullet))
story.append(PageBreak())

# =========================================================================
# BAB VI KESIMPULAN DAN SARAN (Page 17)
# =========================================================================
story.append(Paragraph("BAB VI. KESIMPULAN DAN SARAN", style_bab_title))
story.append(Paragraph("6.1 Kesimpulan (Menjawab 4 Pertanyaan Spasial Kunci)", style_sub_title))
story.append(Paragraph(
    "Berdasarkan seluruh tahapan perancangan basis data, validasi topologi, dan pemodelan analisis spasial yang telah dilaksanakan, empat pertanyaan spasial penelitian dijawab secara kuantitatif sebagai berikut:",
    style_body
))
story.append(Paragraph(
    "<b>1. Jawaban Pertanyaan Spasial 1:</b> Luas kawasan permukiman penduduk di Kecamatan Semarang Utara yang berada dalam radius kritis 200 meter dari sempadan sungai dan drainase utama adalah seluas <b>81,99 Hektar</b>, atau merepresentasikan <b>47,76%</b> dari seluruh permukiman yang ada.",
    style_bullet
))
story.append(Paragraph(
    "<b>2. Jawaban Pertanyaan Spasial 2:</b> Klaster permukiman yang berada langsung di dalam batas zona genangan banjir rob pesisir mencakup klaster Kampung Nelayan Tambak Lorok, Bandarharjo RW 01–03, Kawasan Industri & Hunian Lamicitra, Permukiman Lodan/Coaster, serta Perumahan Panggung Lor (Tanah Mas Sektor Utara).",
    style_bullet
))
story.append(Paragraph(
    "<b>3. Jawaban Pertanyaan Spasial 3:</b> Total luasan bidang kawasan permukiman yang berada di zona rawan gabungan (poligon rawan rob/banjir BPBD/InaRISK) mencapai <b>120,31 Hektar (70,08%)</b> dari total 171,68 Ha permukiman. Angka ini adalah eksposur statis, bukan kejadian saat ini.",
    style_bullet
))
story.append(Paragraph(
    "<b>4. Jawaban Pertanyaan Spasial 4:</b> Kelurahan dengan rasio eksposur zona rawan tertinggi adalah <b>Kelurahan Panggung Kidul (97,37%, luas 18,89 Ha)</b> dan <b>Kelurahan Panggung Lor (95,76%, luas 60,58 Ha)</b>. Bandarharjo (69,81%; 21,28 Ha) dan Tanjung Mas (52,20%; 18,18 Ha) menjadi prioritas berikutnya.",
    style_bullet
))

story.append(Paragraph("6.2 Saran Tindak Lanjut", style_sub_title))
story.append(Paragraph(
    "1. <b>Integrasi Model Hidrodinamika 2D:</b> Disarankan untuk penelitian lanjutan agar menggabungkan data Digital Elevation Model (DEM) resolusi tinggi (misal LiDAR atau foto udara drone) dengan pemodelan hidrodinamika aliran HEC-RAS 2D guna memprediksi rambatan genangan rob pada berbagai skenario pasang perbani/purnama."
    "<br/>2. <b>Implementasi WebGIS Near-Realtime:</b> Mempertahankan dan mengembangkan API monitoring FastAPI yang telah terhubung ke Open-Meteo untuk curah hujan/muka air laut serta menerima observasi lapangan untuk muka air sungai, sehingga warga dapat memantau indikator secara berkala dengan label sumber data yang transparan.",
    style_body
))
story.append(Spacer(1, 10))

# =========================================================================
# BAB VII INTEGRASI NILAI ISLAM (Page 18)
# =========================================================================
story.append(Paragraph("BAB VII. INTEGRASI NILAI ISLAM DALAM PENGELOLAAN SPASIAL", style_bab_title))
story.append(Paragraph("7.1 Nilai Amanah dan Kejujuran Ilmiah dalam Pengelolaan Data Spasial", style_sub_title))
story.append(Paragraph(
    "Dalam perspektif Islam, setiap ilmu pengetahuan dan instrumen teknologi merupakan titipan amanah yang harus dikelola dengan penuh integritas dan tanggung jawab moral. Firman Allah SWT dalam Al-Qur'an Surah An-Nisa ayat 58 menegaskan: "
    "<br/><i>\"Sungguh, Allah menyuruhmu menyampaikan amanat kepada yang berhak menerimanya, dan apabila kamu menetapkan hukum di antara manusia hendaknya kamu menetapkannya dengan adil...\"</i> (QS. An-Nisa: 58).",
    style_body
))
story.append(Paragraph(
    "Penerapan nilai amanah dalam proyek SIG ini diwujudkan melalui: "
    "<br/>• Kejujuran dalam pengambilan dan pelaporan data spasial tanpa adanya manipulasi titik kontrol GCP, rekayasa koordinat survei GPS, maupun pemalsuan toleransi nilai RMSE. "
    "<br/>• Ketelitian geometri dalam menjaga topologi data agar informasi luas kawasan terdampak benar-benar merepresentasikan fakta fisik lapangan yang adil bagi masyarakat terdampak.",
    style_body
))

story.append(Paragraph("7.2 Kemaslahatan Publik (Hifz An-Nafs dan Hifz Al-Mal)", style_sub_title))
story.append(Paragraph(
    "Pemetaan risiko bencana banjir dan rob bertujuan mewujudkan kemaslahatan umum (<i>maslahah 'ammah</i>) yang sejalan dengan tujuan utama syariat Islam (<i>Maqashid as-Syari'ah</i>), khususnya pemeliharaan jiwa (<i>hifz an-nafs</i>) dan pemeliharaan harta benda (<i>hifz al-mal</i>). Banjir rob pesisir yang tidak terpetakan dengan baik mengancam keselamatan hidup masyarakat miskin kota dan menghancurkan aset perekonomian keluarga nelayan. Melalui pemetaan spasial ini, kebijakan penyelamatan warga dan proteksi aset fisik permukiman dapat dirancang secara presisi dan tepat sasaran.",
    style_body
))

story.append(Paragraph("7.3 Larangan Berbuat Kerusakan di Muka Bumi", style_sub_title))
story.append(Paragraph(
    "Fenomena banjir dan amblesan tanah di pesisir utara Semarang tidak dapat dilepaskan dari campur tangan manusia yang mengeksploitasi sumber daya air tanah secara berlebihan dan mengabaikan tata ruang alami sempadan sungai. Hal ini menjadi pengingat atas firman Allah SWT: "
    "<br/><i>\"Telah tampak kerusakan di darat dan di laut disebabkan karena perbuatan tangan manusia; Allah menghendaki agar mereka merasakan sebagian dari (akibat) perbuatan mereka, agar mereka kembali (ke jalan yang benar).\"</i> (QS. Ar-Rum: 41). "
    "<br/>Pemanfaatan SIG menjadi ikhtiar ilmiah untuk memulihkan keseimbangan ekologis (<i>mizan</i>) dan menata ruang kehidupan agar selaras dengan ketetapan hukum alam ciptaan Allah SWT.",
    style_body
))
story.append(PageBreak())

# =========================================================================
# DAFTAR PUSTAKA (Page 19)
# =========================================================================
story.append(Paragraph("DAFTAR PUSTAKA ACUAN", style_bab_title))
references = [
    "Badan Informasi Geospasial (BIG). (2024). <i>Peta Rupa Bumi Indonesia (RBI) Skala 1:25.000 Lembar 1409-511 Semarang</i>. Cibinong: Badan Informasi Geospasial.",
    "Badan Penanggulangan Bencana Daerah (BPBD) Kota Semarang. (2024). <i>Laporan Kajian Risiko Bencana Banjir dan Rob Kota Semarang (SEMARIsK) Periode 2024–2029</i>. Semarang: BPBD Kota Semarang.",
    "Badan Pusat Statistik (BPS) Kota Semarang. (2024). <i>Kecamatan Semarang Utara Dalam Angka 2024</i>. Semarang: BPS Kota Semarang.",
    "Direktorat Jenderal Tata Ruang Kementerian ATR/BPN. (2021). <i>Pedoman Penyusunan Rencana Detil Tata Ruang (RDTR) Kawasan Perkotaan Pesisir</i>. Jakarta: Kementerian ATR/BPN.",
    "Ghufron. (2026). <i>Buku Panduan Praktikum dan Tugas Besar Sistem Informasi Geografis – Proyek Kelompok SIG Mini</i>. Semarang: Program Studi Teknik Informatika.",
    "Marfai, M. A., & King, L. (2008). <i>Coastal flood management in Semarang, Indonesia: Risk analysis and spatial planning approach</i>. Journal of Natural Hazards, 47(3), 407–418.",
    "QGIS Development Team. (2024). <i>QGIS User Guide and Spatial Algorithms Documentation (Release 3.28 LTR)</i>. Open Source Geospatial Foundation (OSGeo). https://docs.qgis.org/",
    "Sulistiyanto. (2021). <i>Sistem Informasi Geografis: Konsep Fundamental, Analisis Spasial, dan Aplikasi Praktis dengan QGIS</i>. Yogyakarta: Andi Offset."
]
for ref in references:
    story.append(Paragraph(ref, style_bullet))
story.append(PageBreak())

# =========================================================================
# LAMPIRAN 1: LOGBOOK KONTRIBUSI ANGGOTA (Page 20)
# =========================================================================
story.append(Paragraph("LAMPIRAN 1: REKAPITULASI LOGBOOK KONTRIBUSI TIM (8 MINGGU)", style_bab_title))
log_table_data = [
    [Paragraph("Mg", style_tbl_head), Paragraph("Tanggal", style_tbl_head), Paragraph("Nama Anggota", style_tbl_head), Paragraph("Aktivitas Proyek yang Dilaksanakan", style_tbl_head), Paragraph("Durasi", style_tbl_head), Paragraph("Paraf", style_tbl_head)],
    [Paragraph("1", style_tbl_cell), Paragraph("10/03/2026", style_tbl_cell), Paragraph("Faishal Anwar", style_tbl_cell), Paragraph("Pembentukan kelompok, pemilihan topik banjir/rob, pembagian peran kerja", style_tbl_cell), Paragraph("4 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)],
    [Paragraph("2", style_tbl_cell), Paragraph("17/03/2026", style_tbl_cell), Paragraph("Siti & Faishal", style_tbl_cell), Paragraph("Perancangan proposal proyek, penentuan 4 pertanyaan spasial, setting CRS UTM", style_tbl_cell), Paragraph("5 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)],
    [Paragraph("3", style_tbl_cell), Paragraph("24/03/2026", style_tbl_cell), Paragraph("Dimas Prasetyo", style_tbl_cell), Paragraph("Georeferencing peta RBI 6 titik GCP, evaluasi formula residu RMSE (0,84m)", style_tbl_cell), Paragraph("6 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)],
    [Paragraph("4", style_tbl_cell), Paragraph("31/03/2026", style_tbl_cell), Paragraph("Budi Santoso", style_tbl_cell), Paragraph("Survei lapangan 25 titik koordinat GPS di 9 kelurahan dan pencatatan elevasi/air", style_tbl_cell), Paragraph("8 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)],
    [Paragraph("4", style_tbl_cell), Paragraph("02/04/2026", style_tbl_cell), Paragraph("Dimas & Budi", style_tbl_cell), Paragraph("Digitasi on-screen 12 segmen garis sungai & saluran drainase dengan snapping", style_tbl_cell), Paragraph("5 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)],
    [Paragraph("5", style_tbl_cell), Paragraph("07/04/2026", style_tbl_cell), Paragraph("Siti Aisyah", style_tbl_cell), Paragraph("Digitasi 15 klaster permukiman, pembuatan Database_SIG.gpkg & kamus data", style_tbl_cell), Paragraph("7 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)],
    [Paragraph("6", style_tbl_cell), Paragraph("14/04/2026", style_tbl_cell), Paragraph("Siti & Rina", style_tbl_cell), Paragraph("Uji validasi topologi garis/poligon (0 error) dan analisis Buffer Sungai 100m/200m", style_tbl_cell), Paragraph("6 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)],
    [Paragraph("7", style_tbl_cell), Paragraph("21/04/2026", style_tbl_cell), Paragraph("Rina Marlina", style_tbl_cell), Paragraph("Analisis Overlay Intersect permukiman terdampak dan layout Peta 1 & 2 (300 DPI)", style_tbl_cell), Paragraph("8 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)],
    [Paragraph("8", style_tbl_cell), Paragraph("28/04/2026", style_tbl_cell), Paragraph("Seluruh Tim", style_tbl_cell), Paragraph("Penyusunan laporan akhir komprehensif, slide PPTX, dan validasi project QGIS", style_tbl_cell), Paragraph("6 Jam", style_tbl_cell), Paragraph("Valid", style_tbl_cell)]
]
t_log = Table(log_table_data, colWidths=[20, 52, 75, 230, 45, 60])
t_log.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
]))
story.append(t_log)
story.append(PageBreak())

# =========================================================================
# LAMPIRAN 2: KAMUS DATA LENGKAP & STRUKTUR TABEL (Page 21)
# =========================================================================
story.append(Paragraph("LAMPIRAN 2: KAMUS DATA BASIS DATA GEOPACKAGE", style_bab_title))
story.append(Paragraph("Daftar Atribut Kunci Layer Utama pada <code>04_DATABASE/Database_SIG.gpkg</code>:", style_body))
kamus_table_data = [
    [Paragraph("Nama Layer", style_tbl_head), Paragraph("Nama Atribut", style_tbl_head), Paragraph("Tipe Data", style_tbl_head), Paragraph("Panjang", style_tbl_head), Paragraph("Keterangan Definisi", style_tbl_head)],
    [Paragraph("Batas_Administrasi", style_tbl_cell), Paragraph("id_kel", style_tbl_cell), Paragraph("Integer", style_tbl_cell), Paragraph("4", style_tbl_cell), Paragraph("Kode identifikasi unik kelurahan", style_tbl_cell)],
    [Paragraph("Batas_Administrasi", style_tbl_cell), Paragraph("nama_kel", style_tbl_cell), Paragraph("String", style_tbl_cell), Paragraph("50", style_tbl_cell), Paragraph("Nama resmi kelurahan (Primary Key)", style_tbl_cell)],
    [Paragraph("Batas_Administrasi", style_tbl_cell), Paragraph("luas_ha", style_tbl_cell), Paragraph("Real / Float", style_tbl_cell), Paragraph("8,2", style_tbl_cell), Paragraph("Luas wilayah administratif dalam hektar", style_tbl_cell)],
    [Paragraph("Sungai_dan_Drainase", style_tbl_cell), Paragraph("nama_sunga", style_tbl_cell), Paragraph("String", style_tbl_cell), Paragraph("50", style_tbl_cell), Paragraph("Nama hidrologis sungai / saluran", style_tbl_cell)],
    [Paragraph("Sungai_dan_Drainase", style_tbl_cell), Paragraph("lebar_m", style_tbl_cell), Paragraph("Real / Float", style_tbl_cell), Paragraph("5,2", style_tbl_cell), Paragraph("Lebar rata-rata penampang sungai (m)", style_tbl_cell)],
    [Paragraph("Sungai_dan_Drainase", style_tbl_cell), Paragraph("panjang_m", style_tbl_cell), Paragraph("Real / Float", style_tbl_cell), Paragraph("8,2", style_tbl_cell), Paragraph("Panjang linier segmen sungai (m)", style_tbl_cell)],
    [Paragraph("Permukiman", style_tbl_cell), Paragraph("nama_pemuk", style_tbl_cell), Paragraph("String", style_tbl_cell), Paragraph("50", style_tbl_cell), Paragraph("Nama kawasan permukiman / perumahan", style_tbl_cell)],
    [Paragraph("Permukiman", style_tbl_cell), Paragraph("kelurahan", style_tbl_cell), Paragraph("String", style_tbl_cell), Paragraph("50", style_tbl_cell), Paragraph("Kelurahan lokasi persil (Foreign Key)", style_tbl_cell)],
    [Paragraph("Permukiman", style_tbl_cell), Paragraph("kepadatan", style_tbl_cell), Paragraph("String", style_tbl_cell), Paragraph("30", style_tbl_cell), Paragraph("Tingkat kepadatan (Tinggi/Sedang/Rendah)", style_tbl_cell)],
    [Paragraph("Area_Genangan", style_tbl_cell), Paragraph("tipe_banji", style_tbl_cell), Paragraph("String", style_tbl_cell), Paragraph("50", style_tbl_cell), Paragraph("Klasifikasi bahaya (Banjir Rob/Sungai)", style_tbl_cell)],
    [Paragraph("Area_Genangan", style_tbl_cell), Paragraph("kedalaman_", style_tbl_cell), Paragraph("String", style_tbl_cell), Paragraph("30", style_tbl_cell), Paragraph("Rentang kedalaman muka air (cm)", style_tbl_cell)],
    [Paragraph("Titik_Survei", style_tbl_cell), Paragraph("tinggi_air", style_tbl_cell), Paragraph("Real / Float", style_tbl_cell), Paragraph("5,2", style_tbl_cell), Paragraph("Ketinggian genangan terukur GPS (cm)", style_tbl_cell)],
    [Paragraph("Titik_Survei", style_tbl_cell), Paragraph("durasi_jam", style_tbl_cell), Paragraph("Real / Float", style_tbl_cell), Paragraph("4,2", style_tbl_cell), Paragraph("Lama air tergenang hingga surut (jam)", style_tbl_cell)]
]
t_kamus = Table(kamus_table_data, colWidths=[90, 80, 55, 45, 212])
t_kamus.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
]))
story.append(t_kamus)
story.append(PageBreak())

# =========================================================================
# LAMPIRAN 3: DOKUMENTASI TEKNIS VALIDASI (Page 22)
# =========================================================================
story.append(Paragraph("LAMPIRAN 3: DOKUMENTASI TEKNIS GEOREFERENCING, TOPOLOGI, DAN SURVEI", style_bab_title))
story.append(Paragraph(
    "Dokumentasi berikut mencatat rekam jejak pengujian teknis yang menjamin kualitas saintifik data: "
    "<br/><b>1. Ringkasan Uji Georeferencing Peta Dasar:</b> "
    "<br/>• Jumlah Titik Kontrol (GCP): 6 titik terdistribusi merata di persimpangan jalan dan jembatan. "
    "<br/>• Metode Transformasi: Polinomial Orde 1 (Affine) | Resampling: Nearest Neighbor. "
    "<br/>• Hasil Uji RMSE: <b>0,840 meter</b> (Batas toleransi maksimum: 2,50 meter -> <b>Lolos Sangat Baik</b>). "
    "<br/><b>2. Ringkasan Uji Topologi Spasial (QGIS Topology Checker):</b> "
    "<br/>• Layer Garis Sungai (12 Segmen): Bebas dari dangles (overshoot/undershoot) -> <b>0 Kesalahan</b>. "
    "<br/>• Layer Batas Kelurahan (9 Poligon): Bebas dari overlap dan gaps -> <b>0 Kesalahan</b>. "
    "<br/>• Layer Permukiman (15 Klaster): Bebas dari overlap antar persil -> <b>0 Kesalahan</b>. "
    "<br/><b>3. Rekapitulasi Karakteristik 25 Titik GPS Lapangan:</b> "
    "<br/>• Titik Terdampak Rob Pesisir: 10 Titik (Kedalaman: 35 – 65 cm, Durasi: 4 – 7 jam). "
    "<br/>• Titik Terdampak Limpasan Hujan/Sungai: 12 Titik (Kedalaman: 15 – 35 cm, Durasi: 2 – 4 jam). "
    "<br/>• Titik Bebas Genangan / Terkendali Pompa: 3 Titik (Ketinggian genangan: 0 cm).",
    style_body
))
story.append(Spacer(1, 8))

# Detail Table 25 GPS Part 1 & 2
t_full_gps = [
    [Paragraph("ID Titik", style_tbl_head), Paragraph("Kelurahan", style_tbl_head), Paragraph("X UTM (m)", style_tbl_head), Paragraph("Y UTM (m)", style_tbl_head), Paragraph("Elev (m)", style_tbl_head), Paragraph("Air (cm)", style_tbl_head), Paragraph("Dur (Jam)", style_tbl_head), Paragraph("Kondisi Lapangan", style_tbl_head)],
    [Paragraph("SRV-01", style_tbl_cell), Paragraph("Tanjung Mas", style_tbl_cell), Paragraph("436.920", style_tbl_cell), Paragraph("9.231.150", style_tbl_cell), Paragraph("0,25", style_tbl_cell), Paragraph("65", style_tbl_cell), Paragraph("7,0", style_tbl_cell), Paragraph("Dermaga Tambak Lorok", style_tbl_cell)],
    [Paragraph("SRV-02", style_tbl_cell), Paragraph("Tanjung Mas", style_tbl_cell), Paragraph("436.450", style_tbl_cell), Paragraph("9.230.820", style_tbl_cell), Paragraph("0,40", style_tbl_cell), Paragraph("55", style_tbl_cell), Paragraph("6,0", style_tbl_cell), Paragraph("Industri Lamicitra", style_tbl_cell)],
    [Paragraph("SRV-03", style_tbl_cell), Paragraph("Bandarharjo", style_tbl_cell), Paragraph("435.850", style_tbl_cell), Paragraph("9.230.250", style_tbl_cell), Paragraph("0,55", style_tbl_cell), Paragraph("45", style_tbl_cell), Paragraph("5,5", style_tbl_cell), Paragraph("Tanggul Kali Baru", style_tbl_cell)],
    [Paragraph("SRV-04", style_tbl_cell), Paragraph("Bandarharjo", style_tbl_cell), Paragraph("435.520", style_tbl_cell), Paragraph("9.230.100", style_tbl_cell), Paragraph("0,65", style_tbl_cell), Paragraph("35", style_tbl_cell), Paragraph("4,0", style_tbl_cell), Paragraph("Permukiman Padat RW 02", style_tbl_cell)],
    [Paragraph("SRV-05", style_tbl_cell), Paragraph("Panggung Lor", style_tbl_cell), Paragraph("434.120", style_tbl_cell), Paragraph("9.229.850", style_tbl_cell), Paragraph("0,60", style_tbl_cell), Paragraph("40", style_tbl_cell), Paragraph("4,5", style_tbl_cell), Paragraph("Tanah Mas Sektor Utara", style_tbl_cell)],
    [Paragraph("SRV-06", style_tbl_cell), Paragraph("Panggung Lor", style_tbl_cell), Paragraph("434.350", style_tbl_cell), Paragraph("9.229.400", style_tbl_cell), Paragraph("0,80", style_tbl_cell), Paragraph("25", style_tbl_cell), Paragraph("3,0", style_tbl_cell), Paragraph("Jl. Tambak Mas Raya", style_tbl_cell)],
    [Paragraph("SRV-07", style_tbl_cell), Paragraph("Panggung Kidul", style_tbl_cell), Paragraph("434.650", style_tbl_cell), Paragraph("9.228.950", style_tbl_cell), Paragraph("0,95", style_tbl_cell), Paragraph("20", style_tbl_cell), Paragraph("2,5", style_tbl_cell), Paragraph("Jl. Ariloka Permukiman", style_tbl_cell)],
    [Paragraph("SRV-08", style_tbl_cell), Paragraph("Kuningan", style_tbl_cell), Paragraph("435.320", style_tbl_cell), Paragraph("9.229.100", style_tbl_cell), Paragraph("0,75", style_tbl_cell), Paragraph("35", style_tbl_cell), Paragraph("3,5", style_tbl_cell), Paragraph("Permukiman Dekat Saluran", style_tbl_cell)],
    [Paragraph("SRV-09", style_tbl_cell), Paragraph("Kuningan", style_tbl_cell), Paragraph("435.550", style_tbl_cell), Paragraph("9.228.850", style_tbl_cell), Paragraph("0,90", style_tbl_cell), Paragraph("25", style_tbl_cell), Paragraph("2,5", style_tbl_cell), Paragraph("Jl. Hasanudin Rel KA", style_tbl_cell)],
    [Paragraph("SRV-10", style_tbl_cell), Paragraph("Dadapsari", style_tbl_cell), Paragraph("435.750", style_tbl_cell), Paragraph("9.228.650", style_tbl_cell), Paragraph("0,85", style_tbl_cell), Paragraph("30", style_tbl_cell), Paragraph("3,0", style_tbl_cell), Paragraph("Bantaran Kali Semarang", style_tbl_cell)],
    [Paragraph("SRV-11", style_tbl_cell), Paragraph("Bulu Lor", style_tbl_cell), Paragraph("433.950", style_tbl_cell), Paragraph("9.228.450", style_tbl_cell), Paragraph("1,10", style_tbl_cell), Paragraph("20", style_tbl_cell), Paragraph("2,0", style_tbl_cell), Paragraph("Sempadan Saluran Bulu", style_tbl_cell)],
    [Paragraph("SRV-12", style_tbl_cell), Paragraph("Purwosari", style_tbl_cell), Paragraph("435.150", style_tbl_cell), Paragraph("9.228.250", style_tbl_cell), Paragraph("1,20", style_tbl_cell), Paragraph("15", style_tbl_cell), Paragraph("1,5", style_tbl_cell), Paragraph("Kawasan Dekat St. Poncol", style_tbl_cell)],
    [Paragraph("SRV-13", style_tbl_cell), Paragraph("Plombokan", style_tbl_cell), Paragraph("434.500", style_tbl_cell), Paragraph("9.228.150", style_tbl_cell), Paragraph("1,50", style_tbl_cell), Paragraph("0", style_tbl_cell), Paragraph("0,0", style_tbl_cell), Paragraph("Kawasan Aman / Tidak Tergenang", style_tbl_cell)],
    [Paragraph("SRV-25", style_tbl_cell), Paragraph("Tanjung Mas", style_tbl_cell), Paragraph("436.150", style_tbl_cell), Paragraph("9.229.500", style_tbl_cell), Paragraph("0,45", style_tbl_cell), Paragraph("0", style_tbl_cell), Paragraph("0,0", style_tbl_cell), Paragraph("Polder Banger Pintu Air", style_tbl_cell)]
]
t_gps_table = Table(t_full_gps, colWidths=[40, 68, 55, 55, 42, 42, 45, 135])
t_gps_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
    ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_LIGHT]),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
story.append(t_gps_table)
story.append(PageBreak())

# =========================================================================
# LAMPIRAN 4: HASIL KARTOGRAFIS PETA TEMATIK 1 & 2 (Page 23 - 24)
# =========================================================================
story.append(Paragraph("LAMPIRAN 4A: HASIL PETA TEMATIK 1", style_bab_title))
story.append(Paragraph("<b>Peta 1: Persebaran Banjir, Rob, Jaringan Sungai, dan Permukiman di Semarang Utara</b>", style_sub_title))
story.append(Paragraph("Peta menyajikan sebaran faktual fenomena hidrometeorologi banjir rob, jaringan sungai, dan permukiman pada skala 1:25.000 dengan sistem proyeksi WGS 84 / UTM Zone 49S. Dilengkapi inset wilayah Kota Semarang, grid koordinat metrik, skala grafis, dan legenda kartografi standar.", style_body))

peta1_full = f"{BASE_DIR}/06_PETA/Peta_1.jpg"
if os.path.exists(peta1_full):
    story.append(Spacer(1, 4))
    story.append(Image(peta1_full, width=480, height=330))
    story.append(Paragraph("<b>Gambar Lampiran 4.1:</b> Peta Persebaran Banjir, Rob, Sungai, dan Permukiman (Ukuran Cetak Penuh 300 DPI)", ParagraphStyle('P1Cap', fontName='Helvetica', fontSize=7.5, leading=9, alignment=1, textColor=C_DARK)))

story.append(PageBreak())

story.append(Paragraph("LAMPIRAN 4B: HASIL PETA TEMATIK 2", style_bab_title))
story.append(Paragraph("<b>Peta 2: Analisis Keterpaparan Permukiman Terhadap Banjir dan Rob di Semarang Utara</b>", style_sub_title))
story.append(Paragraph("Peta analitis ini menyajikan sintesis hasil pemodelan buffer sungai ganda (100 m & 200 m) dan tumpang susun (overlay intersect) yang mengklasifikasikan permukiman ke dalam zona bahaya Sangat Tinggi (Bencana Ganda), Bahaya Tinggi, dan Bahaya Sedang.", style_body))

peta2_full = f"{BASE_DIR}/06_PETA/Peta_2.jpg"
if os.path.exists(peta2_full):
    story.append(Spacer(1, 4))
    story.append(Image(peta2_full, width=480, height=330))
    story.append(Paragraph("<b>Gambar Lampiran 4.2:</b> Peta Analisis Keterpaparan Permukiman Terhadap Banjir dan Rob (Ukuran Cetak Penuh 300 DPI)", ParagraphStyle('P2Cap', fontName='Helvetica', fontSize=7.5, leading=9, alignment=1, textColor=C_DARK)))

# Build Document
doc.build(story, canvasmaker=NumberedCanvas)
print(f"Laporan_Akhir.pdf generated successfully at: {PDF_PATH}")
