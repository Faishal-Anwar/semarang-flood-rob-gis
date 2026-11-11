import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

print("=== STEP 6: GENERATING PROFESSIONAL PPTX PRESENTATION ===")

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA"
PPT_PATH = f"{BASE_DIR}/09_PRESENTASI/Presentasi_SIG.pptx"

prs = Presentation()
# Set 16:9 widescreen dimensions (13.33 x 7.5 inches)
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette
NAVY = RGBColor(26, 82, 118)      # #1a5276
DARK_BLUE = RGBColor(14, 47, 68)  # #0e2f44
ORANGE = RGBColor(230, 126, 34)   # #e67e22
LIGHT_BG = RGBColor(248, 249, 250)
WHITE = RGBColor(255, 255, 255)
GRAY_TEXT = RGBColor(86, 101, 115)
DARK_TEXT = RGBColor(44, 62, 80)
RED_ACCENT = RGBColor(192, 57, 43)

def create_header(slide, title_text, category_text="TUGAS BESAR SISTEM INFORMASI GEOGRAFIS"):
    # Header banner shape
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.color.rgb = NAVY
    
    # Text in header
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.7), Inches(0.85))
    tf = txBox.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = category_text.upper()
    p1.font.size = Pt(10)
    p1.font.bold = True
    p1.font.color.rgb = ORANGE
    
    p2 = tf.add_paragraph()
    p2.text = title_text
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = WHITE

def add_speaker_note(slide, note_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = note_text

# -------------------------------------------------------------
# SLIDE 1: TITLE SLIDE
# -------------------------------------------------------------
blank_layout = prs.slide_layouts[6]
slide1 = prs.slides.add_slide(blank_layout)

# Background rectangle
bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg.fill.solid()
bg.fill.fore_color.rgb = DARK_BLUE
bg.line.fill.background()

# Title text box
tb1 = slide1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.333), Inches(3.2))
tf1 = tb1.text_frame
tf1.word_wrap = True

p_sub = tf1.paragraphs[0]
p_sub.text = "TUGAS BESAR SISTEM INFORMASI GEOGRAFIS (SIG)"
p_sub.font.size = Pt(14)
p_sub.font.bold = True
p_sub.font.color.rgb = ORANGE

p_main = tf1.add_paragraph()
p_main.text = "PEMETAAN DAN ANALISIS RISIKO BANJIR DAN ROB\nDI KOTA SEMARANG BAGIAN UTARA"
p_main.font.size = Pt(28)
p_main.font.bold = True
p_main.font.color.rgb = WHITE

p_extra = tf1.add_paragraph()
p_extra.text = "Pendekatan Geospasial Berbasis Buffer Sempadan Sungai, Overlay Genangan, dan Survei 25 Titik GPS"
p_extra.font.size = Pt(13)
p_extra.font.italic = True
p_extra.font.color.rgb = RGBColor(189, 195, 199)

# Group member card
card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.8), Inches(11.333), Inches(1.8))
card.fill.solid()
card.fill.fore_color.rgb = RGBColor(22, 40, 56)
card.line.color.rgb = NAVY

tb_mem = slide1.shapes.add_textbox(Inches(1.2), Inches(4.9), Inches(10.9), Inches(1.6))
tf_mem = tb_mem.text_frame
p_m_title = tf_mem.paragraphs[0]
p_m_title.text = "DISUSUN OLEH KELOMPOK 3 - KELAS SIG | DOSEN PENGAMPU: GHUFRON, M.KOM"
p_m_title.font.size = Pt(11)
p_m_title.font.bold = True
p_m_title.font.color.rgb = ORANGE

p_m_list = tf_mem.add_paragraph()
p_m_list.text = "1. Faishal Anwar (Project Manager & Analyst)   |   2. Budi Santoso (Field Surveyor GPS)\n3. Dimas Prasetyo (Digitizing & Georef Operator)   |   4. Siti Aisyah (Spatial Database Analyst)\n5. Rina Marlina (Cartographer & Spatial Modeler)"
p_m_list.font.size = Pt(11)
p_m_list.font.color.rgb = WHITE

add_speaker_note(slide1, "Assalamu'alaikum Wr. Wb. Selamat pagi Bapak Dosen dan rekan-rekan. Pada kesempatan hari ini, kami dari Kelompok Tugas Besar SIG akan mempresentasikan hasil proyek pemetaan dan analisis spasial risiko banjir dan rob di Kota Semarang Bagian Utara menggunakan Sistem Informasi Geografis berbasis QGIS dan GeoPackage.")

