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
    new_master = st.file_uploader("Update Database (Excel/CSV)", type=['xlsx', 'csv'])
    
    if new_master and st.button("Refresh Database"):
        try:
            if new_master.name.endswith('.xlsx'):
                df_master_new = pd.read_excel(new_master, sheet_name="MASTER MATERIAL")
            else:
                df_master_new = pd.read_csv(new_master)
            
            kolom_wajib = ['Nama', 'Kode', 'Tipe']
            if all(k in df_master_new.columns for k in kolom_wajib):
                new_dict = {}
                for _, row in df_master_new.iterrows():
                    new_dict[str(row['Nama']).strip()] = {
                        'Kode': str(row['Kode']).strip(),
                        'Tipe': str(row['Tipe']).strip()
                    }
                with open("master_data.py", "w", encoding="utf-8") as f:
                    f.write(f"MASTER_LIST = {repr(new_dict)}")
                st.success("✅ Database Updated!")
                st.rerun()
            else:
                st.error(f"Kolom wajib tidak ditemukan: {kolom_wajib}")
        except Exception as e:
            st.error(f"Error: {e}")

st.title("🛠️ :orange[SOMEON] SOSYS Material Automation")
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

# --- 5. TAMPILAN TABEL VENDOR ---
if st.session_state['df_hasil'] is not None:
    st.markdown("---")
    display_name = sheet_name if 'sheet_name' in locals() else 'data proses'
    st.subheader(f"📋 Hasil Konversi: {display_name}")
    
    # Pre-processing tampilan (Mencegah modifikasi data asli di session_state)
    df_vendor_view = st.session_state['df_hasil'].copy()
    kolom_angka = ['Referensi Jumlah', 'Jumlah Material Gudang (PLN)', 'Jumlah Material Dipesan (Tunai)', 'Jumlah Pasang', 'Jumlah Bongkar']
    
    for col in kolom_angka:
        if col in df_vendor_view.columns:
            df_vendor_view[col] = pd.to_numeric(df_vendor_view[col], errors='coerce').replace(0, None)

    # Editor Tabel Vendor
    edited_df = st.data_editor(
        df_vendor_view,
        num_rows="dynamic",
        key=f"editor_vendor_{display_name}", # Key unik agar tidak bentrok
        use_container_width=True,
        column_config={
            "Kode Material": st.column_config.Column(disabled=True),
            "Tipe Material": st.column_config.Column(disabled=True),
        }
    )

    # Cek Perubahan untuk Re-lookup
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
        st.session_state['df_hasil'] = edited_df
        st.rerun()

    # Logika Download (Engine XlsxWriter agar kompatibel SOSYS)
    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        edited_df.to_excel(writer, index=False, sheet_name=display_name[:31])
    
    st.download_button(
        "📥 Download Template", 
        towrite.getvalue(), 
        f"{display_name}.xlsx", 
        key="btn_download_final"
    )

# --- 6. BAGIAN DATABASE MASTER (DIISOLASI AGAR TIDAK MUNCUL 2 TABEL) ---
st.markdown("---")

# Mengunci Expander jika sedang mencari
if 'input_cari' not in st.session_state:
    st.session_state['input_cari'] = ""

is_searching = st.session_state['input_cari'] != ""

with st.expander("📂 Lihat Database Master Material", expanded=is_searching):
    st.subheader("Data Referensi Sistem")
    if master_dict:

        # Menampilkan metrik jumlah material agar tampilan lebih profesional
        total_data = len(master_dict)
        #st.metric(label="Total Material Terdata", value=f"{total_data} Item")
        st.markdown(
            f"### :orange[Total Material ] <span style='font-size: 40px; color: #39e75f;'>{total_data}</span> :orange[Item]", 
            unsafe_allow_html=True
        )

        # MENGGUNAKAN NAMA VARIABEL BERBEDA (df_master_db) AGAR TIDAK BENTROK DENGAN df_display
        df_master_db = pd.DataFrame.from_dict(master_dict, orient='index').reset_index()
        df_master_db.columns = ['Nama Material', 'Kode Material', 'Tipe Material']
        
        st.info("💡 Klik sel lalu **Ctrl+C** untuk copy nama yang benar.")
        
        # Search Box dengan key session_state
        cari = st.text_input("🔍 Cari di Database:", key="input_cari")
        
        if cari:
            # Filter menggunakan variabel unik df_master_filtered
            df_master_filtered = df_master_db[
                df_master_db['Nama Material'].str.contains(cari, case=False, regex=False) | 
                df_master_db['Kode Material'].str.contains(cari, case=False, regex=False)
            ]
            st.dataframe(df_master_filtered, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_master_db.head(5), use_container_width=True, hide_index=True)