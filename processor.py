import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
import logging
import re
from functools import lru_cache

# Try to import rapidfuzz, fallback to difflib if not available
try:
    from rapidfuzz import fuzz, process
    USE_RAPIDFUZZ = True
except ImportError:
    from difflib import SequenceMatcher
    USE_RAPIDFUZZ = False
    import warnings
    warnings.warn(
        "rapidfuzz not found, using difflib (slower). "
        "Install with: pip install rapidfuzz",
        ImportWarning
    )

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log optimization status
if USE_RAPIDFUZZ:
    logger.info("✅ RapidFuzz loaded - using optimized fuzzy matching (10-100x faster)")
else:
    logger.info("⚠️ RapidFuzz not found - using difflib (slower fallback)")

logger.info("✅ LRU Cache enabled for normalize_text (maxsize=1024) and calculate_similarity (maxsize=2048)")

# ==================== CACHE MANAGEMENT ====================

def clear_fuzzy_cache():
    """
    Clear all fuzzy matching caches
    Panggil fungsi ini jika master data berubah
    """
    normalize_text.cache_clear()
    calculate_similarity.cache_clear()
    logger.info("🗑️ Fuzzy matching cache cleared")


def get_cache_info() -> Dict[str, Any]:
    """
    Get cache statistics
    
    Returns:
        Dictionary dengan info cache hits, misses, size
    """
    return {
        'normalize_text': normalize_text.cache_info()._asdict(),
        'calculate_similarity': calculate_similarity.cache_info()._asdict(),
        'using_rapidfuzz': USE_RAPIDFUZZ
    }

# ==================== FUZZY MATCHING UTILITIES ====================