# -------------------------------------------------------------
# SLIDE 2: LATAR BELAKANG
# -------------------------------------------------------------
slide2 = prs.slides.add_slide(blank_layout)
create_header(slide2, "Latar Belakang & Urgensi Permasalahan Pesisir")

# Box 1
b1 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.2))
b1.fill.solid()
b1.fill.fore_color.rgb = WHITE
b1.line.color.rgb = NAVY
tb = slide2.shapes.add_textbox(Inches(0.9), Inches(1.7), Inches(3.4), Inches(5.0))
tf = tb.text_frame
tf.word_wrap = True
tf.paragraphs[0].text = "1. Fenomena Pesisir Semarang"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(13)
tf.paragraphs[0].font.color.rgb = NAVY
p = tf.add_paragraph()
p.text = "\n• Kota Semarang bagian utara merupakan dataran aluvial pantai berketinggian 0–2 m dpl.\n• Mengalami kombinasi penurunan muka tanah (land subsidence) 5–10 cm/tahun dan kenaikan muka air laut global.\n• Pasang surut air laut harian menimbulkan rob kronis di permukiman."
p.font.size = Pt(11)
p.font.color.rgb = DARK_TEXT

# Box 2
b2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.2))
b2.fill.solid()
b2.fill.fore_color.rgb = WHITE
b2.line.color.rgb = ORANGE
tb = slide2.shapes.add_textbox(Inches(4.9), Inches(1.7), Inches(3.4), Inches(5.0))
tf = tb.text_frame
tf.word_wrap = True
tf.paragraphs[0].text = "2. Ancaman Bencana Ganda"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(13)
tf.paragraphs[0].font.color.rgb = ORANGE
p = tf.add_paragraph()
p.text = "\n• Fluvial Flood: Limpasan debit aliran sungai saat hujan lebat di hulu (Kali Semarang, BKB, Kali Baru).\n• Coastal Flood: Intrusi pasang air laut pasang perbani/purnama.\n• Compound Hazard: Kejadian bersamaan hujan lebat dan pasang tinggi menyebabkan backwater dan genangan parah."
p.font.size = Pt(11)
p.font.color.rgb = DARK_TEXT

# Box 3
b3 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.2))
b3.fill.solid()
b3.fill.fore_color.rgb = WHITE
b3.line.color.rgb = RED_ACCENT
tb = slide2.shapes.add_textbox(Inches(8.9), Inches(1.7), Inches(3.5), Inches(5.0))
tf = tb.text_frame
tf.word_wrap = True
tf.paragraphs[0].text = "3. Urgensi Pendekatan SIG"
tf.paragraphs[0].font.bold = True
tf.paragraphs[0].font.size = Pt(13)
tf.paragraphs[0].font.color.rgb = RED_ACCENT
p = tf.add_paragraph()
p.text = "\n• Data tabular saja tidak mampu menggambarkan lokasi riil permukiman yang terpapar.\n• SIG mampu mengintegrasikan data hidrologi sungai, batas genangan, dan permukiman secara spasial.\n• Memberikan jawaban presisi terkait luas terdampak dan kelurahan paling rawan."
p.font.size = Pt(11)
p.font.color.rgb = DARK_TEXT

add_speaker_note(slide2, "Kecamatan Semarang Utara memiliki kerentanan fisik sangat tinggi akibat kombinasi subsidence dan pasang air laut. Pendekatan SIG hadir sebagai solusi berbasis bukti spasial untuk memetakan eksposur permukiman di zona rawan secara obyektif.")

# -------------------------------------------------------------
# SLIDE 3: PERTANYAAN SPASIAL & TUJUAN
# -------------------------------------------------------------
slide3 = prs.slides.add_slide(blank_layout)
create_header(slide3, "Tujuan Proyek & 4 Pertanyaan Spasial Kunci")

t_box = slide3.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))
t_tf = t_box.text_frame
t_tf.word_wrap = True

t_p = t_tf.paragraphs[0]
t_p.text = "PERTANYAAN SPASIAL YANG HARUS DIJAWAB OLEH SISTEM:"
t_p.font.size = Pt(14)
t_p.font.bold = True
t_p.font.color.rgb = NAVY

qs = [
    ("Pertanyaan Spasial 1:", "Berapa luas permukiman yang berada dalam radius kritis 200 meter dari sungai dan saluran utama?"),
    ("Pertanyaan Spasial 2:", "Permukiman mana saja yang berada langsung di dalam zona genangan banjir dan rob pesisir?"),
    ("Pertanyaan Spasial 3:", "Berapa total luasan kawasan permukiman yang berada di zona rawan gabungan (rob dan sempadan sungai)?"),
    ("Pertanyaan Spasial 4:", "Kelurahan mana di Semarang Utara yang memiliki persentase eksposur zona rawan permukiman tertinggi dan memerlukan prioritas penanganan?")
]

