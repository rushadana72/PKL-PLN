# SOSMATE — SOSYS Automated Material Entry

<p align="center">
  <img src="assets/sosmate-logo.png" alt="SOSMATE Logo" width="120"/>
</p>

<p align="center">
  <strong>Otomasi Konversi Material RAB Vendor ke Template PK SOSYS</strong><br/>
  Dikembangkan untuk PT PLN (Persero) UP3 Malang
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/License-Internal-lightgrey" />
</p>

---

## Tentang Aplikasi

**SOSMATE** adalah aplikasi web berbasis Streamlit yang mengotomasi proses entri material dari file RAB (Rencana Anggaran Biaya) Vendor ke dalam template PK SOSYS PLN. Aplikasi ini menggunakan sistem pencocokan cerdas berbasis *fuzzy matching* untuk mencocokkan nama material vendor dengan database master material secara otomatis.

---

## Fitur Utama

- **Upload & Parsing Otomatis** — Mendukung file master material (`.xlsx`, `.csv`) dan file RAB vendor (`.xlsx`, `.xls`)
- **Multi-Sheet Support** — Deteksi otomatis sheet yang tersedia pada file Excel vendor
- **Konfigurasi Kolom Fleksibel** — Pemetaan kolom yang dapat disesuaikan (A–AZ)
- **Fuzzy Matching Cerdas** — Pencocokan nama material dengan toleransi variasi penulisan (threshold 80%)
- **Edit Interaktif** — Tabel hasil dapat diedit langsung di browser; perubahan nama material akan otomatis memperbarui kode & tipe material dari master
- **Ekspor Multi-Format** — Unduh hasil dalam format Excel (`.xlsx`) maupun CSV

---

## Struktur Proyek

```
sosmate/
├── app.py                  # Entry point aplikasi Streamlit
├── config.py               # Konfigurasi global & konstanta
├── processor.py            # Logika pemrosesan & fuzzy matching
├── data_handlers.py        # Handler file master & vendor
├── ui_components.py        # Komponen UI yang dapat digunakan ulang
├── styles.py               # Custom CSS & styling
├── requirements.txt        # Dependensi Python
├── .streamlit/
│   └── config.toml         # Konfigurasi tema Streamlit
└── assets/
    ├── sosmate-logo.png
    └── favicon-logo.png
```

---

## Cara Penggunaan

### 1. Prasyarat

- Python 3.9 atau lebih baru
- pip

### 2. Instalasi

```bash
# Clone repository
git clone https://github.com/username/sosmate.git
cd sosmate

# Install dependensi
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`.

---

## Alur Penggunaan

```
[1] Upload Master Material  →  [2] Upload RAB Vendor  →  [3] Konfigurasi Kolom  →  [4] Proses & Unduh
```

| Langkah | Deskripsi |
|---------|-----------|
| **Step 1** | Unggah file database master material (Excel/CSV) dengan kolom: `Nama`, `Kode`, `Tipe` |
| **Step 2** | Unggah file RAB vendor (Excel), pilih sheet dan jumlah baris header yang dilewati |
| **Step 3** | Petakan kolom file vendor ke field yang dibutuhkan (Nama, MAT, PSG, BKR, Satuan, Total) |
| **Step 4** | Klik **Mulai Proses Data** dan tinjau hasilnya di tabel interaktif |

---

## Format File

### Master Material
| Kolom | Keterangan |
|-------|------------|
| `Nama` | Nama material |
| `Kode` | Kode material SOSYS |
| `Tipe` | Tipe material (PLN / Tunai) |

### Output (Template PK SOSYS)
| Kolom | Keterangan |
|-------|------------|
| `Kode Material` | Hasil pencocokan dari master |
| `Nama Material` | Nama dari vendor |
| `Tipe Material` | PLN / Tunai |
| `Referensi Jumlah` | Volume referensi |
| `Jumlah Material Gudang (PLN)` | Volume PLN |
| `Jumlah Material Dipesan (Tunai)` | Volume tunai |
| `Jumlah Pasang` | Volume pemasangan |
| `Jumlah Bongkar` | Volume pembongkaran |

---

## Dependensi

| Package | Kegunaan |
|---------|----------|
| `streamlit` | Framework web UI |
| `pandas` | Manipulasi data |
| `openpyxl` | Baca/tulis file Excel |
| `xlsxwriter` | Export Excel |
| `rapidfuzz` | Fuzzy string matching |
| `numpy` | Komputasi numerik |

---

## Pengembang

Dikembangkan oleh **Tim Magang Konstruksi — Universitas Brawijaya**  
untuk **PT PLN (Persero) UP3 Malang**

---

> *SOSMATE adalah alat bantu internal. Seluruh data yang diproses bersifat lokal dan tidak dikirimkan ke server eksternal.*