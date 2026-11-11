# Deploy Publik (Render — paling mudah)

Repo: <https://github.com/Faishal-Anwar/semarang-flood-rob-gis>

Project ini terdiri dari dua bagian:

- **WebGIS statis** di `PROJECT_SIG_SEMARANG_UTARA/webgis/`
- **API FastAPI** di `PROJECT_SIG_SEMARANG_UTARA/backend/`

FastAPI sudah menyajikan folder `webgis` dari root yang sama, jadi cukup **satu Web Service** untuk mendapatkan website + API + monitoring.

## Opsi 1 — Render Blueprint (paling cepat)

1. Buka <https://dashboard.render.com/blueprints>
2. Klik **New Blueprint Instance**
3. Pilih repo `Faishal-Anwar/semarang-flood-rob-gis`
4. Render akan membaca `render.yaml`
5. Klik **Apply** / **Deploy**
6. Tunggu build selesai, lalu buka URL `https://<nama-service>.onrender.com`

`render.yaml` sudah mengatur:
- root project: `PROJECT_SIG_SEMARANG_UTARA`
- build: `pip install -r backend/requirements.txt`
- start: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
- health check: `/api/health`
- Python 3.11.9
- rate limit 30 POST/menit

## Opsi 2 — Render Web Service manual

Jika Blueprint tidak tersedia:

1. Render Dashboard → **New +** → **Web Service**
2. Connect repo GitHub
3. Isi:
   - **Name:** `semarang-flood-rob-gis`
   - **Language:** Python 3
   - **Root Directory:** `PROJECT_SIG_SEMARANG_UTARA`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Deploy.

## Setelah deploy

Buka:

- Website: `https://<nama-service>.onrender.com/`
- Peta: `https://<nama-service>.onrender.com/map.html`
- Dashboard: `https://<nama-service>.onrender.com/dashboard.html`
- API status: `https://<nama-service>.onrender.com/api/monitoring/status`
- Form observasi: `https://<nama-service>.onrender.com/observasi.html`

## Catatan penting

- Render Free akan **tidur setelah tidak diakses**. Kunjungan pertama bisa lambat 30–60 detik; setelah itu normal.
- `monitoring.db` di Render Free bersifat **ephemeral**: observasi lapangan bisa hilang saat redeploy/restart. Data tematik, laporan, dan WebGIS tetap aman karena berasal dari file repo.
- Jika butuh data observasi permanen, tambahkan **Render Disk** (berbayar) atau ganti SQLite ke PostgreSQL.
- Kalau memakai domain sendiri, set environment variable `ALLOWED_ORIGINS` ke domain tersebut.
- Untuk membatasi siapa yang boleh POST observasi, set `MONITORING_API_KEY`; form observasi punya field kunci API.
- Jangan mengaktifkan GitHub Pages untuk project ini kalau ingin monitoring live: Pages hanya menyajikan file statis dan tidak menjalankan FastAPI. Di Pages, panel monitoring akan menjadi **SIMULASI LOKAL**.

## Alternatif kalau hanya butuh tampilan statis

Jika yang dipublikasikan hanya portofolio/tampilan peta tanpa API:

- Upload folder `PROJECT_SIG_SEMARANG_UTARA/webgis/` ke hosting statis (Netlify, Vercel, Cloudflare Pages, GitHub Pages).
- Website tetap terbuka, tetapi monitoring hanya simulasi lokal dan layer laporan PetaBencana tidak aktif.

Untuk project ini, **Render full-stack adalah pilihan yang paling cepat dan lengkap**.