for q_title, q_desc in qs:
    p1 = t_tf.add_paragraph()
    p1.text = f"\n{q_title}"
    p1.font.bold = True
    p1.font.size = Pt(12)
    p1.font.color.rgb = ORANGE
    p2 = t_tf.add_paragraph()
    p2.text = f"  ➔  {q_desc}"
    p2.font.size = Pt(12)
    p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide3, "Sesuai ketentuan tugas besar, setiap analisis spasial harus menjawab pertanyaan spesifik yang tidak tertulis langsung di data mentah. Keempat pertanyaan spasial inilah yang menjadi kompas kerja teknis kami.")

# -------------------------------------------------------------
# SLIDE 4: 5 KOMPONEN SIG
# -------------------------------------------------------------
slide4 = prs.slides.add_slide(blank_layout)
create_header(slide4, "Penerapan Lima Komponen SIG dalam Proyek")

comps = [
    ("1. Orang (People)", "Kelompok 5 mahasiswa dengan pembagian peran terstruktur (Manager, Surveyor, Digitizer, DB Analyst, Cartographer) dan civitas akademika.", NAVY),
    ("2. Prosedur (Procedures)", "SOP georeferencing dengan toleransi RMSE < 2.5m, SOP survei GPS HP, digitasi snapping, validasi topologi, dan metode intersect SIG.", DARK_BLUE),
    ("3. Data (Spatial & Attribute)", "Vektor titik survei (25 GPS), garis sungai (12 segmen), poligon kelurahan (9), poligon permukiman (15 klaster), dan zona genangan BPBD.", ORANGE),
    ("4. Perangkat Keras (Hardware)", "Laptop Intel Core i7 / RAM 16GB, Smartphone GPS dengan receiver multi-GNSS terkalibrasi untuk survei lapangan.", GRAY_TEXT),
    ("5. Perangkat Lunak (Software)", "QGIS 3.28 LTR, SQLite/Spatialite, GeoPandas & Python Spatial Stack, SW Maps, MS Excel untuk kamus data dan logbook.", NAVY)
]

for idx, (c_name, c_desc, c_col) in enumerate(comps):
    y_pos = 1.5 + (idx * 1.1)
    card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(y_pos), Inches(11.7), Inches(0.95))
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = c_col
    card.line.width = Pt(1.5)
    
    tb = slide4.shapes.add_textbox(Inches(1.0), Inches(y_pos + 0.05), Inches(11.3), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = c_name
    p1.font.bold = True
    p1.font.size = Pt(12)
    p1.font.color.rgb = c_col
    p2 = tf.add_paragraph()
    p2.text = c_desc
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide4, "Kami menerapkan 5 komponen SIG secara nyata, bukan sebatas teori. Peran manusia, kejelasan prosedur, ketelitian data, dukungan hardware laptop dan GPS, serta software QGIS menjadi satu kesatuan sistem.")

# -------------------------------------------------------------
# SLIDE 5: METODOLOGI SUBSISTEM SIG
# -------------------------------------------------------------
slide5 = prs.slides.add_slide(blank_layout)
create_header(slide5, "Metodologi Alur Subsistem SIG")

stages = [
    ("Tahap 1: Input Data", "• Pengumpulan Peta Dasar\n• Georeferencing (6 GCP)\n• RMSE Evaluasi (0.84 m)\n• Survei Lapangan 25 GPS\n• Digitasi Titik, Garis, Poligon"),
    ("Tahap 2: Manajemen Data", "• Desain GeoPackage GPKG\n• Kamus Data 8 Tabel\n• Relasi Tabel PK-FK\n• Cek Topologi 100% Bersih\n• Metadata Standar ISO 19115"),
    ("Tahap 3: Analisis Spasial", "• Buffer Sungai 100 & 200m\n• Overlay Intersect Permukiman\n• Spatial & Attribute Query\n• Kalkulasi Geometri Ha & %\n• Statistik Per Kelurahan"),
    ("Tahap 4: Keluaran (Output)", "• Peta 1: Persebaran Banjir\n• Peta 2: Eksposur Zona Rawan\n• Layout 300 DPI Kartografis\n• Laporan Akademik Lengkap\n• Proyek QGIS Siap Buka")
]

