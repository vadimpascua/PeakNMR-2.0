import nmrglue as ng
import numpy as np
import os
import zipfile
import pandas as pd
from tkinter import messagebox
import globals

def find_pdata_directories(root_dir):
    """Find all Bruker pdata/1 directories recursively."""
    pdata_dirs = []
    for dirpath, _, filenames in os.walk(root_dir):
        if "/pdata/1" in dirpath.replace("\\", "/"):
            pdata_dirs.append(dirpath)
    return pdata_dirs

def load_spectra_from_directory(root_dir):
    """Load NMR spectra from Bruker pdata directories."""
    spectra = []
    pdata_dirs = find_pdata_directories(root_dir)

    for pdata_dir in pdata_dirs:
        try:
            dic, data = ng.bruker.read_pdata(pdata_dir, scale_data=True)
            udic = ng.bruker.guess_udic(dic, data)
            uc = ng.fileiobase.uc_from_udic(udic)
            ppm_scale = uc.ppm_scale()
            sample_name = get_sample_name(pdata_dir)
            spectra.append((ppm_scale, data, sample_name, pdata_dir))
        except OSError as e:
            print(f"Error loading {pdata_dir}: {e}")
            continue

    return natural_sort_spectra(spectra)

def natural_sort_spectra(spectra_list):
    """Sort spectra naturally by sample name."""
    def natural_sort_key(s):
        import re
        return [int(text) if text.isdigit() else text.lower()
               for text in re.split('([0-9]+)', s[2])]
    
    return sorted(spectra_list, key=natural_sort_key)

def extract_zip_file(zip_path):
    """Extract zip file and return extraction directory."""
    if not zip_path.endswith(".zip"):
        messagebox.showerror("Error", "This is not a .zip file.")
        return None
        
    # Create a unique extraction directory
    import tempfile
    extract_dir = tempfile.mkdtemp(prefix="nmr_extracted_")
    
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)
    return extract_dir

def load_peak_limits(file_path):
    """Load peak limits from Excel file."""
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot read peak_limits.xlsx:\n{e}")
        return None

def get_sample_name(pdata_dir):
    """Extract sample name from pdata directory path."""
    return os.path.basename(os.path.dirname(os.path.dirname(pdata_dir)))

def load_bruker_data(pdata_dir):
    """Load Bruker data from pdata directory."""
    try:
        dic, data = ng.bruker.read_pdata(pdata_dir, scale_data=True)
        return dic, data
    except Exception as e:
        print(f"Error loading Bruker data from {pdata_dir}: {e}")
        return None, None

def get_spectrum_info(dic, data, pdata_dir):
    """Get spectrum information from Bruker data."""
    try:
        udic = ng.bruker.guess_udic(dic, data)
        uc = ng.fileiobase.uc_from_udic(udic)
        ppm_scale = uc.ppm_scale()
        sample_name = get_sample_name(pdata_dir)
        return ppm_scale, sample_name
    except Exception as e:
        print(f"Error getting spectrum info: {e}")
        return None, None