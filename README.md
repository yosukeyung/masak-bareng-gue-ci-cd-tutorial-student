# Workshop CI/CD — Masak Bareng Gue

**Tools:** GitHub, GitHub Actions, Render.com  
**Project:** Web app resep masakan Indonesia

---

## Apa yang Akan Kamu Bangun

Di akhir workshop ini, kamu akan punya **pipeline CI/CD** yang bekerja seperti ini:

```
Kamu push code ke GitHub
        ↓
GitHub Actions otomatis jalankan test (24 test cases)
        ↓
Cek code quality dengan flake8
        ↓
Kalau semua hijau → app otomatis deploy ke internet
        ↓
Buka URL → Masak Apa Nih? live dan bisa diakses siapapun
```

Semua terjadi otomatis. Kamu tidak perlu deploy manual sama sekali.

---

## Sebelum Mulai

Pastikan kamu sudah punya:

- [ ] Akun GitHub
- [ ] Git terinstall di laptop
- [ ] Python 3.10+ terinstall
- [ ] Akun Render.com (daftar gratis di render.com)

---

## Bagian 1 — Setup

### 1.1 Fork & Clone Repo

**Fork** berarti kamu membuat salinan repo ini ke akun GitHub kamu sendiri. Penting: kamu harus fork, bukan clone langsung dari repo instruktur, karena GitHub Actions berjalan di repo masing-masing.