for idx, (s_title, s_desc) in enumerate(stages):
    x_pos = 0.8 + (idx * 2.95)
    card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_pos), Inches(1.8), Inches(2.75), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = NAVY if idx % 2 == 0 else ORANGE
    card.line.fill.background()
    
    tb = slide5.shapes.add_textbox(Inches(x_pos + 0.1), Inches(1.9), Inches(2.55), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = s_title
    p1.font.bold = True
    p1.font.size = Pt(12)
    p1.font.color.rgb = WHITE
    p2 = tf.add_paragraph()
    p2.text = f"\n{s_desc}"
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = WHITE

add_speaker_note(slide5, "Diagram alur pengerjaan kami mengikuti empat pilar subsistem SIG yang diajarkan pada modul kuliah: Input Data, Manajemen Basis Data, Analisis Spasial, dan Penyajian Keluaran.")

# -------------------------------------------------------------
# SLIDE 6: INPUT DATA - GEOREFERENCING & RMSE
# -------------------------------------------------------------
slide6 = prs.slides.add_slide(blank_layout)
create_header(slide6, "Input Data: Georeferencing Peta & Hasil Uji RMSE")

# Add image plot GCP
gcp_plot_path = f"{BASE_DIR}/11_DOKUMENTASI/Georeferencing/Plot_GCP_Georeferencing.png"
if os.path.exists(gcp_plot_path):
    slide6.shapes.add_picture(gcp_plot_path, Inches(0.8), Inches(1.5), width=Inches(6.8))

tb = slide6.shapes.add_textbox(Inches(7.8), Inches(1.5), Inches(4.8), Inches(5.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "HASIL GEOREFERENCING PETA DASAR:"
p.font.bold = True
p.font.size = Pt(13)
p.font.color.rgb = NAVY

desc = """
• Titik Kontrol (GCP): 6 titik persimpangan jalan, jembatan, dan stasiun yang teridentifikasi jelas.
• Transformasi: Polinomial Orde 1 (Affine).
• Sistem Koordinat: WGS 84 / UTM Zone 49S.

EVALUASI KETELITIAN POSISI (RMSE):
• Residu dx rata-rata : 0.577 meter
• Residu dy rata-rata : 0.575 meter
• Total RMSE : 0.840 meter

Ketentuan tugas: Minimal 4 titik kontrol dengan pelaporan RMSE terpenuhi secara saintifik. Nilai RMSE < 1 meter menunjukkan ketelitian posisi yang sangat tinggi untuk skala 1:25.000.
"""
p2 = tf.add_paragraph()
p2.text = desc
p2.font.size = Pt(11)
p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide6, "Proses georeferencing menggunakan 6 titik kontrol tanah dengan nilai RMSE total 0.84 meter. Ini membuktikan bahwa proses rektifikasi geometrik kami sangat presisi dan memenuhi standar kartografi.")

# -------------------------------------------------------------
# SLIDE 7: SURVEI LAPANGAN 25 TITIK GPS
# -------------------------------------------------------------
slide7 = prs.slides.add_slide(blank_layout)
create_header(slide7, "Input Data: Survei Lapangan 25 Titik GPS")

surv_plot_path = f"{BASE_DIR}/11_DOKUMENTASI/Survei/Plot_Sebaran_Titik_Survei.png"
if os.path.exists(surv_plot_path):
    slide7.shapes.add_picture(surv_plot_path, Inches(0.8), Inches(1.5), width=Inches(6.8))

tb = slide7.shapes.add_textbox(Inches(7.8), Inches(1.5), Inches(4.8), Inches(5.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "KARAKTERISTIK SURVEI LAPANGAN:"
p.font.bold = True
p.font.size = Pt(13)
p.font.color.rgb = NAVY

desc_surv = """
• Instrumen: Smartphone Multi-GNSS + SW Maps
• Periode: 18 - 23 Maret 2026
• Jumlah Titik: 25 Titik GPS (SRV-01 s/d SRV-25)

SEBARAN KONDISI LAPANGAN:
1. Genangan Rob Pasang Laut: 10 Titik
   - Lokasi: Tambak Lorok, Lamicitra, Lodan
   - Ketinggian air: 35 – 65 cm
   - Durasi genangan: 4.0 – 7.0 jam
2. Genangan Banjir Hujan & Saluran: 12 Titik
   - Lokasi: Panggung Lor, Kuningan, Dadapsari
   - Ketinggian air: 15 – 35 cm
3. Titik Bebas Genangan / Aman: 3 Titik
   - Polder Banger, Plombokan, Jembatan Berok
"""
p2 = tf.add_paragraph()
p2.text = desc_surv
p2.font.size = Pt(10.5)
p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide7, "Survei lapangan 25 titik GPS dilakukan merata di seluruh 9 kelurahan Semarang Utara. Data mencatat elevasi, tinggi genangan dari 15 hingga 65 cm, durasi surut, serta foto kondisi saluran drainase.")

# -------------------------------------------------------------
# SLIDE 8: BASIS DATA SIG & RELASI TABEL
# -------------------------------------------------------------
slide8 = prs.slides.add_slide(blank_layout)
create_header(slide8, "Manajemen Data: GeoPackage & Relasi Tabel")

tb = slide8.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "STRUKTUR BASIS DATA RELASIONAL SPASIAL (OGC GEOPACKAGE):"
p.font.bold = True
p.font.size = Pt(13)
p.font.color.rgb = NAVY

txt_db = """
1. Standar Format OGC GeoPackage (.gpkg):
   • Seluruh layer spasial disimpan dalam basis data tunggal 'Database_SIG.gpkg' berbasis SQLite.
   • Setiap layer memiliki minimal 8–15 atribut bermakna (melebihi syarat minimal 5 field per layer).

2. Relasi Tabel yang Dibangun & Teruji:
   • Batas_Administrasi_Kelurahan (PK: nama_kel) ➔ Permukiman (FK: kelurahan) [Kardinalitas 1-to-Many]
   • Batas_Administrasi_Kelurahan (PK: nama_kel) ➔ Titik_Survei_Lapangan (FK: kelurahan) [1-to-Many]
   • Batas_Administrasi_Kelurahan (PK: id_kel) ➔ Tabel_Kelurahan_Profil (FK: id_kel) [1-to-1 Relasi Statistik]
   • Permukiman (PK: id_perm) ➔ Permukiman_Terdampak (FK: id_perm) [1-to-Many]

3. Integritas Data & Validasi Topologi:
   • Pemeriksaan topologi garis: Bebas overshoot & undershoot pada seluruh persimpangan saluran.
   • Pemeriksaan topologi poligon: Bebas gap & overlap ilegal antar batas kelurahan maupun permukiman.
"""
p2 = tf.add_paragraph()
p2.text = txt_db
p2.font.size = Pt(11)
p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide8, "Manajemen basis data menggunakan GeoPackage yang modern dan portable. Kami merancang kamus data lengkap dan membangun 4 relasi foreign key yang berfungsi secara nyata di lingkungan QGIS.")

# -------------------------------------------------------------
# SLIDE 9: ANALISIS SPASIAL 1 - BUFFER SUNGAI
# -------------------------------------------------------------
slide9 = prs.slides.add_slide(blank_layout)
create_header(slide9, "Analisis Spasial 1: Buffer Sempadan Sungai (100m & 200m)")

tb = slide9.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "PARAMETER DAN HASIL ANALISIS BUFFER SUNGAI:"
p.font.bold = True
p.font.size = Pt(13)
p.font.color.rgb = NAVY

txt_buf = """
Tujuan Analisis:
Mengidentifikasi kawasan permukiman yang berada pada sempadan sungai aktif (Banjir Kanal Barat, Kali Semarang, Kali Baru, Kali Asin, Kali Banger) yang rentan terhadap bahaya limpasan fluvial saat curah hujan tinggi.

Parameter Buffer:
1. Radius 0 – 100 Meter (Zona Sempadan Kritis):
   • Luas Zona Penyangga: 341.91 Hektar
   • Tingkat Ancaman: Sangat Kritis terhadap limpasan tanggul dan rembesan air pasang.
2. Radius 100 – 200 Meter (Zona Penyangga Menengah):
   • Luas Zona Penyangga: 314.28 Hektar
   • Tingkat Ancaman: Waspada terhadap genangan air balik (backwater) drainase sekunder.

Temuan Spasial:
Mayoritas permukiman padat di Bandarharjo, Kuningan, dan Dadapsari berada langsung dalam radius 100 meter dari tanggul Kali Semarang dan Kali Baru.
"""
p2 = tf.add_paragraph()
p2.text = txt_buf
p2.font.size = Pt(11.5)
p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide9, "Analisis buffer sungai membagi zona bahaya menjadi dua cincin sempadan: 100 meter dan 200 meter. Total zona penyangga sungai di Semarang Utara mencapai lebih dari 650 hektar.")

# -------------------------------------------------------------
# SLIDE 10: ANALISIS SPASIAL 2 - OVERLAY & STATISTIK
# -------------------------------------------------------------
slide10 = prs.slides.add_slide(blank_layout)
create_header(slide10, "Analisis Spasial 2: Overlay Eksposur Zona Rawan")

tb = slide10.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.5))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "HASIL OVERLAY (INTERSECT) PERMUKIMAN x GENANGAN x BUFFER SUNGAI:"
p.font.bold = True
p.font.size = Pt(13)
p.font.color.rgb = NAVY

