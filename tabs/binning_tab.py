import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import analysis.binning as binning_analysis
import globals
import gui

def create_binning_tab(tab_control):
    """Create the binning analysis tab."""
    tab = gui.create_themed_frame(tab_control)
    tab_control.add(tab, text="📈 Binning")
    
    bin_frame = gui.create_themed_frame(tab)
    bin_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Input section
    bin_input_frame = gui.create_themed_labelframe(bin_frame, text="Binning Parameters", padding=15)
    bin_input_frame.pack(fill='x', pady=(0, 15))

    gui.create_themed_label(bin_input_frame, text="Bin step size:").grid(row=0, column=0, sticky='w', pady=5)
    binning_entry = ttk.Entry(bin_input_frame, width=15)
    binning_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
    binning_entry.insert(0, "0.05")
    gui.create_themed_label(bin_input_frame, text="ppm").grid(row=0, column=2, sticky='w', pady=5, padx=(5, 0))

    # Control buttons
    bin_control_frame = gui.create_themed_frame(bin_frame)
    bin_control_frame.pack(fill='x', pady=10)

    process_bin_btn = gui.create_themed_button(bin_control_frame, text="🚀 Perform Binning", 
                                command=lambda: process_binning(binning_entry, binning_table))
    process_bin_btn.pack(side='left', padx=(0, 10))

    export_bin_btn = gui.create_themed_button(bin_control_frame, text="💾 Export to Excel", 
                               command=export_binning)
    export_bin_btn.pack(side='left')

    # Results table
    bin_results_frame = gui.create_themed_labelframe(bin_frame, text="Binning Results", padding=15)
    bin_results_frame.pack(fill='both', expand=True, pady=(15, 0))

    # Create results table
    binning_table = ttk.Treeview(bin_results_frame, show="headings", height=15)
    binning_table.pack(fill='both', expand=True)

    # Add scrollbar
    bin_scrollbar = ttk.Scrollbar(bin_results_frame, orient="vertical", command=binning_table.yview)
    binning_table.configure(yscrollcommand=bin_scrollbar.set)
    bin_scrollbar.pack(side='right', fill='y')

    # Description
    bin_desc_frame = gui.create_themed_labelframe(bin_frame, text="About", padding=15)
    bin_desc_frame.pack(fill='x', pady=(15, 0))

    description_text = """This module performs uniform binning across the entire spectrum.
The spectrum is divided into bins of specified size and area is calculated for each bin."""
    
    gui.create_themed_label(bin_desc_frame, text=description_text, justify='left').pack(anchor='w')
    
    return tab

def process_binning(binning_entry, binning_table):
    """Process binning analysis."""
    try:
        bin_size = float(binning_entry.get())
    except:
        messagebox.showerror("Error", "Invalid step size.")
        return

    globals.binning_results = binning_analysis.perform_binning(bin_size)
    if globals.binning_results is not None:
        display_binning_results(binning_table)

def display_binning_results(binning_table):
    """Display binning results in the table."""
    # Clear the table
    for row in binning_table.get_children():
        binning_table.delete(row)
    
    if globals.binning_results is not None:
        # Get column names (bins) and sort numerically
        columns = list(globals.binning_results.columns)
        
        # Sort bins numerically by converting to float
        columns_sorted = sorted(columns, key=lambda x: float(x))
        
        # Configure table columns
        binning_table["columns"] = ["Sample"] + columns_sorted
        for col in binning_table["columns"]:
            binning_table.heading(col, text=col)
            binning_table.column(col, width=80)
        
        # Natural sort function for samples
        def natural_sort_key(s):
            import re
            return [int(text) if text.isdigit() else text.lower()
                   for text in re.split('([0-9]+)', s)]
        
        # Sort samples naturally
        samples_sorted = sorted(globals.binning_results.index, key=natural_sort_key)
        
        # Populate table (show first 20 bins to avoid overcrowding)
        display_columns = ["Sample"] + columns_sorted[:20]
        binning_table["columns"] = display_columns
        
        for sample in samples_sorted:
            values = [sample]
            for col in columns_sorted[:20]:
                values.append(f"{globals.binning_results.loc[sample, col]:.6f}")
            binning_table.insert("", "end", values=values)

def export_binning():
    """Export binning results to Excel."""
    if globals.binning_results is None:
        messagebox.showerror("Error", "No binning results to export.")
        return
        
    filename = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save binning results as"
    )
    
    if filename:
        with pd.ExcelWriter(filename) as writer:
            globals.binning_results.to_excel(writer)
        messagebox.showinfo("Success", f"Binning results saved to {filename}")