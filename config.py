"""
Configuration file for SOSYS Material Automation
Contains all constants, default values, and configuration settings
"""

# ==================== APP CONFIGURATION ====================
APP_TITLE = "SOSMATE - Otomasi Material SOSYS"
APP_SUBTITLE = "Otomasi Konversi Material RAB Vendor ke Template PK SOSYS"
APP_ICON = "assets/favicon-logo.png"
APP_LAYOUT = "centered"

# ==================== FILE CONFIGURATION ====================
MASTER_FILE_TYPES = ['xlsx', 'csv']
VENDOR_FILE_TYPES = ['xlsx', 'xls']

REQUIRED_MASTER_COLUMNS = ['Nama', 'Kode', 'Tipe']

# CSV encoding options to try
CSV_ENCODINGS = ['cp1252', 'utf-8', 'latin1']

# ==================== COLUMN CONFIGURATION ====================
# Default column indices (Excel format)
DEFAULT_COLUMNS = {
    'uraian': 2,    # C
    'mat': 7,       # H
    'psg': 8,       # I
    'bkr': 9,       # J
    'satuan': 11,   # L
    'total': 17     # R
}

# Column options for dropdown (A-Z, AA-AZ)
KOLOM_HURUF = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
KOLOM_OPTIONS = KOLOM_HURUF + [f'A{c}' for c in KOLOM_HURUF]

# ==================== PROCESSING CONFIGURATION ====================
# Default skip rows for vendor file
DEFAULT_SKIP_ROWS = 6
MAX_SKIP_ROWS = 50

# Fuzzy matching threshold (0.0 - 1.0)
FUZZY_THRESHOLD = 0.8

# ==================== OUTPUT CONFIGURATION ====================
# Columns in the final output DataFrame
OUTPUT_COLUMNS = [
    'Kode Material',
    'Nama Material', 
    'Tipe Material',
    'Referensi Jumlah',
    'Jumlah Material Gudang (PLN)',
    'Jumlah Material Dipesan (Tunai)',
    'Jumlah Pasang',
    'Jumlah Bongkar'
]

# Numeric columns for display formatting
NUMERIC_COLUMNS = [
    'Referensi Jumlah',
    'Jumlah Material Gudang (PLN)',
    'Jumlah Material Dipesan (Tunai)',
    'Jumlah Pasang',
    'Jumlah Bongkar'
]

# ==================== UI TEXT ====================
UI_TEXT = {
    'step1_title': 'Database Master Material',
    'step1_desc': (
        'Unggah file Database Master Material sebagai referensi utama proses pencocokan data. \n\n'
        'Format yang didukung: Excel (.xlsx) atau CSV dengan kolom: Nama, Kode, Tipe.'
    ),
    
    'step2_title': 'File RAB Vendor',
    'step2_desc': (
        'Unggah file RAB dari vendor yang akan dikonversi ke template PK SOSYS.\n\n'
        'Format yang didukung: Excel (.xlsx, .xls).'
    ),
    
    'step3_title': 'Konfigurasi Kolom',
    'step3_desc': 'Lakukan penyesuaian kolom file vendor. Pilih kolom yang sesuai untuk setiap field yang tersedia.',
    
    'step4_title': 'Proses dan Transformasi Data',
    'step4_desc': 'Klik tombol proses untuk menjalankan konversi data menggunakan sistem pencocokan otomatis.',
}

# ==================== COLUMN HELP TEXT ====================
COLUMN_HELP = {
    'uraian': 'Kolom yang memuat nama atau deskripsi material',
    'mat': 'Kolom volume material (MAT)',
    'psg': 'Kolom volume pekerjaan pemasangan (PSG)',
    'bkr': 'Kolom volume pembongkaran (BKR)',
    'satuan': 'Kolom satuan untuk membedakan kategori PLN dan TUNAI',
    'total': 'Kolom total nilai harga yang digunakan sebagai filter data'
}

# ==================== COLUMN LABELS ====================
COLUMN_LABELS = {
    'uraian': 'Kolom Nama Material',
    'mat': 'Kolom Volume MAT',
    'psg': 'Kolom Volume PSG',
    'bkr': 'Kolom Volume BKR',
    'satuan': 'Kolom Satuan (PLN/TUNAI)',
    'total': 'Kolom Total Nilai Harga'
}