txt_ovl = """
Metode:
Operasi geometrik Intersection antara layer Poligon Permukiman (171.68 Ha) dengan Poligon Area Genangan Banjir & Rob (640.54 Ha) serta Buffer Sungai 200 meter.

HASIL KUANTITATIF EKSPOSUR ZONA RAWAN PERMUKIMAN:
• Total Luas Permukiman Semarang Utara: 171.68 Hektar
• Total Permukiman Terpapar Bahaya: 120.31 Hektar (70.1% dari seluruh permukiman)
• Klasifikasi Tingkat Bahaya Permukiman Terpapar:
  1. Bahaya Sangat Tinggi (Bencana Ganda: Rob & Fluvial): 18.18 Ha (Tambak Lorok)
  2. Bahaya Tinggi (Rob Pasang Pesisir): 75.91 Ha (Tanah Mas, Puri Anjasmoro, Lodan, Bandarharjo)
  3. Bahaya Sedang (Limpasan Saluran Drainase): 26.23 Ha (Hasanudin, Brotojoyo, Kampung Melayu)
"""
p2 = tf.add_paragraph()
p2.text = txt_ovl
p2.font.size = Pt(11.5)
p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide10, "Melalui analisis overlay intersect, 70,08% kawasan permukiman di Semarang Utara berada di dalam poligon zona rawan BPBD/InaRISK. Angka ini adalah eksposur statis, bukan kejadian banjir saat ini, dan dihitung dari luas permukiman 171,68 Ha.")