@lru_cache(maxsize=1024)
def normalize_text(text: str) -> str:
    """
    Normalisasi teks untuk fuzzy matching yang lebih baik
    
    Args:
        text: Teks yang akan dinormalisasi
    
    Returns:
        Teks yang sudah dinormalisasi
    
    Examples:
        >>> normalize_text("KABEL NYY 2x2.5 MM2")
        "kabel nyy 2x2.5 mm2"
        >>> normalize_text("  Kabel  NYM  3X2,5  ")
        "kabel nym 3x2,5"
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase dan strip whitespace
    text = text.lower().strip()
    
    # Normalize multiple spaces menjadi single space
    text = re.sub(r'\s+', ' ', text)
    
    return text


@lru_cache(maxsize=2048)
def calculate_similarity(str1: str, str2: str) -> float:
    """
    Hitung similarity score antara dua string menggunakan RapidFuzz (atau SequenceMatcher sebagai fallback)
    
    Args:
        str1: String pertama
        str2: String kedua
    
    Returns:
        Similarity score (0.0 - 1.0)
    
    Examples:
        >>> calculate_similarity("KABEL NYY", "kabel nyy")
        1.0
        >>> calculate_similarity("KABEL NYY 2x2.5", "KABEL NYY 2x2,5")
        0.96...
    """
    # Normalisasi kedua string
    s1_norm = normalize_text(str1)
    s2_norm = normalize_text(str2)
    
    if not s1_norm or not s2_norm:
        return 0.0
    
    # Exact match setelah normalisasi
    if s1_norm == s2_norm:
        return 1.0
    
    # Calculate similarity
    if USE_RAPIDFUZZ:
        # RapidFuzz: 10-100x lebih cepat dari difflib
        return fuzz.ratio(s1_norm, s2_norm) / 100.0
    else:
        # Fallback ke difflib.SequenceMatcher
        return SequenceMatcher(None, s1_norm, s2_norm).ratio()


def fuzzy_match_material(
    material_name: str, 
    master_dict: Dict[str, Dict], 
    threshold: float = 0.8
) -> Tuple[Optional[str], Optional[float]]:
    """
    Cari material terbaik dari master menggunakan fuzzy matching dengan RapidFuzz
    
    OPTIMIZED VERSION:
    - Menggunakan rapidfuzz.process.extractOne untuk performa optimal
    - Fallback ke manual iteration jika rapidfuzz tidak tersedia
    - Cached normalization untuk speed boost
    
    Args:
        material_name: Nama material dari vendor
        master_dict: Dictionary master material
        threshold: Minimum similarity score (0.0 - 1.0)
    
    Returns:
        Tuple (matched_name, similarity_score) atau (None, None) jika tidak ada match
    
    Examples:
        >>> master = {"KABEL NYY 2x2.5": {...}, "KABEL NYM 3x2.5": {...}}
        >>> fuzzy_match_material("kabel nyy 2x2,5", master, 0.8)
        ("KABEL NYY 2x2.5", 0.96)
    """
    if not material_name or not master_dict:
        return None, None
    
    # Normalize input
    normalized_input = normalize_text(material_name)
    
    if USE_RAPIDFUZZ:
        # FAST PATH: RapidFuzz process.extractOne
        # 10-50x lebih cepat untuk master data besar
        result = process.extractOne(
            normalized_input,
            master_dict.keys(),
            scorer=fuzz.ratio,
            score_cutoff=threshold * 100  # RapidFuzz uses 0-100 scale
        )
        
        if result:
            matched_name, score, _ = result
            return matched_name, score / 100.0  # Convert back to 0-1 scale
        
        return None, None
    
    else:
        # SLOW PATH: Manual iteration dengan difflib (fallback)
        best_match = None
        best_score = 0.0
        
        for master_name in master_dict.keys():
            score = calculate_similarity(material_name, master_name)
            
            if score > best_score:
                best_score = score
                best_match = master_name
        
        # Return hanya jika score melebihi threshold
        if best_score >= threshold:
            return best_match, best_score
        
        return None, None


# ==================== HELPER FUNCTIONS ====================

def huruf_ke_angka(huruf: str) -> int:
    """
    Mengubah input alfabet (A, B, C, AA, AB) menjadi angka (0, 1, 2, 26, 27)
    
    Args:
        huruf: Kolom Excel dalam format huruf (A-Z, AA-ZZ)
    
    Returns:
        Index kolom (0-based)
    
    Examples:
        >>> huruf_ke_angka('A')
        0
        >>> huruf_ke_angka('Z')
        25
        >>> huruf_ke_angka('AA')
        26
    """
    huruf = huruf.upper().strip()
    angka = 0
    for c in huruf:
        angka = angka * 26 + (ord(c) - ord('A') + 1)
    return angka - 1


def load_master_from_dataframe(df_master: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    """
    Membaca DataFrame master dan mengkonversinya menjadi dictionary
    
    Args:
        df_master: DataFrame dengan kolom Nama, Kode, Tipe
    
    Returns:
        Dictionary dengan struktur: {nama_material: {Kode: xxx, Tipe: xxx}}
    """
    try:
        master_dict = {}
        
        for _, row in df_master.iterrows():
            nama_key = str(row['Nama']).strip()
            
            # Skip jika nama kosong atau NaN
            if not nama_key or nama_key.lower() == 'nan':
                continue
            
            master_dict[nama_key] = {
                'Kode': str(row['Kode']).strip() if pd.notna(row['Kode']) else '-',
                'Tipe': str(row['Tipe']).strip() if pd.notna(row['Tipe']) else '-'
            }
        
        logger.info(f"Berhasil memuat {len(master_dict)} material dari master data")
        return master_dict
        
    except Exception as e:
        logger.error(f"Error saat membaca master data: {e}")
        return {}


def validate_config(config: Dict[str, Any], df_shape: tuple) -> Tuple[bool, str]:
    """
    Validasi apakah konfigurasi kolom valid
    
    Args:
        config: Dictionary konfigurasi kolom
        df_shape: Shape dari dataframe (rows, cols)
    
    Returns:
        Tuple (is_valid, error_message)
    """
    max_col_index = df_shape[1] - 1
    
    for key, value in config.items():
        # Skip non-integer config values
        if not isinstance(value, int):
            continue
            
        col_index = value
        if col_index > max_col_index:
            return False, f"Kolom {key} (index {col_index}) melebihi jumlah kolom file ({max_col_index})"
        if col_index < 0:
            return False, f"Kolom {key} memiliki index negatif ({col_index})"
    
    return True, ""


def safe_numeric(value: Any, default: float = 0.0) -> float:
    """
    Konversi nilai ke numerik dengan aman
    
    Args:
        value: Nilai yang akan dikonversi
        default: Nilai default jika konversi gagal
    
    Returns:
        Nilai numerik atau default
    """
    try:
        result = pd.to_numeric(value, errors='coerce')
        return result if pd.notna(result) else default
    except:
        return default


# ==================== MAIN PROCESSING ENGINE ====================

def proses_data_vendor(
    df_v: pd.DataFrame, 
    master_dict: Dict, 
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Memproses data mentah vendor menjadi format SOSYS berdasarkan 
    konfigurasi kolom yang dimasukkan user.
    
    FEATURES:
    - Vectorized operations pandas (optimal performance)
    - Pre-filtering untuk mengurangi iterasi
    - Fuzzy matching untuk toleransi typo/variasi nama
    - Batch processing untuk lookup master
    
    Args:
        df_v: DataFrame vendor (raw)
        master_dict: Dictionary master material
        config: Konfigurasi index kolom (termasuk fuzzy_threshold)
    
    Returns:
        DataFrame hasil konversi dalam format SOSYS
    """
    
    try:
        # Validasi konfigurasi
        is_valid, error_msg = validate_config(config, df_v.shape)
        if not is_valid:
            logger.error(f"Konfigurasi tidak valid: {error_msg}")
            return pd.DataFrame()
        
        # Ekstrak konfigurasi
        c_u = config['c_uraian']
        c_m = config['c_mat']
        c_p = config['c_psg']
        c_b = config['c_bkr']
        c_s = config['c_satuan']
        c_t = config['c_total']
        fuzzy_threshold = 0.8  # Fixed at 80%
        
        # Buat working dataframe dengan kolom yang relevan saja (memory efficient)
        df_work = pd.DataFrame({
            'nama': df_v.iloc[:, c_u].astype(str).str.strip(),
            'vol_mat': pd.to_numeric(df_v.iloc[:, c_m], errors='coerce').fillna(0),
            'vol_psg': pd.to_numeric(df_v.iloc[:, c_p], errors='coerce').fillna(0),
            'vol_bkr': pd.to_numeric(df_v.iloc[:, c_b], errors='coerce').fillna(0),
            'satuan': df_v.iloc[:, c_s].astype(str).str.strip().str.upper(),
            'total': pd.to_numeric(df_v.iloc[:, c_t], errors='coerce').fillna(0)
        })
        
        # Pre-filtering (vectorized) - jauh lebih cepat dari loop
        mask_valid = (
            (df_work['total'] > 0) &  # Harga harus > 0
            (df_work['nama'].str.lower() != 'nan') &  # Bukan NaN
            (~df_work['nama'].str.contains('TOTAL', case=False, na=False))  # Tidak mengandung "TOTAL"
        )
        
        df_filtered = df_work[mask_valid].copy()
        
        logger.info(f"Data terfilter: {len(df_filtered)} dari {len(df_v)} baris")
        
        if df_filtered.empty:
            logger.warning("Tidak ada data yang memenuhi kriteria filter")
            return pd.DataFrame()
        
        # ==================== FUZZY MATCHING LOOKUP ====================
        
        def lookup_with_fuzzy(nama):
            """
            Lookup material dengan prioritas:
            1. Exact match (langsung dari dict)
            2. Fuzzy match (jika exact tidak ketemu)
            """
            # Try exact match first
            if nama in master_dict:
                return pd.Series([
                    master_dict[nama]['Kode'],
                    master_dict[nama]['Tipe'],
                    None,  # match_score (None = exact match)
                    None   # matched_with (None = exact match)
                ])
            
            # Try fuzzy match
            matched_name, score = fuzzy_match_material(nama, master_dict, fuzzy_threshold)
            
            if matched_name:
                return pd.Series([
                    master_dict[matched_name]['Kode'],
                    master_dict[matched_name]['Tipe'],
                    score * 100,  # Convert to percentage
                    matched_name
                ])
            
            # No match found
            return pd.Series(['-', '-', None, None])
        
        # Apply lookup dengan fuzzy matching
        df_filtered[['Kode Material', 'Tipe Material', 'Match Score', 'Matched With']] = \
            df_filtered['nama'].apply(lookup_with_fuzzy)
        
        # ==================== PLN vs TUNAI LOGIC ====================
        
        df_filtered['Jumlah Material Gudang (PLN)'] = np.where(
            df_filtered['satuan'] == 'PLN',
            df_filtered['vol_mat'],
            0
        )
        
        df_filtered['Jumlah Material Dipesan (Tunai)'] = np.where(
            df_filtered['satuan'] != 'PLN',
            df_filtered['vol_mat'],
            0
        )
        
        # ==================== SUSUN HASIL FINAL ====================
        
        # Kolom output sesuai template SOSYS (tanpa kolom fuzzy matching info)
        result_columns = {
            'Kode Material': df_filtered['Kode Material'],
            'Nama Material': df_filtered['nama'],
            'Tipe Material': df_filtered['Tipe Material'],
            'Referensi Jumlah': 1,
            'Jumlah Material Gudang (PLN)': df_filtered['Jumlah Material Gudang (PLN)'],
            'Jumlah Material Dipesan (Tunai)': df_filtered['Jumlah Material Dipesan (Tunai)'],
            'Jumlah Pasang': df_filtered['vol_psg'],
            'Jumlah Bongkar': df_filtered['vol_bkr']
        }
        
        df_hasil = pd.DataFrame(result_columns)
        
        # Reset index
        df_hasil = df_hasil.reset_index(drop=True)
        
        # ==================== LOG STATISTIK ====================
        
        total_items = len(df_hasil)
        exact_matched = (df_hasil['Kode Material'] != '-').sum()
        
        # Hitung fuzzy match dari kolom internal df_filtered
        fuzzy_matched = df_filtered['Match Score'].notna().sum()
        exact_only = exact_matched - fuzzy_matched
        unmatched = total_items - exact_matched
        
        logger.info(
            f"Hasil: {total_items} items | "
            f"Exact: {exact_only} | "
            f"Fuzzy: {fuzzy_matched} | "
            f"Unmatched: {unmatched}"
        )
        
        return df_hasil
        
    except Exception as e:
        logger.error(f"Error dalam proses_data_vendor: {e}", exc_info=True)
        return pd.DataFrame()


