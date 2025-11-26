import numpy as np
from tkinter import messagebox
import file_io
import globals

def calculate_integrals():
    """Calculate integrals for all peak regions in all spectra."""
    if not globals.selected_pdata_dirs:
        messagebox.showerror("Error", "Select a dataset first.")
        return []
        
    if globals.peak_limits.empty:
        messagebox.showerror("Error", "No peak limits loaded.")
        return []

    integration_results = []
    
    for root_dir in globals.selected_pdata_dirs:
        pdata_dirs = file_io.find_pdata_directories(root_dir)

        for pdata_dir in pdata_dirs:
            try:
                # Load spectrum data
                import nmrglue as ng
                dic, data = ng.bruker.read_pdata(pdata_dir, scale_data=True)
                udic = ng.bruker.guess_udic(dic, data)
                uc = ng.fileiobase.uc_from_udic(udic)
                ppm_scale = uc.ppm_scale()
                
                sample_name = file_io.get_sample_name(pdata_dir)
                
                # Calculate integrals for each peak region
                for _, row in globals.peak_limits.iterrows():
                    name = row["Peak identity"]
                    start = row["ppm start"]
                    end = row["ppm end"]
                    
                    integral = calculate_peak_area(ppm_scale, data, start, end)
                    
                    integration_results.append({
                        "Sample": sample_name,
                        "Peak": name,
                        "Start (ppm)": start,
                        "End (ppm)": end,
                        "Integral": integral,
                        "File Path": pdata_dir
                    })
    
            except Exception as e:
                continue
    
    return integration_results

def calculate_peak_area(ppm_scale, data, start_ppm, end_ppm):
    """Calculate peak area by summation."""
    s = np.abs(ppm_scale - start_ppm).argmin()
    e = np.abs(ppm_scale - end_ppm).argmin()
    if s > e: 
        s, e = e, s
    return data[s:e+1].sum()