# -------------------------------------------------------------
# SLIDE 11: STATISTIK KETERPAPARAN PER KELURAHAN
# -------------------------------------------------------------
slide11 = prs.slides.add_slide(blank_layout)
create_header(slide11, "Peringkat Eksposur Zona Rawan per Kelurahan")

# Add summary table
table_shape = slide11.shapes.add_table(10, 6, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
tbl = table_shape.table

headers = ["Kelurahan", "Populasi (Jiwa)", "Luas Kelurahan (Ha)", "Luas Permukiman (Ha)", "Luas Zona Rawan (Ha)", "Status Kerentanan"]
widths = [Inches(2.2), Inches(1.8), Inches(1.9), Inches(1.9), Inches(1.9), Inches(2.0)]
for i, w in enumerate(widths):
    tbl.columns[i].width = w

for j, h in enumerate(headers):
    cell = tbl.cell(0, j)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

kel_rows = [
    ("Panggung Kidul", "10.450", "48.44", "19.40", "18.89 (97.4%)", "Sangat Kritis"),
    ("Panggung Lor", "15.600", "247.46", "63.26", "60.58 (95.8%)", "Sangat Kritis"),
    ("Bandarharjo", "23.410", "226.34", "30.48", "21.28 (69.8%)", "Waspada"),
    ("Tanjung Mas", "31.250", "378.80", "34.82", "18.18 (52.2%)", "Waspada"),
    ("Kuningan", "12.900", "85.35", "5.56", "1.40 (25.2%)", "Terkendali"),
    ("Bulu Lor", "14.850", "65.89", "15.57", "0.00 (0.0%)", "Di luar zona rawan"),
    ("Plombokan", "9.800", "54.32", "2.59", "0.00 (0.0%)", "Di luar zona rawan"),
    ("Dadapsari", "11.200", "39.74", "0.00", "0.00 (—)", "Data Belum Tersedia"),
    ("Purwosari", "8.350", "48.33", "0.00", "0.00 (—)", "Data Belum Tersedia")
]

for row_idx, r_data in enumerate(kel_rows, 1):
    for col_idx, val in enumerate(r_data):
        cell = tbl.cell(row_idx, col_idx)
        cell.text = val
        cell.fill.solid()
        if "Sangat Kritis" in val:
            cell.fill.fore_color.rgb = RGBColor(250, 219, 216)
        elif "Kritis" in val:
            cell.fill.fore_color.rgb = RGBColor(254, 237, 222)
        else:
            cell.fill.fore_color.rgb = WHITE
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(9.5)
            p.font.color.rgb = DARK_TEXT
            if col_idx in [1, 2, 3, 4, 5]:
                p.alignment = PP_ALIGN.RIGHT if col_idx < 5 else PP_ALIGN.CENTER

add_speaker_note(slide11, "Tabel ini menjawab Pertanyaan Spasial 4. Tiga rasio eksposur zona rawan tertinggi adalah Panggung Kidul (97,37%), Panggung Lor (95,76%), dan Bandarharjo (69,81%).")

# -------------------------------------------------------------
# SLIDE 12: HASIL PETA TEMATIK 1
# -------------------------------------------------------------
slide12 = prs.slides.add_slide(blank_layout)
create_header(slide12, "Hasil Keluaran: Peta Tematik 1 (Persebaran Banjir & Rob)")

peta1_path = f"{BASE_DIR}/06_PETA/Peta_1.jpg"
if os.path.exists(peta1_path):
    slide12.shapes.add_picture(peta1_path, Inches(0.8), Inches(1.4), width=Inches(7.8))

tb = slide12.shapes.add_textbox(Inches(8.8), Inches(1.4), Inches(3.8), Inches(5.5))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "DESKRIPSI KARTOGRAFIS PETA 1:"
p.font.bold = True
p.font.size = Pt(12)
p.font.color.rgb = NAVY

txt_p1 = """
Judul:
Peta Persebaran Banjir, Rob, Sungai, dan Permukiman Semarang Utara.

Elemen Kartografi Lengkap:
• Skala Grafis & Angka (1:25.000)
• Inset Peta Kota Semarang
• Sistem Grid UTM Zona 49S
• Legenda Tematik Komprehensif
• Sumber Resmi & Tim Penyusun

Informasi Spasial:
Menyajikan sebaran faktual genangan rob pesisir di Tanjung Mas dan muara Kali Baru, saluran drainase, serta 25 titik survei GPS lapangan.
"""
p2 = tf.add_paragraph()
p2.text = txt_p1
p2.font.size = Pt(10)
p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide12, "Peta Tematik 1 memenuhi seluruh standar kartografi: judul, arah utara, skala angka dan grafis, inset Kota Semarang, legenda lengkap, serta koordinat grid UTM dengan resolusi ekspor 300 DPI.")

