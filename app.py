"""
SOSYS Material Automation - Main Application
Streamlit app for converting vendor RAB files to SOSYS format with AI-powered fuzzy matching
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import custom modules
from config import (
    APP_TITLE, APP_ICON, APP_LAYOUT, 
    DEFAULT_COLUMNS, DEFAULT_SKIP_ROWS, MAX_SKIP_ROWS,
    KOLOM_OPTIONS, COLUMN_HELP, COLUMN_LABELS,
    NUMERIC_COLUMNS, UI_TEXT
)
from styles import get_custom_css
from ui_components import (
    render_header, render_step_card, render_statistics, 
    render_footer, create_download_section,
    prepare_dataframe_for_display, get_column_config
)
from data_handlers import (
    process_master_data, get_visible_sheets, 
    update_material_codes, validate_column_selection
)
from processor import huruf_ke_angka, proses_data_vendor


# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title=APP_TITLE, 
    layout=APP_LAYOUT,
    page_icon=APP_ICON
)

# Load custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ==================== SESSION STATE INITIALIZATION ====================
if 'df_hasil' not in st.session_state:
    st.session_state['df_hasil'] = None
if 'master_dict' not in st.session_state:
    st.session_state['master_dict'] = None
if 'master_uploaded' not in st.session_state:
    st.session_state['master_uploaded'] = False
if 'master_success_message' not in st.session_state:
    st.session_state['master_success_message'] = None


# ==================== MAIN UI ====================
render_header()


# ==================== STEP 1: MASTER DATABASE ====================
render_step_card(1, UI_TEXT['step1_title'], UI_TEXT['step1_desc'])

uploaded_master = st.file_uploader(
    "Pilih File Master",
    type=['xlsx', 'csv'],
    help="File harus berisi kolom: Nama, Kode, Tipe",
    key="master_uploader",
    label_visibility="collapsed"
)

if uploaded_master:
    if st.button("Proses Data Master", width='stretch', type="primary"):
        master_dict, success_msg, error_msg = process_master_data(uploaded_master)
        
        if error_msg:
            st.error(error_msg)
        else:
            st.session_state['master_dict'] = master_dict
            st.session_state['master_uploaded'] = True
            st.session_state['master_success_message'] = success_msg
            st.rerun()

# Display success message if exists
if st.session_state.get('master_success_message'):
    st.success(st.session_state['master_success_message'])

st.markdown("<br>", unsafe_allow_html=True)


# ==================== STEP 2: UPLOAD VENDOR FILE ====================
if st.session_state['master_uploaded']:
    render_step_card(2, UI_TEXT['step2_title'], UI_TEXT['step2_desc'])
    
    uploaded_vendor = st.file_uploader(
        "Pilih File Vendor",
        type=['xlsx', 'xls'],
        help="Unggah file Excel yang berisi data RAB dari vendor",
        key="vendor_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_vendor:
        visible_sheets, error = get_visible_sheets(uploaded_vendor)
        
        if error:
            st.error(error)
        else:
            # Sheet selection and Skip rows
            col_sheet, col_skip = st.columns([3, 1])
            
            with col_sheet:
                sheet_name = st.selectbox(
                    "Pilih Sheet",
                    visible_sheets,
                    help="Pilih sheet yang berisi data RAB vendor"
                )
            
            with col_skip:
                skip_rows = st.number_input(
                    "Lewati Baris",
                    min_value=0,
                    max_value=MAX_SKIP_ROWS,
                    value=DEFAULT_SKIP_ROWS,
                    help="Jumlah baris header yang akan dilewati"
                )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # ==================== STEP 3: COLUMN CONFIGURATION ====================
    if uploaded_vendor and 'sheet_name' in locals():
        render_step_card(3, UI_TEXT['step3_title'], UI_TEXT['step3_desc'])
        
        st.info("Tentukan kolom mana yang berisi data yang diperlukan")
        
        # Column selector
        col1, col2, col3 = st.columns(3)
        
        with col1:
            h_uraian = st.selectbox(
                COLUMN_LABELS['uraian'], 
                KOLOM_OPTIONS, 
                index=DEFAULT_COLUMNS['uraian'],
                help=COLUMN_HELP['uraian']
            )
            
            h_mat = st.selectbox(
                COLUMN_LABELS['mat'], 
                KOLOM_OPTIONS, 
                index=DEFAULT_COLUMNS['mat'],
                help=COLUMN_HELP['mat']
            )
        
        with col2:
            h_psg = st.selectbox(
                COLUMN_LABELS['psg'], 
                KOLOM_OPTIONS, 
                index=DEFAULT_COLUMNS['psg'],
                help=COLUMN_HELP['psg']
            )
            
            h_bkr = st.selectbox(
                COLUMN_LABELS['bkr'], 
                KOLOM_OPTIONS, 
                index=DEFAULT_COLUMNS['bkr'],
                help=COLUMN_HELP['bkr']
            )
        
        with col3:
            h_satuan = st.selectbox(
                COLUMN_LABELS['satuan'], 
                KOLOM_OPTIONS, 
                index=DEFAULT_COLUMNS['satuan'],
                help=COLUMN_HELP['satuan']
            )
            
            h_total = st.selectbox(
                COLUMN_LABELS['total'], 
                KOLOM_OPTIONS, 
                index=DEFAULT_COLUMNS['total'],
                help=COLUMN_HELP['total']
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        
        # ==================== STEP 4: PROCESS ====================
        render_step_card(4, UI_TEXT['step4_title'], UI_TEXT['step4_desc'])
        
        btn_proses = st.button("Mulai Proses Data", width='stretch', type="primary")
        
        if btn_proses:
            try:
                # Read vendor file
                df_v = pd.read_excel(uploaded_vendor, sheet_name=sheet_name, skiprows=skip_rows, header=None)
                
                # Build configuration
                config = {
                    'c_uraian': huruf_ke_angka(h_uraian),
                    'c_mat': huruf_ke_angka(h_mat),
                    'c_psg': huruf_ke_angka(h_psg),
                    'c_bkr': huruf_ke_angka(h_bkr),
                    'c_satuan': huruf_ke_angka(h_satuan),
                    'c_total': huruf_ke_angka(h_total)
                }
                
                # Validate columns
                is_valid, error_msg = validate_column_selection(config, df_v.shape)
                if not is_valid:
                    st.error(error_msg)
                    st.stop()
                
                # Process data
                df_hasil = proses_data_vendor(
                    df_v,
                    st.session_state['master_dict'],
                    config
                )
                
                if df_hasil.empty:
                    st.warning("Tidak ada data yang memenuhi kriteria filter")
                else:
                    st.session_state['df_hasil'] = df_hasil
                    matched = (df_hasil['Kode Material'] != '-').sum()
                    st.success(f"Berhasil memproses **{len(df_hasil)}** material!")
                
            except Exception as e:
                st.error(f"Processing error: {str(e)}")
                st.exception(e)


# ==================== RESULTS DISPLAY ====================
if st.session_state['df_hasil'] is not None:
    st.markdown("<hr>", unsafe_allow_html=True)
    
    display_name = sheet_name if 'sheet_name' in locals() else 'processed_data'
    df_stats = st.session_state['df_hasil']
    
    # Show statistics
    render_statistics(df_stats)
    
    # Filter options
    unmatched = (df_stats['Kode Material'] == '-').sum()
    if unmatched > 0:
        show_unmatched = st.checkbox(
            f"Show only unmatched materials ({unmatched} items)",
            value=False
        )
    else:
        show_unmatched = False
    
    # Prepare data for display
    df_vendor_view = st.session_state['df_hasil'].copy()
    
    if show_unmatched:
        df_vendor_view = df_vendor_view[df_vendor_view['Kode Material'] == '-']
    
    df_vendor_view = prepare_dataframe_for_display(df_vendor_view, NUMERIC_COLUMNS)
    
    # Data editor
    st.markdown(f"### <i class='fas fa-solid fa-table-list'></i> Data Hasil Konversi: {display_name}", unsafe_allow_html=True)
    
    edited_df = st.data_editor(
        df_vendor_view,
        num_rows="dynamic",
        key=f"editor_vendor_{display_name}",
        width='stretch',
        column_config=get_column_config(),
        hide_index=True
    )
    
    st.markdown("""
        <div style='background-color: #fff3cd; padding: 0.75rem 1rem; border-radius: 0.375rem; border-left: 4px solid #ffc107; margin-top: 1rem;'>
            <i class='fas fa-edit'></i> <strong>Tabel dapat diedit:</strong> Klik sel untuk mengubah nilai. 
            Perubahan <strong>Nama Material</strong> akan otomatis memperbarui <strong>Kode & Tipe Material</strong> dari database master.
        </div>
        """, unsafe_allow_html=True)

    # Auto-update logic: Check for Nama Material changes and update Kode & Tipe
    master_dict = st.session_state.get('master_dict', {})
    edited_df, perubahan_terjadi = update_material_codes(edited_df, master_dict)
    
    # Update session state and rerun if changes occurred
    if perubahan_terjadi:
        st.session_state['df_hasil'] = edited_df
        st.rerun()
    else:
        st.session_state['df_hasil'] = edited_df
    
    # Download section
    create_download_section(edited_df, display_name)


# ==================== FOOTER ====================
render_footer()