# ==================== SUMMARY REPORT ====================

def generate_summary(df_hasil: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate statistik summary dari hasil konversi
    
    Args:
        df_hasil: DataFrame hasil konversi
    
    Returns:
        Dictionary berisi statistik
    """
    if df_hasil.empty:
        return {
            'total_items': 0,
            'matched': 0,
            'unmatched': 0,
            'fuzzy_matched': 0,
            'exact_matched': 0,
            'pln_items': 0,
            'tunai_items': 0
        }
    
    matched = (df_hasil['Kode Material'] != '-').sum()
    fuzzy_matched = df_hasil['Match Score'].notna().sum() if 'Match Score' in df_hasil.columns else 0
    
    return {
        'total_items': len(df_hasil),
        'matched': matched,
        'exact_matched': matched - fuzzy_matched,
        'fuzzy_matched': fuzzy_matched,
        'unmatched': (df_hasil['Kode Material'] == '-').sum(),
        'pln_items': (df_hasil['Jumlah Material Gudang (PLN)'] > 0).sum(),
        'tunai_items': (df_hasil['Jumlah Material Dipesan (Tunai)'] > 0).sum(),
        'total_vol_mat': df_hasil['Jumlah Material Gudang (PLN)'].sum() + 
                        df_hasil['Jumlah Material Dipesan (Tunai)'].sum(),
        'total_pasang': df_hasil['Jumlah Pasang'].sum(),
        'total_bongkar': df_hasil['Jumlah Bongkar'].sum()
    }