# -------------------------------------------------------------
# SLIDE 13: HASIL PETA TEMATIK 2
# -------------------------------------------------------------
slide13 = prs.slides.add_slide(blank_layout)
create_header(slide13, "Hasil Keluaran: Peta Tematik 2 (Eksposur Zona Rawan)")

peta2_path = f"{BASE_DIR}/06_PETA/Peta_2.jpg"
if os.path.exists(peta2_path):
    slide13.shapes.add_picture(peta2_path, Inches(0.8), Inches(1.4), width=Inches(7.8))

tb = slide13.shapes.add_textbox(Inches(8.8), Inches(1.4), Inches(3.8), Inches(5.5))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "DESKRIPSI KARTOGRAFIS PETA 2:"
p.font.bold = True
p.font.size = Pt(12)
p.font.color.rgb = NAVY

txt_p2 = """
Judul:
Peta Analisis Keterpaparan Permukiman Terhadap Banjir dan Rob Semarang Utara.

Nilai Tambah Analisis:
• Layer Buffer Sungai (100m & 200m)
• Zonasi Bahaya Genangan
• Permukiman di Zona Rawan Terklasifikasi:
  - Sangat Tinggi (Merah Pekat)
  - Tinggi (Oranye)
  - Sedang (Kuning)
• Callout lokasi paling kritis: Tambak Lorok dan Lamicitra (> 50 cm rob).
"""
p2 = tf.add_paragraph()
p2.text = txt_p2
p2.font.size = Pt(10)
p2.font.color.rgb = DARK_TEXT

add_speaker_note(slide13, "Peta Tematik 2 menyajikan sintesis analitis yang menjawab seluruh pertanyaan spasial secara visual, menonjolkan zona rawan bertingkat untuk membantu perencanaan tata ruang dan mitigasi.")

# -------------------------------------------------------------
# SLIDE 14: KESIMPULAN & REKOMENDASI SPASIAL
# -------------------------------------------------------------
slide14 = prs.slides.add_slide(blank_layout)
create_header(slide14, "Kesimpulan Proyek & Rekomendasi Spasial")

tb1 = slide14.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.5))
tf1 = tb1.text_frame
tf1.word_wrap = True
p1 = tf1.paragraphs[0]
p1.text = "KESIMPULAN UTAMA PENELITIAN:"
p1.font.bold = True
p1.font.size = Pt(13)
p1.font.color.rgb = NAVY
p1_desc = """
1. Eksposur Zona Rawan: Dari total 171,68 Ha kawasan permukiman di Semarang Utara, seluas 120,31 Ha (70,08%) berada di zona rawan BPBD/InaRISK — eksposur statis, bukan kejadian saat ini.
2. Wilayah Prioritas 1: Panggung Kidul (97,37%; 18,89 Ha) dan Panggung Lor (95,76%; 60,58 Ha). Bandarharjo dan Tanjung Mas menjadi prioritas berikutnya.
3. Kualitas SIG: Seluruh tahapan dari Georeferencing (RMSE 0.84m), Survei 25 GPS, Basis Data GeoPackage, Analisis Spasial, hingga Peta 300 DPI berhasil diimplementasikan 100%.
"""
p1_sub = tf1.add_paragraph()
p1_sub.text = p1_desc
p1_sub.font.size = Pt(11)
p1_sub.font.color.rgb = DARK_TEXT

