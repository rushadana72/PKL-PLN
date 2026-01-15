import pandas as pd
import pprint

def update_master_script(uploaded_file):
    """
    Fungsi untuk membaca CSV dan menulis ulang file master_data.py
    """
    try:
        # Baca file CSV (menangani berbagai encoding)
        try:
            df = pd.read_csv(uploaded_file, sep=';', encoding='cp1252')
        except:
            df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
        
        # Ambil data: Kolom 0 (Nama), 1 (Kode), 2 (Tipe)
        new_data = {}
        for _, row in df.iterrows():
            nama_key = str(row.iloc[0]).strip()
            new_data[nama_key] = {
                'Kode': row.iloc[1],
                'Tipe': row.iloc[2]
            }
        
        # Tulis secara fisik ke file master_data.py
        with open("master_data.py", "w", encoding="utf-8") as f:
            f.write("# File ini otomatis diperbarui oleh sistem\n")
            f.write("MASTER_LIST = ")
            f.write(pprint.pformat(new_data, indent=4))
        
        return True
    except Exception as e:
        print(f"Error saat update master: {e}")
        return False