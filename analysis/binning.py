import numpy as np
import pandas as pd
from tkinter import messagebox
import file_io
import globals

def perform_binning(bin_size):
    """Perform uniform binning on all spectra."""
    if not globals.selected_pdata_dirs:
        messagebox.showerror("Error", "Select dataset first.")
        return None

    all_ppm_scales = []
    PDATA = []
    sample_names = []

    for root_dir in globals.selected_pdata_dirs:
        for pdata_dir in file_io.find_pdata_directories(root_dir):
            try:
                # Load spectrum data
                import nmrglue as ng
                dic, data = ng.bruker.read_pdata(pdata_dir, scale_data=True)
                udic = ng.bruker.guess_udic(dic, data)
                uc = ng.fileiobase.uc_from_udic(udic)
                ppm_scale = uc.ppm_scale()
                sample_name = file_io.get_sample_name(pdata_dir)

                all_ppm_scales.append(ppm_scale)
                PDATA.append((pdata_dir, data))
                sample_names.append(sample_name)
            except:
                continue

    if not all_ppm_scales:
        messagebox.showerror("Error", "No spectra found to process.")
        return None

    # Calculate global ppm range
    minppm = min([p.min() for p in all_ppm_scales])
    maxppm = max([p.max() for p in all_ppm_scales])

    # Create bins
    bins = np.arange(minppm, maxppm, bin_size)

    # Perform binning
    matrix = []

    for (pdata_dir, data), ppm in zip(PDATA, all_ppm_scales):
        idx = np.digitize(ppm, bins)
        binned = [data[idx == i].sum() for i in range(1, len(bins))]
        matrix.append(binned)

    # Create DataFrame
    df = pd.DataFrame(matrix, columns=[f"{bins[i]:.3f}" for i in range(len(bins)-1)])
    df.index = sample_names
    
    return df