tb2 = slide14.shapes.add_textbox(Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.5))
tf2 = tb2.text_frame
tf2.word_wrap = True
p2 = tf2.paragraphs[0]
p2.text = "REKOMENDASI KEBIJAKAN SPASIAL:"
p2.font.bold = True
p2.font.size = Pt(13)
p2.font.color.rgb = ORANGE
p2_desc = """
1. Pengendalian Struktural Terpadu:
   • Percepatan pembangunan tanggul laut sabuk pantai (coastal embankment) Tambak Lorok.
   • Penguatan parapet beton Kali Semarang dan normalisasi pengerukan sedimen lumpur Kali Baru.
2. Optimalisasi Sistem Polder:
   • Peningkatan kapasitas debit rumah pompa di Polder Banger, Kali Baru, dan Tanah Mas dengan backup genset otomatis.
3. Kebijakan Non-Struktural & Adaptasi:
   • Moratorium izin hunian baru di sempadan 100m sungai.
   • Program adaptasi rumah panggung komunal nelayan.
"""
p2_sub = tf2.add_paragraph()
p2_sub.text = p2_desc
p2_sub.font.size = Pt(11)
p2_sub.font.color.rgb = DARK_TEXT

add_speaker_note(slide14, "Kesimpulan kami menegaskan pentingnya prioritas penanganan di Tanjung Mas dan Bandarharjo. Rekomendasi menggabungkan pendekatan struktural polder dan tanggul dengan kebijakan tata ruang zonasi sempadan.")

# -------------------------------------------------------------
# SLIDE 15: INTEGRASI NILAI ISLAM & PENUTUP
# -------------------------------------------------------------
slide15 = prs.slides.add_slide(blank_layout)

bg15 = slide15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg15.fill.solid()
bg15.fill.fore_color.rgb = DARK_BLUE
bg15.line.fill.background()

tb_end = slide15.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(10.9), Inches(5.2))
tf_end = tb_end.text_frame
tf_end.word_wrap = True

p_i1 = tf_end.paragraphs[0]
p_i1.text = "INTEGRASI NILAI ISLAM DALAM PENGELOLAAN SPASIAL"
p_i1.font.bold = True
p_i1.font.size = Pt(15)
p_i1.font.color.rgb = ORANGE

islam_text = """
"Dan janganlah kamu berbuat kerusakan di bumi setelah (diciptakan) dengan baik..." (QS. Al-A'raf: 56)

Pengelolaan data spasial dalam proyek ini merupakan manifestasi dari nilai amanah (kejujuran ilmiah dan ketepatan data tanpa rekayasa). Pemanfaatan SIG untuk memetakan risiko bencana banjir dan rob bertujuan mewujudkan kemaslahatan publik (hifz an-nafs dan hifz al-mal), yaitu melindungi keselamatan jiwa warga dan aset kehidupan masyarakat pesisir Semarang Utara dari ancaman kepunahan akibat kerusakan lingkungan.
"""
p_i2 = tf_end.add_paragraph()
p_i2.text = islam_text
p_i2.font.size = Pt(12)
p_i2.font.italic = True
p_i2.font.color.rgb = WHITE

p_tq = tf_end.add_paragraph()
p_tq.text = "\nTERIMA KASIH ATAS PERHATIANNYA\nWassalamu'alaikum Warahmatullahi Wabarakatuh"
p_tq.font.bold = True
p_tq.font.size = Pt(16)
p_tq.font.color.rgb = ORANGE

add_speaker_note(slide15, "Sebagai penutup, seluruh ikhtiar pemetaan ini kami sandarkan pada nilai-nilai keislaman sebagai bentuk amanah keilmuan dan kepedulian terhadap kemaslahatan masyarakat pesisir. Kami persilakan Bapak Dosen dan rekan-rekan bila ada pertanyaan atau masukan. Terima kasih.")

# Save presentation
prs.save(PPT_PATH)
print("Presentasi_SIG.pptx created successfully (15 slides with full notes)!")
