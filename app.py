import streamlit as st
import pandas as pd
import os
import sys
import importlib.util
import io
import openpyxl 

# --- 1. FUNGSI LOAD MASTER ---
def load_master_data_lokal():
    file_path = "master_data.py"
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("MASTER_LIST = {}")
    
    spec = importlib.util.spec_from_file_location("master_data", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["master_data"] = module
    spec.loader.exec_module(module)
    return module.MASTER_LIST

# --- 2. IMPORT LOGIKA ---
from processor import huruf_ke_angka, proses_data_vendor
from converter import update_master_script  

st.set_page_config(page_title="SOSYS Tool", layout="wide")

# Muat data referensi
master_dict = load_master_data_lokal()

# Inisialisasi memori untuk tabel agar tidak hilang
if 'df_hasil' not in st.session_state:
    st.session_state['df_hasil'] = None

# --- UPDATE DI BAGIAN SIDEBAR ---
with st.sidebar:
    st.header("Pengaturan")
    st.subheader("Upload Master Material")
    new_master = st.file_uploader("Update Database (Excel/CSV)", type=['xlsx', 'csv'])
    
    if new_master and st.button("Refresh Database"):
        try:
            if new_master.name.endswith('.xlsx'):
                # Target spesifik sheet "MASTER MATERIAL"
                df_master_new = pd.read_excel(new_master, sheet_name="MASTER MATERIAL")
            else:
                df_master_new = pd.read_csv(new_master)
            
            # Gunakan kolom Nama, Kode, dan Tipe sesuai file Master.xlsx Anda
            new_dict = {}
            for _, row in df_master_new.iterrows():
                nama_key = str(row['Nama']).strip()
                new_dict[nama_key] = {
                    'Kode': str(row['Kode']).strip(),
                    'Tipe': str(row['Tipe']).strip()
                }
            
            # Simpan ke master_data.py
            with open("master_data.py", "w", encoding="utf-8") as f:
                f.write(f"MASTER_LIST = {repr(new_dict)}")
            
            st.success("✅ Database 'MASTER MATERIAL' Updated!")
            st.rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# --- UPDATE PADA BAGIAN DISPLAY TABEL (DI MAIN AREA) ---
if st.session_state['df_hasil'] is not None:
    df_display = st.session_state['df_hasil'].copy()
    
    # Kolom jumlah sesuai format SOSYS Anda
    kolom_angka = [
        'Referensi Jumlah', 
        'Jumlah Material Gudang (PLN)', 
        'Jumlah Material Dipesan (Tunai)', 
        'Jumlah Pasang', 
        'Jumlah Bongkar'
    ]
    
    for col in kolom_angka:
        if col in df_display.columns:
            # Paksa menjadi numerik lalu ubah 0 menjadi None agar terlihat kosong di web
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce').replace(0, None)

    # Render editor dengan data yang sudah bersih dari angka 0
    edited_df = st.data_editor(
        df_display,
        num_rows="dynamic",
        key="editor_sosys",
        use_container_width=True
    )

# --- 4. MAIN AREA: KONVERSI ---
st.title("🛠️ SOSYS Material Automation")
st.subheader("SILAHKAN MASUKAN FILE VENDOR")
uploaded_vendor = st.file_uploader("Upload File Vendor (Excel)", type=['xlsx'])

if uploaded_vendor:
    wb = openpyxl.load_workbook(uploaded_vendor, read_only=True)
    sheet_tertampil = [s.title for s in wb.worksheets if s.sheet_state == 'visible']
    wb.close()

    if not sheet_tertampil:
        st.error("Tidak ada sheet yang terlihat di file ini.")
        st.stop()

    sheet_name = st.selectbox("Pilih Sheet Vendor:", sheet_tertampil)
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        h_uraian = st.text_input("Kolom Nama Material", "C")
        h_mat = st.text_input("Kolom Volume MAT", "H")
    with col2:
        h_psg = st.text_input("Kolom Volume PSG", "I")
        h_bkr = st.text_input("Kolom Volume BKR", "J")
    with col3:
        h_satuan = st.text_input("Kolom Harga Satuan", "L")
        h_total = st.text_input("Kolom Total Harga", "R")
    
    if st.button("Proses Data", key="btn_proses_utama"):
        df_v = pd.read_excel(uploaded_vendor, sheet_name=sheet_name, skiprows=6, header=None)
        
        config = {
            'c_uraian': huruf_ke_angka(h_uraian),
            'c_mat': huruf_ke_angka(h_mat),
            'c_psg': huruf_ke_angka(h_psg),
            'c_bkr': huruf_ke_angka(h_bkr),
            'c_satuan': huruf_ke_angka(h_satuan),
            'c_total': huruf_ke_angka(h_total)
        }
        
        # 1. Jalankan proses original
        df_hasil = proses_data_vendor(df_v, master_dict, config)
        
        # 2. JANGAN gunakan .replace(0, None) di sini karena bisa merusak tipe data
        # Biarkan angka 0 tetap ada di memori session_state untuk keamanan data
        st.session_state['df_hasil'] = df_hasil

    # Tampilan Tabel Hasil Konversi
    if st.session_state['df_hasil'] is not None:
        st.success(f"Berhasil! {len(st.session_state['df_hasil'])} item ditemukan.")
        st.info("💡 Perbaiki typo pada 'Nama Material' lalu tekan Enter untuk update otomatis.")
        
        # --- 1. PRE-PROCESSING UNTUK TAMPILAN (MENGOSONGKAN 0) ---
        # Kita buat copy agar data asli di session_state tidak berubah tipe datanya
        df_display = st.session_state['df_hasil'].copy()
        
        # Daftar semua kolom yang ingin dibersihkan dari angka 0
        kolom_angka = [
            'Referensi Jumlah', 
            'Jumlah Material Gudang (PLN)', 
            'Jumlah Material Dipesan (Tunai)', 
            'Jumlah Pasang', 
            'Jumlah Bongkar',
            'Volume MAT', 
            'Volume PSG', 
            'Volume BKR'
        ]
        
        for col in kolom_angka:
            if col in df_display.columns:
                # Mengubah angka 0 menjadi None agar sel terlihat kosong/blank di Streamlit
                df_display[col] = df_display[col].replace(0, None)

        # --- 2. TAMPILKAN EDITOR ---
        # Gunakan df_display yang sudah bersih dari angka 0
        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            key=f"editor_sosys_{sheet_name}", # Key menjadi dinamis
            use_container_width=True,
            column_config={
                "Kode Material": st.column_config.Column(
                    "Kode Material",
                    help="Kolom ini terkunci (otomatis dari Master)",
                    disabled=True, # MENGUNCI KOLOM KODE
                ),
                "Tipe Material": st.column_config.Column(
                    "Tipe Material",
                    help="Kolom ini terkunci (otomatis dari Master)",
                    disabled=True, # MENGUNCI KOLOM TIPE
                ),
            }
        )

        # --- 3. LOGIKA RE-LOOKUP OTOMATIS ---
        perubahan_terjadi = False 
        
        for index, row in edited_df.iterrows():
            nama_input = str(row['Nama Material']).strip()
            
            target_kode = master_dict.get(nama_input, {}).get('Kode', "-")
            target_tipe = master_dict.get(nama_input, {}).get('Tipe', "-")
            
            if row['Kode Material'] != target_kode or row['Tipe Material'] != target_tipe:
                edited_df.at[index, 'Kode Material'] = target_kode
                edited_df.at[index, 'Tipe Material'] = target_tipe
                perubahan_terjadi = True
        
        if perubahan_terjadi:
            # Simpan kembali ke session_state agar perubahan permanen
            st.session_state['df_hasil'] = edited_df
            st.rerun()
        
        # --- 4. LOGIKA DOWNLOAD ---
        towrite = io.BytesIO()
        # Pastikan saat di-download, sel yang None tetap menjadi sel kosong di Excel
        edited_df.to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)
        st.download_button(
            "📥 Download Template", 
            towrite, 
            f"{sheet_name}.xlsx",
            key="btn_download_final"
        )

# --- 5. BAGIAN PALING BAWAH: DATABASE MASTER ---
st.markdown("---")
with st.expander("📂 Lihat Database Master Material", expanded=False):
    st.subheader("Data Referensi Sistem")
    if master_dict:
        df_master = pd.DataFrame.from_dict(master_dict, orient='index').reset_index()
        df_master.columns = ['Nama Material', 'Kode Material', 'Tipe Material']
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Total Material", len(df_master))
        st.success("Cukup klik sekali pada cell, lalu tekan ctrl + c untuk copy")
        cari = st.text_input("🔍 Cari di Database:", "", key="cari_database_bawah")
        if cari:
            df_display = df_master[
                df_master['Nama Material'].str.contains(cari, case=False, regex=False) | 
                df_master['Kode Material'].str.contains(cari, case=False, regex=False)
            ]
        else:
            df_display = df_master
        st.dataframe(df_display, use_container_width=True, height=400)
    else:
        st.warning("Database kosong.")