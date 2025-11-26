import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import analysis.integration as integration_analysis
import globals
import gui

def create_integration_tab(tab_control):
    """Create the integration analysis tab."""
    tab = gui.create_themed_frame(tab_control)
    tab_control.add(tab, text="📉 Integrations")
    
    int_frame = gui.create_themed_frame(tab)
    int_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Control section
    int_control_frame = gui.create_themed_labelframe(int_frame, text="Integration Controls", padding=15)
    int_control_frame.pack(fill='x', pady=(0, 15))

    # Process button
    process_int_btn = gui.create_themed_button(int_control_frame, text="🧮 Calculate Integrals", 
                               command=lambda: process_integrations(integration_table))
    process_int_btn.grid(row=0, column=0, sticky='w', padx=(0, 10))

    # Export button
    export_int_btn = gui.create_themed_button(int_control_frame, text="💾 Export to Excel", 
                              command=export_integrations)
    export_int_btn.grid(row=0, column=1, sticky='w')

    # Results table
    table_frame = gui.create_themed_labelframe(int_frame, text="Integration Results", padding=15)
    table_frame.pack(fill='both', expand=True, pady=(0, 15))

    # Configure grid weights for resizing
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    # Create results table
    columns = ("Sample", "Peak", "Start (ppm)", "End (ppm)", "Integral")
    integration_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    # Define headings
    integration_table.heading("Sample", text="Sample")
    integration_table.heading("Peak", text="Peak")
    integration_table.heading("Start (ppm)", text="Start (ppm)")
    integration_table.heading("End (ppm)", text="End (ppm)")
    integration_table.heading("Integral", text="Integral")

    # Set column widths
    integration_table.column("Sample", width=150)
    integration_table.column("Peak", width=150)
    integration_table.column("Start (ppm)", width=120)
    integration_table.column("End (ppm)", width=120)
    integration_table.column("Integral", width=150)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=integration_table.yview)
    integration_table.configure(yscrollcommand=scrollbar.set)

    # Pack table and scrollbar
    integration_table.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Description
    int_desc_frame = gui.create_themed_labelframe(int_frame, text="About", padding=15)
    int_desc_frame.pack(fill='x')

    description_text = """This module calculates integrals for defined peak regions using simple summation.
Results can be exported to Excel for further analysis."""
    
    gui.create_themed_label(int_desc_frame, text=description_text, justify='left').pack(anchor='w')
    
    return tab

def process_integrations(integration_table):
    """Process integration calculations."""
    globals.integration_results = integration_analysis.calculate_integrals()
    if globals.integration_results:
        display_integration_results(integration_table)

def display_integration_results(integration_table):
    """Display integration results in the table."""
    # Clear the table
    for row in integration_table.get_children():
        integration_table.delete(row)
    
    # Natural sort function
    def natural_sort_key(s):
        import re
        return [int(text) if text.isdigit() else text.lower()
               for text in re.split('([0-9]+)', s)]
    
    # Sort results by sample name naturally
    sorted_results = sorted(globals.integration_results, key=lambda x: natural_sort_key(x["Sample"]))
    
    # Populate with sorted results
    for result in sorted_results:
        integration_table.insert("", "end", values=(
            result["Sample"],
            result["Peak"],
            f"{result['Start (ppm)']:.3f}",
            f"{result['End (ppm)']:.3f}",
            f"{result['Integral']:.6f}"
        ))

def export_integrations():
    """Export integration results to Excel."""
    if not globals.integration_results:
        messagebox.showerror("Error", "No integration results to export.")
        return
        
    # Create DataFrame and pivot to have samples as rows and peaks as columns
    df = pd.DataFrame(globals.integration_results)
    df_pivot = df.pivot(index="Sample", columns="Peak", values="Integral")
    
    # Export to Excel
    filename = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save integration results as"
    )
    
    if filename:
        with pd.ExcelWriter(filename) as writer:
            df_pivot.to_excel(writer, sheet_name="Integrals")
            df.to_excel(writer, sheet_name="Detailed Results")
        messagebox.showinfo("Success", f"Integration results saved to {filename}")