1. Buka repo template di GitHub ([https://github.com/alfhisa/masak-bareng-gue-ci-cd-tutorial.git](https://github.com/alfhisa/masak-bareng-gue-ci-cd-tutorial.git))
2. Klik tombol **Fork** di pojok kanan atas
3. Pilih akun GitHub kamu sebagai destination
4. Klik **Create fork**

Sekarang kamu punya repo sendiri di `github.com/USERNAME/masak-bareng-gue-ci-cd-tutorial`.

Clone ke laptop:

```bash
git clone https://github.com/USERNAME/masak-bareng-gue-ci-cd-tutorial.git
cd masak-bareng-gue-ci-cd-tutorial
```

### 1.2 Setup Virtual Environment

```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan (Mac/Linux)
source venv/bin/activate

# Aktifkan (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> **Tanda berhasil:** Terminal kamu ada prefix `(venv)` di depannya.

### 1.3 Jalankan Aplikasi

```bash
uvicorn app.main:app --reload
```

Buka browser ke **http://localhost:8000** — kamu akan lihat halaman Masak Apa Nih?.

Coba:
- Ketik "ayam" di search bar
- Klik salah satu resep
- Klik tombol "Acak Resep"

### 1.4 Jalankan Test

Sebelum membuat pipeline, pastikan semua test sudah hijau di lokal:

```bash
pytest tests/ -v
```

Kamu seharusnya lihat output seperti ini:

```
tests/test_api.py::TestHomepage::test_returns_200 PASSED
tests/test_api.py::TestHomepage::test_contains_recipe_content PASSED
tests/test_api.py::TestSearch::test_search_ayam PASSED
...
24 passed in 2.34s
```

> Kalau ada yang FAILED, berhenti dulu dan tanya instruktur sebelum lanjut.

### 1.5 Lihat Struktur Folder

```
masak-apa-nih/
├── app/
│   ├── main.py          ← FastAPI routes
│   ├── data.py          ← Load & search data
│   └── templates/       ← HTML templates
├── static/
│   └── style.css
├── tests/
│   └── test_api.py      ← 24 test cases yang akan dijalankan CI
├── data/
│   └── recipes.json     ← 3.000 resep masakan Indonesia
├── .github/
│   └── workflows/       ← KOSONG — ini yang akan kita isi
└── requirements.txt
```

Perhatikan folder `.github/workflows/` yang **masih kosong**. Itu adalah tempat kita mendefinisikan pipeline CI/CD. GitHub Actions akan otomatis mendeteksi file apapun di folder itu.

---

## Bagian 2 — CI Pipeline

### Apa itu GitHub Actions?

GitHub Actions adalah sistem CI/CD yang sudah built-in di GitHub. Kamu mendefinisikan pipeline dalam file YAML, dan GitHub akan menjalankannya di server mereka setiap kali ada event tertentu (push, pull request, dll).

Satu file YAML = satu **workflow**.  
Satu workflow terdiri dari satu atau lebih **jobs**.  
Satu job terdiri dari beberapa **steps**.

### 2.1 Buat File Workflow Pertama

Buat file baru:

```bash
mkdir -p .github/workflows
touch .github/workflows/ci.yml
```

Buka file itu di code editor kamu, dan mulai isi dari atas:

### 2.2 Definisikan Trigger

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
```

**Penjelasan:**
- `name` — nama pipeline yang muncul di tab Actions GitHub
- `on` — kapan pipeline ini dijalankan
- `push: branches: [main, develop]` — setiap kali ada push ke branch `main` atau `develop`
- `pull_request: branches: [main]` — setiap kali ada PR yang targetnya `main`

### 2.3 Definisikan Job

Tambahkan di bawah bagian `on`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
```

**Penjelasan:**
- `jobs` — daftar semua job dalam workflow ini
- `test` — nama job (bebas, tapi harus deskriptif)
- `runs-on: ubuntu-latest` — job ini dijalankan di virtual machine Ubuntu terbaru milik GitHub

> **Catatan:** GitHub menyediakan runner Ubuntu, Windows, dan macOS. Untuk web app Python, Ubuntu paling umum dipakai.

### 2.4 Tambahkan Steps

Masih di dalam job `test`, tambahkan steps:

```yaml
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ -v
```

**Penjelasan setiap step:**

| Step | Penjelasan |
|------|-----------|
| `actions/checkout@v4` | Download kode repo ke runner. Tanpa ini, runner tidak punya kode kamu. |
| `actions/setup-python@v5` | Install Python versi yang ditentukan di runner. |
| `pip install -r requirements.txt` | Install semua library yang dibutuhkan app. |
| `pytest tests/ -v` | Jalankan semua test. Pipeline gagal kalau ada test yang FAILED. |

### 2.5 File Lengkap Sejauh Ini

File `ci.yml` kamu sekarang seharusnya terlihat seperti ini:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ -v
```

### 2.6 Push dan Lihat Pipeline Jalan

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add initial CI workflow"
git push origin main
```

Sekarang buka repo kamu di GitHub → klik tab **Actions**.

Kamu akan lihat workflow sedang berjalan. Klik untuk melihat detail — setiap step akan muncul satu per satu secara real-time.

> **Yang diharapkan:** Semua steps hijau ✓ dan kamu lihat "24 passed" di step Run tests.

### 2.7 Coba Buat Pipeline Merah (Sengaja)

Ini bagian penting — kita perlu merasakan bahwa pipeline benar-benar menjaga kode kita.

Buka `tests/test_api.py`, cari test ini dan ubah assertion-nya jadi salah:

```python
# Ubah ini:
def test_total_is_3000(self):
    stats = client.get("/api/stats").json()
    assert stats["total"] == 3000

# Jadi ini (angka salah sengaja):
def test_total_is_3000(self):
    stats = client.get("/api/stats").json()
    assert stats["total"] == 9999
```

Push perubahannya:

```bash
git add tests/test_api.py
git commit -m "test: sengaja break test untuk demo"
git push origin main
```

Buka tab Actions — pipeline sekarang **merah ✗**.

Sekarang kembalikan ke kondisi semula dan push lagi — pipeline kembali **hijau ✓**.

> **Pelajaran:** Pipeline CI adalah safety net. Kalau ada kode yang break, tim langsung tahu sebelum masuk ke production.

---

## Bagian 3 — Quality Gates

Pipeline yang hanya menjalankan test belum cukup. Di industri, pipeline juga menjaga **kualitas kode** — bukan hanya "apakah kode bekerja" tapi juga "apakah kode ditulis dengan baik."

Kita akan tambah dua quality gate:
1. **Linting** — cek format dan gaya penulisan kode
2. **Coverage threshold** — pipeline gagal kalau test coverage di bawah 80%

### 3.1 Tambah Dependencies Baru

Buka `requirements.txt` dan tambahkan dua library:

```
flake8==7.1.1
pytest-cov==5.0.0
```

### 3.2 Update Step di ci.yml

Ganti step `Run tests` dengan tiga step baru:

```yaml
      - name: Lint dengan flake8
        run: flake8 app/ tests/ --max-line-length=100

      - name: Test + coverage report
        run: pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
```

**Penjelasan:**
- `flake8 app/ tests/` — cek semua file Python di folder `app/` dan `tests/`
- `--max-line-length=100` — toleransi panjang baris 100 karakter (default 79, agak ketat)
- `--cov=app` — ukur coverage untuk kode di folder `app/`
- `--cov-report=term-missing` — tampilkan baris mana yang belum di-test
- `--cov-fail-under=80` — pipeline **gagal** kalau coverage di bawah 80%

### 3.3 File ci.yml yang Sudah Diupdate

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Lint dengan flake8
        run: flake8 app/ tests/ --max-line-length=100

      - name: Test + coverage report
        run: pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
```

### 3.4 Push dan Cek Coverage Report

```bash
git add requirements.txt .github/workflows/ci.yml
git commit -m "ci: add linting and coverage threshold"
git push origin main
```

Buka tab Actions → klik workflow terbaru → klik step "Test + coverage report". Kamu akan lihat tabel coverage seperti ini:

```
Name                Stmts   Miss  Cover
---------------------------------------
app/data.py            28      2    93%
app/main.py            32      0   100%
---------------------------------------
TOTAL                  60      2    97%
```

### 3.5 Demo: Buat Linting Fail

Buka `app/data.py`, tambahkan spasi di akhir salah satu baris (trailing whitespace):

```python
def get_stats() -> dict:   
    return {
```

Push → pipeline merah di step Lint. Hapus spasi itu → push lagi → hijau.

> **Pelajaran:** Quality gates memastikan seluruh tim menulis kode dengan standar yang sama. Tidak ada lagi "di laptopku jalan" tapi formatnya berantakan.

---

## Bagian 4 — CD: Deploy ke Render.com

Sekarang pipeline kita bisa test dan cek quality. Langkah terakhir: **otomatisasi deploy**.

Setiap kali push ke `main` dan semua test hijau → app otomatis live di internet.

### 4.1 Setup Render.com

1. Buka **render.com** dan login
2. Klik **New** → **Web Service**
3. Klik **Connect a repository** → pilih repo `masak-bareng-gue-ci-cd-tutorial` kamu
4. Isi konfigurasi:

| Field | Value |
|-------|-------|
| Name | `masak-bareng-gue-ci-cd-tutorial` (atau nama lain) |
| Region | Singapore (paling dekat) |
| Branch | `main` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | **Free** |

5. Klik **Deploy Web Service**

Tunggu beberapa menit sampai deployment pertama selesai. Kamu akan dapat URL seperti `https://masak-bareng-gue-ci-cd-tutorial-xxxx.onrender.com`.

> **Catatan:** Deploy pertama dilakukan manual. Setelah ini, semua deploy berikutnya akan otomatis lewat pipeline kita.

### 4.2 Dapatkan Deploy Hook URL

Kita akan trigger deploy dari GitHub Actions menggunakan **Deploy Hook** — sebuah URL khusus yang kalau di-hit, Render akan langsung deploy ulang app kita.

1. Di dashboard Render, masuk ke service kamu
2. Klik **Settings** → scroll ke bagian **Deploy Hook**
3. Klik **Generate Deploy Hook**
4. **Copy URL-nya** — bentuknya seperti `https://api.render.com/deploy/srv-xxxxx?key=yyyyy`

> **PENTING:** Jangan share URL ini ke siapapun. URL ini bisa dipakai siapapun untuk trigger deploy app kamu.

### 4.3 Simpan sebagai GitHub Secret

URL deploy hook tidak boleh ada di kode (bisa dilihat publik). Kita simpan sebagai **Secret** di GitHub.

1. Buka repo kamu di GitHub
2. Klik **Settings** → **Secrets and variables** → **Actions**
3. Klik **New repository secret**
4. Isi:
   - **Name:** `RENDER_DEPLOY_HOOK`
   - **Secret:** paste URL deploy hook dari Render
5. Klik **Add secret**

Sekarang pipeline kita bisa menggunakan secret ini tanpa mengeksposnya ke publik.

### 4.4 Tambah Job Deploy ke ci.yml

Tambahkan job baru di bawah job `test`:

```yaml
  deploy:
    name: Deploy ke Render
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Trigger Render deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

**Penjelasan konfigurasi penting:**

| Konfigurasi | Artinya |
|-------------|---------|
| `needs: test` | Job `deploy` hanya jalan kalau job `test` **berhasil**. Kalau test gagal, deploy tidak terjadi. |
| `if: github.ref == 'refs/heads/main'` | Deploy hanya terjadi kalau push ke branch `main`. PR atau push ke branch lain tidak akan deploy. |
| `curl -X POST` | Kirim HTTP request ke Render deploy hook untuk trigger deployment. |

### 4.5 File ci.yml Final

Ini adalah file lengkap yang sudah jadi:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Test & Quality Check
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Lint dengan flake8
        run: flake8 app/ tests/ --max-line-length=100

      - name: Test + coverage report
        run: pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80

  deploy:
    name: Deploy ke Render
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Trigger Render deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

### 4.6 Push dan Lihat Sihirnya

```bash
git add .
git commit -m "ci: add CD job - auto deploy to Render on main"
git push origin main
```

Buka tab **Actions** di GitHub. Kamu akan lihat:

```
CI/CD Pipeline
├── Test & Quality Check    ✓ (2 menit)
└── Deploy ke Render        ✓ (30 detik)
```

Setelah pipeline hijau semua, buka URL Render kamu. Tunggu 1-2 menit untuk Render selesai deploy, lalu refresh.

**🎉 App kamu sekarang live di internet.**

Coba search "rendang" — hasilnya muncul dari server yang jalan di internet, bukan laptop kamu.

### 4.7 Demo Alur Lengkap

Untuk membuktikan bahwa ini benar-benar otomatis, coba:

1. Ubah sesuatu yang kecil di app — misalnya ganti teks di `app/templates/index.html`
2. Commit dan push ke `main`
3. Lihat pipeline jalan di tab Actions
4. Setelah hijau, refresh URL Render — perubahan sudah live

Dari push sampai live: **kurang lebih 3 menit**, tanpa satu pun langkah manual.

---

## Bagian 5 — Branch Protection

Pipeline sudah jalan. Tapi sekarang siapapun masih bisa merge PR ke `main` bahkan kalau pipeline-nya merah. Kita akan fix itu.

### 5.1 Setup Branch Protection Rule

1. Buka repo di GitHub → **Settings** → **Branches**
2. Klik **Add branch protection rule**
3. Di **Branch name pattern**, ketik `main`
4. Centang **Require status checks to pass before merging**
5. Di search box yang muncul, ketik `Test` → pilih `Test & Quality Check`
6. Centang **Require branches to be up to date before merging**
7. Klik **Create**

Sekarang branch `main` **terlindungi**:
- Tidak bisa push langsung ke `main` (harus lewat PR)
- PR tidak bisa di-merge kalau pipeline merah

Ini adalah standar yang dipakai di hampir semua perusahaan teknologi.

---

## Recap: Apa yang Sudah Kamu Buat

```
.github/workflows/ci.yml
│
├── Trigger: setiap push ke main/develop atau PR ke main
│
├── Job: test
│   ├── Checkout code
│   ├── Setup Python 3.11
│   ├── Install dependencies
│   ├── Lint dengan flake8 (quality gate)
│   └── Run 24 tests + cek coverage ≥ 80% (quality gate)
│
└── Job: deploy (hanya kalau test hijau DAN branch main)
    └── Trigger Render deploy hook → app live otomatis
```

**Dalam 90 menit, kamu sudah:**
- Membuat pipeline CI/CD yang berjalan otomatis
- Menjaga kualitas kode dengan linting dan coverage
- Mendeploy web app ke internet secara otomatis
- Melindungi branch `main` dari kode yang belum teruji

---

## Eksplorasi Lanjutan

Kalau masih ada waktu, coba salah satu tantangan ini:

### Tantangan 1 — Cache Dependencies
Pipeline kita install dependencies dari nol setiap kali. Ini lambat. Tambahkan caching:

```yaml
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: pip install -r requirements.txt
```

Bandingkan waktu eksekusi sebelum dan sesudah.

### Tantangan 2 — Notifikasi Pipeline
Tambahkan step yang print pesan kalau pipeline berhasil:

```yaml
      - name: Notifikasi sukses
        run: echo "✅ Deploy berhasil! App live di Render."
```

### Tantangan 3 — Tambah Endpoint Baru
Buat endpoint `/api/easy` yang return resep dengan `num_ingredients <= 5`.  
Tulis test-nya dulu, baru implementasinya.  
Push → lihat pipeline otomatis test endpoint baru kamu.

---

## Troubleshooting

**Pipeline tidak muncul di tab Actions?**  
Pastikan file ada di path yang benar: `.github/workflows/ci.yml` (bukan `github/` tanpa dot).

**Step "Lint" gagal dengan error `E501`?**  
Ada baris yang terlalu panjang (lebih dari 100 karakter). Cek baris yang disebutkan di error message.

**Step "Test + coverage" gagal dengan "Coverage failure: total of XX is less than 80%"?**  
Coverage kamu di bawah 80%. Tambahkan test untuk fungsi/endpoint yang belum di-cover.

**Deploy hook tidak bekerja (curl error)?**  
Pastikan nama secret di GitHub **persis** `RENDER_DEPLOY_HOOK` dan URL-nya sudah benar.

**App di Render tidak update setelah pipeline hijau?**  
Render free tier kadang butuh 1-3 menit. Kalau lebih dari 5 menit, cek dashboard Render apakah ada error di log deploy.

**App Render loading sangat lama (30+ detik)?**  
Normal untuk free tier — service "tidur" kalau tidak ada traffic dan butuh waktu untuk "bangun" lagi.

---

## Referensi

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Render.com Documentation](https://render.com/docs)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io)
- [flake8 Documentation](https://flake8.pycqa.org)