"""
Reusable UI Components for SOSYS Material Automation
Contains all UI rendering functions
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from typing import Dict, Any


def render_header():
    """Render the main header with title and subtitle"""
    st.markdown("""
    <div class="main-title">
        <i class="fas fa-bolt"></i>
        SOSYS Order Synchronization 
    </div>
    <div class="subtitle">
        Sinkronisasi Material RAB Vendor ke Template PK SOSYS
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def render_step_card(step_number: int, title: str, description: str):
    """
    Render a step card with number, title and description
    
    Args:
        step_number: Step number (1, 2, 3, 4)
        title: Step title
        description: Step description
    """
    # Get icon based on step number
    icons = {
        1: 'database',
        2: 'file-excel',
        3: 'sliders-h',
        4: 'cogs'
    }
    icon = icons.get(step_number, 'check')
    
    st.markdown(f"""
    <div class="step-card">
        <div class="step-title">
            <span class="step-number">{step_number}</span>
            <i class="fas fa-{icon} icon"></i>
            {title}
        </div>
        <div class="step-description">
            {description}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(icon: str, value: int, label: str, color: str = 'primary'):
    """
    Render a metric card with icon, value and label
    
    Args:
        icon: FontAwesome icon name (without 'fa-' prefix)
        value: Numeric value to display
        label: Label text
        color: Color theme (primary, success, danger, warning)
    """
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon" style="color: var(--{color});">
            <i class="fas fa-{icon}"></i>
        </div>
        <div class="metric-value">{value:,}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_statistics(df_stats: pd.DataFrame):
    """
    Render statistics overview with 4 metric cards
    
    Args:
        df_stats: DataFrame containing processed results
    """
    matched = (df_stats['Kode Material'] != '-').sum()
    unmatched = (df_stats['Kode Material'] == '-').sum()
    pln_count = (df_stats['Jumlah Material Gudang (PLN)'] > 0).sum()
    
    st.markdown("### Ringkasan Hasil", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card('box', len(df_stats), 'Total Material', 'primary')
    
    with col2:
        render_metric_card('check-circle', matched, 'Cocok', 'success')
    
    with col3:
        render_metric_card('times-circle', unmatched, 'Tidak Cocok', 'danger')
    
    with col4:
        render_metric_card('building', pln_count, 'Material PLN', 'warning')
    
    st.markdown("<br>", unsafe_allow_html=True)


def create_download_section(edited_df: pd.DataFrame, display_name: str):
    """
    Create download section with Excel and CSV buttons
    
    Args:
        edited_df: DataFrame to download
        display_name: Name to use in filename
    """
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### <i class='fas fa-download icon'></i>Unduh Hasil", unsafe_allow_html=True)
    st.info("Unduh data yang telah diproses dalam format Excel atau CSV")
    
    col_dl1, col_dl2 = st.columns([1, 1])
    
    with col_dl1:
        # Export Excel
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            edited_df.to_excel(writer, index=False, sheet_name=display_name[:31])
        
        st.download_button(
            "Download Excel",
            towrite.getvalue(),
            f"SOSYS_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )
    
    with col_dl2:
        # Export CSV
        csv_data = edited_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv_data,
            f"SOSYS_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width='stretch'
        )


def prepare_dataframe_for_display(df: pd.DataFrame, numeric_columns: list) -> pd.DataFrame:
    """
    Prepare DataFrame for display by formatting numeric columns
    
    Args:
        df: DataFrame to prepare
        numeric_columns: List of column names to format as numeric
    
    Returns:
        Prepared DataFrame
    """
    df_display = df.copy()
    
    for col in numeric_columns:
        if col in df_display.columns:
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce').replace(0, None)
    
    return df_display


def get_column_config() -> Dict[str, Any]:
    """
    Get column configuration for st.data_editor
    
    Returns:
        Dictionary with column configuration
    """
    return {
        "Kode Material": st.column_config.Column(
            disabled=True,
            help="Kode material yang terdaftar pada master database (read-only)"
        ),
        "Tipe Material": st.column_config.Column(
            disabled=True,
            help="Tipe material dari master database (read-only)"
        ),
        "Nama Material": st.column_config.TextColumn(
            help="Nama material dari vendor"
        ),
    }


def render_footer():
    """Render the footer"""
    st.markdown("""
    <div class="footer">
        <i class="fas fa-bolt"></i> SOSYS Material Automation v2.1 | 
        Built with Streamlit | 
        <i class="fas fa-code"></i> Powered by AI
    </div>
    """, unsafe_allow_html=True)