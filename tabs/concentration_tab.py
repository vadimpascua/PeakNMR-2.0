import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import analysis.concentration as concentration_analysis
import globals
import gui

def create_concentration_tab(tab_control):
    """Create the concentration analysis tab."""
    tab = gui.create_themed_frame(tab_control)
    tab_control.add(tab, text="🧪 Concentrations")
    
    conc_frame = gui.create_themed_frame(tab)
    conc_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Input section
    input_frame = gui.create_themed_labelframe(conc_frame, text="Concentration Parameters", padding=15)
    input_frame.pack(fill='x', pady=(0, 15))

    gui.create_themed_label(input_frame, text="Reference concentration (TSP/DSS):").grid(row=0, column=0, sticky='w', pady=5)
    concentration_entry = ttk.Entry(input_frame, width=15)
    concentration_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
    concentration_entry.insert(0, "0")
    gui.create_themed_label(input_frame, text="μM").grid(row=0, column=2, sticky='w', pady=5, padx=(5, 0))

    # Control buttons
    control_frame = gui.create_themed_frame(conc_frame)
    control_frame.pack(fill='x', pady=10)

    process_conc_btn = gui.create_themed_button(control_frame, text="🚀 Calculate Concentrations", 
                                 command=lambda: process_concentrations(concentration_entry, concentration_table))
    process_conc_btn.pack(side='left', padx=(0, 10))

    export_conc_btn = gui.create_themed_button(control_frame, text="💾 Export to Excel", 
                                command=export_concentrations)
    export_conc_btn.pack(side='left')

    # Results table
    results_frame = gui.create_themed_labelframe(conc_frame, text="Concentration Results", padding=15)
    results_frame.pack(fill='both', expand=True, pady=(15, 0))

    # Create results table
    concentration_table = ttk.Treeview(results_frame, show="headings", height=15)
    concentration_table.pack(fill='both', expand=True)

    # Add scrollbar
    conc_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=concentration_table.yview)
    concentration_table.configure(yscrollcommand=conc_scrollbar.set)
    conc_scrollbar.pack(side='right', fill='y')

    # Description
    desc_frame = gui.create_themed_labelframe(conc_frame, text="About", padding=15)
    desc_frame.pack(fill='x', pady=(15, 0))

    description_text = """This module calculates absolute concentrations using the internal reference standard.
Areas are calculated by simple summation of intensity values within defined peak regions."""
    
    gui.create_themed_label(desc_frame, text=description_text, justify='left').pack(anchor='w')
    
    return tab

def process_concentrations(concentration_entry, concentration_table):
    """Process concentration calculations."""
    try:
        tsp_concentration = float(concentration_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid concentration value.")
        return

    results = concentration_analysis.calculate_concentrations(tsp_concentration)
    if results:
        globals.concentration_results, results_area = results
        display_concentration_results(concentration_table)

def display_concentration_results(concentration_table):
    """Display concentration results in the table."""
    # Clear the table
    for row in concentration_table.get_children():
        concentration_table.delete(row)
    
    # Group by sample
    samples = {}
    for result in globals.concentration_results:
        sample = result["Sample"]
        if sample not in samples:
            samples[sample] = {}
        samples[sample][result["Peak"]] = result["Concentration"]
    
    # Populate table with natural sorting
    if samples:
        # Get peaks and sort naturally
        all_peaks = set()
        for sample_data in samples.values():
            all_peaks.update(sample_data.keys())
        
        # Natural sort function
        def natural_sort_key(s):
            import re
            return [int(text) if text.isdigit() else text.lower()
                   for text in re.split('([0-9]+)', s)]
        
        peaks_sorted = sorted(all_peaks, key=natural_sort_key)
        
        # Configure columns
        concentration_table["columns"] = ["Sample"] + peaks_sorted
        for col in concentration_table["columns"]:
            concentration_table.heading(col, text=col)
            concentration_table.column(col, width=100)
        
        # Sort samples naturally as well
        samples_sorted = sorted(samples.keys(), key=natural_sort_key)
        
        for sample in samples_sorted:
            values = [sample]
            for peak in peaks_sorted:
                values.append(f"{samples[sample].get(peak, 0):.6f}")
            concentration_table.insert("", "end", values=values)

def export_concentrations():
    """Export concentration results to Excel."""
    if not globals.concentration_results:
        messagebox.showerror("Error", "No concentration results to export.")
        return
        
    filename = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save concentration results as"
    )
    
    if filename:
        # Create DataFrames
        df_c = pd.DataFrame(globals.concentration_results).pivot(index="Sample", columns="Peak", values="Concentration")
        
        with pd.ExcelWriter(filename) as writer:
            df_c.to_excel(writer, sheet_name="Concentrations")
        messagebox.showinfo("Success", f"Concentration results saved to {filename}")