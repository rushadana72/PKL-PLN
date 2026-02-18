"""
Data Handlers for SOSYS Material Automation
Functions for loading, validating, and processing data files
"""

import pandas as pd
import openpyxl
import streamlit as st
from typing import Dict, Tuple, List, Optional
from processor import load_master_from_dataframe, clear_fuzzy_cache, fuzzy_match_material
from config import CSV_ENCODINGS, REQUIRED_MASTER_COLUMNS


def load_master_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load master file (Excel or CSV) and validate columns
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        Tuple of (DataFrame, error_message)
        If successful: (df, None)
        If error: (None, error_message)
    """
    try:
        # Read file based on extension
        if uploaded_file.name.endswith('.xlsx'):
            try:
                df_master = pd.read_excel(uploaded_file, sheet_name="MASTER MATERIAL")
            except:
                df_master = pd.read_excel(uploaded_file, sheet_name=0)
        else:
            # Try multiple encodings for CSV
            df_master = None
            for enc in CSV_ENCODINGS:
                try:
                    df_master = pd.read_csv(uploaded_file, sep=';', encoding=enc)
                    break
                except:
                    try:
                        uploaded_file.seek(0)
                        df_master = pd.read_csv(uploaded_file, encoding=enc)
                        break
                    except:
                        continue
            
            if df_master is None:
                return None, "Failed to read CSV file with any supported encoding"
        
        # Validate columns
        df_master.columns = df_master.columns.str.strip()
        cols_lower = {col.lower(): col for col in df_master.columns}
        
        missing_cols = []
        col_mapping = {}
        
        for req_col in REQUIRED_MASTER_COLUMNS:
            found = False
            for actual_col_lower, actual_col in cols_lower.items():
                if req_col.lower() in actual_col_lower:
                    col_mapping[req_col] = actual_col
                    found = True
                    break
            if not found:
                missing_cols.append(req_col)
        
        if missing_cols:
            return None, f"Missing required columns: {missing_cols}\nAvailable: {list(df_master.columns)}"
        
        # Rename to standard format
        df_master = df_master.rename(columns=col_mapping)
        
        return df_master, None
        
    except Exception as e:
        return None, f"Error loading master file: {str(e)}"


def get_visible_sheets(uploaded_file) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Get list of visible sheets from Excel file
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        Tuple of (sheet_list, error_message)
    """
    try:
        wb = openpyxl.load_workbook(uploaded_file, read_only=True, keep_vba=False)
        
        visible_sheets = [
            sheet.title for sheet in wb.worksheets 
            if sheet.sheet_state == 'visible'
        ]
        wb.close()
        
        if not visible_sheets:
            return None, "No visible sheets found in the file"
        
        return visible_sheets, None
        
    except Exception as e:
        return None, f"Error reading Excel file: {str(e)}"


def update_material_codes(edited_df: pd.DataFrame, master_dict: Dict) -> Tuple[pd.DataFrame, bool]:
    """
    Update Kode Material and Tipe Material based on Nama Material changes
    Uses exact match first, then fuzzy matching
    
    Args:
        edited_df: DataFrame with potentially edited Nama Material
        master_dict: Master material dictionary
    
    Returns:
        Tuple of (updated_df, changes_made)
    """
    perubahan_terjadi = False
    
    for index, row in edited_df.iterrows():
        nama_input = str(row['Nama Material']).strip()
        
        # Skip empty or NaN values
        if not nama_input or nama_input.lower() == 'nan':
            continue
        
        # Try exact match first
        if nama_input in master_dict:
            target_kode = master_dict[nama_input].get('Kode', '-')
            target_tipe = master_dict[nama_input].get('Tipe', '-')
        else:
            # Use fuzzy matching if exact match not found
            matched_name, score = fuzzy_match_material(nama_input, master_dict, threshold=0.8)
            
            if matched_name:
                target_kode = master_dict[matched_name].get('Kode', '-')
                target_tipe = master_dict[matched_name].get('Tipe', '-')
            else:
                target_kode = '-'
                target_tipe = '-'
        
        # Update if there are differences
        if row['Kode Material'] != target_kode or row['Tipe Material'] != target_tipe:
            edited_df.at[index, 'Kode Material'] = target_kode
            edited_df.at[index, 'Tipe Material'] = target_tipe
            perubahan_terjadi = True
    
    return edited_df, perubahan_terjadi


def process_master_data(uploaded_file) -> Tuple[Optional[Dict], Optional[str], Optional[str]]:
    """
    Process master file and convert to dictionary
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        Tuple of (master_dict, success_message, error_message)
    """
    # Load file
    df_master, error = load_master_file(uploaded_file)
    if error:
        return None, None, error
    
    # Convert to dictionary
    master_dict = load_master_from_dataframe(df_master)
    
    if not master_dict:
        return None, None, "Database Master Material kosong atau tidak valid"
    
    # Clear fuzzy matching cache when new master data is loaded
    clear_fuzzy_cache()
    
    success_msg = f"Database berhasil dimuat! Total data: **{len(master_dict)}** material."
    return master_dict, success_msg, None


def validate_column_selection(config: Dict[str, int], df_shape: Tuple[int, int]) -> Tuple[bool, str]:
    """
    Validate if selected columns are within DataFrame bounds
    
    Args:
        config: Dictionary with column indices
        df_shape: Shape of the DataFrame (rows, cols)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    max_col_index = df_shape[1] - 1
    max_col = max(config.values())
    
    if max_col > max_col_index:
        return False, f"Selected column index {max_col} exceeds file columns (max: {max_col_index})"
    
    return True, ""
