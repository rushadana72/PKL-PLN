import pandas as pd
import pprint
        
# Fungsi 1: Alat bantu konversi koordinat Excel
def huruf_ke_angka(huruf):
    """Mengubah input alfabet (A, B, C) menjadi angka (0, 1, 2)"""
    huruf = huruf.upper().strip()
    angka = 0
    for c in huruf:
        angka = angka * 26 + (ord(c) - ord('A') + 1)
    return angka - 1

# Fungsi 2: Alat bantu baca Master Data
def load_master_data(file_obj):
    """Membaca file master_data.csv dan menyimpannya dalam dictionary"""
    # Menggunakan try-except untuk menangani masalah encoding (ANSI vs UTF-8)
    try:
        # file_obj bisa berupa path atau object upload dari Streamlit
        df_master = pd.read_csv(file_obj, sep=';', encoding='cp1252')
    except:
        df_master = pd.read_csv(file_obj, sep=';', encoding='utf-8')
    
    master_dict = {}
    for _, row in df_master.iterrows():
        # Kolom 0: Nama, Kolom 1: Kode, Kolom 2: Tipe
        nama_key = str(row.iloc[0]).strip()
        master_dict[nama_key] = {
            'Kode': row.iloc[1],
            'Tipe': row.iloc[2]
        }
    return master_dict

# Fungsi 3: Logika Bisnis Utama (The Engine)
def proses_data_vendor(df_v, master_dict, config):
    """
    Memproses data mentah vendor menjadi format SOSYS berdasarkan 
    konfigurasi kolom yang dimasukkan user.
    """
    hasil_final = []
    
    # Ambil index kolom dari config yang dikirim dari app.py
    c_u = config['c_uraian']
    c_m = config['c_mat']
    c_p = config['c_psg']
    c_b = config['c_bkr']
    c_s = config['c_satuan']
    c_t = config['c_total']

    for i in range(len(df_v)):
        try:
            nama_v = str(df_v.iloc[i, c_u]).strip()
            val_total = pd.to_numeric(df_v.iloc[i, c_t], errors='coerce') or 0
            
            # Filter utama: Harga > 0, Nama bukan NaN, Nama tidak mengandung 'TOTAL'
            if val_total > 0 and nama_v.lower() != 'nan' and "TOTAL" not in nama_v.upper():
                
                v_mat = pd.to_numeric(df_v.iloc[i, c_m], errors='coerce') or 0
                v_psg = pd.to_numeric(df_v.iloc[i, c_p], errors='coerce') or 0
                v_bkr = pd.to_numeric(df_v.iloc[i, c_b], errors='coerce') or 0
                h_sat = str(df_v.iloc[i, c_s]).strip().upper()

                # Cari di Master
                info = master_dict.get(nama_v, {'Kode': '-', 'Tipe': '-'})

                # Logika PLN vs TUNAI
                jml_pln = v_mat if h_sat == "PLN" else 0
                jml_tunai = v_mat if h_sat != "PLN" else 0

                hasil_final.append({
                    'Kode Material': info['Kode'],
                    'Nama Material': nama_v,
                    'Tipe Material': info['Tipe'],
                    'Referensi Jumlah': 1,
                    'Jumlah Material Gudang (PLN)': jml_pln,
                    'Jumlah Material Dipesan (Tunai)': jml_tunai,
                    'Jumlah Pasang': v_psg,
                    'Jumlah Bongkar': v_bkr
                })
        except:
            continue
            
    return pd.DataFrame(hasil_final)