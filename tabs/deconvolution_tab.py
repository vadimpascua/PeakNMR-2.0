import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import pandas as pd
import analysis.deconvolution as deconvolution_analysis
import globals
import gui

def create_deconvolution_tab(tab_control):
    """Create the spectral deconvolution tab."""
    tab = gui.create_themed_frame(tab_control)
    tab_control.add(tab, text="📊 Spectral Deconvolution")
    
    deconv_frame = gui.create_themed_frame(tab)
    deconv_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Left panel - controls and spectra list
    deconv_left_panel = gui.create_themed_frame(deconv_frame)
    deconv_left_panel.pack(side='left', fill='y', padx=(0, 10))

    # Spectra selection
    deconv_spectra_frame = gui.create_themed_labelframe(deconv_left_panel, text="Spectrum Selection", padding=15)
    deconv_spectra_frame.pack(fill='x', pady=(0, 15))

    gui.create_themed_label(deconv_spectra_frame, text="Select spectrum:").pack(anchor='w', pady=(0, 5))
    deconvolution_spectra_listbox = tk.Listbox(deconv_spectra_frame, height=8, width=25)
    gui.configure_listbox(deconvolution_spectra_listbox)
    deconvolution_spectra_listbox.pack(fill='x', pady=5)
    deconvolution_spectra_listbox.bind('<<ListboxSelect>>', 
                                      lambda event: on_deconvolution_spectrum_select(event, deconv_fig, deconv_canvas))

    # Deconvolution parameters
    deconv_params_frame = gui.create_themed_labelframe(deconv_left_panel, text="Deconvolution Parameters", padding=15)
    deconv_params_frame.pack(fill='x', pady=(15, 0))

    # Start PPM
    gui.create_themed_label(deconv_params_frame, text="Start PPM:").grid(row=0, column=0, sticky='w', pady=2)
    deconv_start_entry = ttk.Entry(deconv_params_frame, width=10)
    deconv_start_entry.grid(row=0, column=1, sticky='w', pady=2, padx=(5, 0))
    deconv_start_entry.insert(0, "1.0")

    # End PPM
    gui.create_themed_label(deconv_params_frame, text="End PPM:").grid(row=1, column=0, sticky='w', pady=2)
    deconv_end_entry = ttk.Entry(deconv_params_frame, width=10)
    deconv_end_entry.grid(row=1, column=1, sticky='w', pady=2, padx=(5, 0))
    deconv_end_entry.insert(0, "2.0")

    # Number of peaks
    gui.create_themed_label(deconv_params_frame, text="Number of peaks:").grid(row=2, column=0, sticky='w', pady=2)
    deconv_peaks_entry = ttk.Entry(deconv_params_frame, width=10)
    deconv_peaks_entry.grid(row=2, column=1, sticky='w', pady=2, padx=(5, 0))
    deconv_peaks_entry.insert(0, "3")

    # Max iterations
    gui.create_themed_label(deconv_params_frame, text="Max iterations:").grid(row=3, column=0, sticky='w', pady=2)
    deconv_iterations_entry = ttk.Entry(deconv_params_frame, width=10)
    deconv_iterations_entry.grid(row=3, column=1, sticky='w', pady=2, padx=(5, 0))
    deconv_iterations_entry.insert(0, "2000")

    # Baseline window size
    gui.create_themed_label(deconv_params_frame, text="Baseline window:").grid(row=4, column=0, sticky='w', pady=2)
    baseline_window_entry = ttk.Entry(deconv_params_frame, width=10)
    baseline_window_entry.grid(row=4, column=1, sticky='w', pady=2, padx=(5, 0))
    baseline_window_entry.insert(0, "51")
    #gui.create_themed_label(deconv_params_frame, text="(odd number)").grid(row=4, column=2, sticky='w', pady=2, padx=(5, 0))

    # Auto-detect button
    auto_detect_btn = gui.create_themed_button(deconv_params_frame, text="🔍 Auto-detect Peaks", 
                                command=lambda: auto_detect_peak_count(deconvolution_spectra_listbox, 
                                                                      deconv_start_entry, deconv_end_entry, 
                                                                      deconv_peaks_entry))
    auto_detect_btn.grid(row=5, column=0, columnspan=2, sticky='w', pady=(10, 5))

    # Control buttons
    deconv_control_frame = gui.create_themed_frame(deconv_left_panel)
    deconv_control_frame.pack(fill='x', pady=15)

    deconv_btn = gui.create_themed_button(deconv_control_frame, text="🔍 Deconvolve Peaks", 
                           command=lambda: perform_spectral_deconvolution(
                               deconvolution_spectra_listbox, deconv_start_entry, deconv_end_entry,
                               deconv_peaks_entry, deconv_iterations_entry, baseline_window_entry,
                               deconvolution_table, deconv_fig, deconv_canvas))
    deconv_btn.pack(side='left', padx=(0, 10))

    export_deconv_btn = gui.create_themed_button(deconv_control_frame, text="💾 Export Results", 
                                  command=export_deconvolution_results)
    export_deconv_btn.pack(side='left')

    # Results table
    deconv_results_frame = gui.create_themed_labelframe(deconv_left_panel, text="Deconvolution Results", padding=15)
    deconv_results_frame.pack(fill='both', expand=True, pady=(15, 0))

    # Create results table with additional columns
    deconvolution_table = ttk.Treeview(deconv_results_frame, 
                                      columns=("Peak", "Center_PPM", "Amplitude", "Width", "Integral", "Integration_Range"), 
                                      show="headings", height=10)
    deconvolution_table.heading("Peak", text="Peak")
    deconvolution_table.heading("Center_PPM", text="Center (ppm)")
    deconvolution_table.heading("Amplitude", text="Amplitude")
    #deconvolution_table.heading("Width", text="FWHM") #  Cool but not typically useful for a user
    deconvolution_table.heading("Integral", text="Integral")
    deconvolution_table.heading("Integration_Range", text="Integration Range")
    deconvolution_table.column("Peak", width=80)
    deconvolution_table.column("Center_PPM", width=100)
    #deconvolution_table.column("Amplitude", width=100) # Same thing here, not very useful for the user
    deconvolution_table.column("Width", width=80)
    deconvolution_table.column("Integral", width=120)
    deconvolution_table.column("Integration_Range", width=120)
    deconvolution_table.pack(fill='both', expand=True)

    # Right panel - deconvolution plot
    deconv_right_panel = gui.create_themed_frame(deconv_frame)
    deconv_right_panel.pack(side='right', fill='both', expand=True)

    # Create matplotlib figure for deconvolution
    deconv_fig = plt.Figure(figsize=(10, 8), dpi=100)
    deconv_canvas = FigureCanvasTkAgg(deconv_fig, master=deconv_right_panel)
    deconv_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Toolbar for deconvolution plot
    deconv_toolbar_frame = gui.create_themed_frame(deconv_right_panel)
    deconv_toolbar_frame.pack(side=tk.TOP, fill=tk.X)
    deconv_toolbar = NavigationToolbar2Tk(deconv_canvas, deconv_toolbar_frame)
    deconv_toolbar.update()

    # Initial plot
    setup_initial_deconv_plot(deconv_fig, deconv_canvas)

    # Description
    deconv_desc_frame = gui.create_themed_labelframe(deconv_left_panel, text="About Spectral Deconvolution", padding=15)
    deconv_desc_frame.pack(fill='x', pady=(15, 0))

    description_text = """This module mathematically separates overlapping peaks using Gaussian fitting.

Key features:
• Advanced baseline estimation using Savitzky-Golay filter
• Proper integration with shaded regions showing integrated areas
• Individual peak fitting with amplitude, width, and integral calculations
• Visual feedback showing baseline and integration boundaries

Instructions:
1. Select a spectrum
2. Define the ppm region to analyze
3. Specify number of expected peaks
4. Run deconvolution and review results

Tips for better results:
• Use 'Auto-detect Peaks' for initial guess
• Ensure region boundaries properly contain peaks
• Shaded areas show what is being integrated
• Green numbers show calculated integrals"""
    
    gui.create_themed_label(deconv_desc_frame, text=description_text, justify='left', font=('Segoe UI', 9)).pack(anchor='w')
    
    # Register for spectra updates
    globals.add_event_listener('spectra_updated', 
                              lambda spectra: update_deconvolution_spectra_list(deconvolution_spectra_listbox))
    
    return tab, deconvolution_spectra_listbox

def update_deconvolution_spectra_list(deconvolution_spectra_listbox):
    """Update the deconvolution spectra listbox."""
    deconvolution_spectra_listbox.delete(0, tk.END)
    
    if not globals.spectra:
        return
        
    for i, (ppm_scale, data, sample_name, pdata_dir) in enumerate(globals.spectra):
        deconvolution_spectra_listbox.insert(tk.END, sample_name)

def on_deconvolution_spectrum_select(event, deconv_fig, deconv_canvas):
    """Handle spectrum selection in deconvolution tab."""
    selection = event.widget.curselection()
    if selection and globals.spectra:
        index = selection[0]
        if index < len(globals.spectra):
            ppm_scale, data, sample_name, pdata_dir = globals.spectra[index]
            plot_deconvolution_spectrum(ppm_scale, data, sample_name, deconv_fig, deconv_canvas)

def plot_deconvolution_spectrum(ppm_scale, data, sample_name, deconv_fig, deconv_canvas):
    """Plot spectrum in deconvolution tab."""
    deconv_fig.clear()
    ax = deconv_fig.add_subplot(111)
    
    gui.setup_plot_style(ax)
    
    # Plot spectrum
    ax.plot(ppm_scale, data, color=gui.Theme.SPECTRUM_COLORS[0], linewidth=1, label=sample_name)
    
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.set_title(f"Spectrum: {sample_name}")
    ax.invert_xaxis()
    ax.legend()
    deconv_canvas.draw()

def auto_detect_peak_count(deconvolution_spectra_listbox, deconv_start_entry, deconv_end_entry, deconv_peaks_entry):
    """Auto-detect optimal number of peaks in selected region."""
    selection = deconvolution_spectra_listbox.curselection()
    if not selection:
        messagebox.showinfo("Info", "Please select a spectrum first.")
        return
    
    try:
        start_ppm = float(deconv_start_entry.get())
        end_ppm = float(deconv_end_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please set valid region boundaries first.")
        return
    
    # Get selected spectrum
    index = selection[0]
    if index >= len(globals.spectra):
        return
        
    ppm_scale, data, sample_name, pdata_dir = globals.spectra[index]
    
    # Extract region
    start_idx = np.abs(ppm_scale - start_ppm).argmin()
    end_idx = np.abs(ppm_scale - end_ppm).argmin()
    if start_idx > end_idx: 
        start_idx, end_idx = end_idx, start_idx
    
    x_data = ppm_scale[start_idx:end_idx+1]
    y_data = data[start_idx:end_idx+1]
    
    optimal_peaks = deconvolution_analysis.find_optimal_peak_count(x_data, y_data)
    
    # Update the peaks entry
    deconv_peaks_entry.delete(0, tk.END)
    deconv_peaks_entry.insert(0, str(optimal_peaks))
    
    messagebox.showinfo("Auto-detection", f"Suggested number of peaks: {optimal_peaks}")

def perform_spectral_deconvolution(deconvolution_spectra_listbox, deconv_start_entry, deconv_end_entry,
                                  deconv_peaks_entry, deconv_iterations_entry, baseline_window_entry,
                                  deconvolution_table, deconv_fig, deconv_canvas):
    """Perform spectral deconvolution on selected region."""
    selection = deconvolution_spectra_listbox.curselection()
    if not selection:
        messagebox.showinfo("Info", "Please select a spectrum first.")
        return
    
    # Get deconvolution parameters
    try:
        start_ppm = float(deconv_start_entry.get())
        end_ppm = float(deconv_end_entry.get())
        num_peaks = int(deconv_peaks_entry.get())
        max_iterations = int(deconv_iterations_entry.get())
        baseline_window = int(baseline_window_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric parameters.")
        return
    
    # Get selected spectrum
    index = selection[0]
    if index >= len(globals.spectra):
        return
        
    ppm_scale, data, sample_name, pdata_dir = globals.spectra[index]
    
    # Perform deconvolution
    success = deconvolution_analysis.perform_deconvolution(
        ppm_scale, data, sample_name, start_ppm, end_ppm, num_peaks, max_iterations,
        deconv_fig, deconv_canvas)
    
    if success:
        display_deconvolution_results(deconvolution_table)
        valid_peaks = len(globals.deconvolution_results)
        messagebox.showinfo("Success", f"Deconvolution completed! Found {valid_peaks} valid peaks.\n\nIntegration areas are shown as shaded regions on the plot.")

def display_deconvolution_results(deconvolution_table):
    """Display deconvolution results in the table."""
    # Clear the table
    for row in deconvolution_table.get_children():
        deconvolution_table.delete(row)
    
    # Populate with results
    for result in globals.deconvolution_results:
        integration_range = f"{result.get('Integration_Start_PPM', 0):.3f}-{result.get('Integration_End_PPM', 0):.3f}"
        deconvolution_table.insert("", "end", values=(
            result["Peak"],
            f"{result['Center_PPM']:.4f}",
            f"{result['Amplitude']:.2e}",
            f"{result['Width']:.4f}",
            f"{result['Integral']:.2e}",
            integration_range
        ))

def export_deconvolution_results():
    """Export deconvolution results to Excel."""
    if not globals.deconvolution_results:
        messagebox.showerror("Error", "No deconvolution results to export.")
        return
        
    filename = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save deconvolution results as"
    )
    
    if filename:
        df = pd.DataFrame(globals.deconvolution_results)
        with pd.ExcelWriter(filename) as writer:
            df.to_excel(writer, sheet_name="Deconvolution Results", index=False)
        messagebox.showinfo("Success", f"Deconvolution results saved to {filename}")

def setup_initial_deconv_plot(deconv_fig, deconv_canvas):
    """Set up the initial empty plot for deconvolution."""
    ax = deconv_fig.add_subplot(111)
    gui.setup_plot_style(ax)
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.invert_xaxis()
    ax.set_title("Select a spectrum for deconvolution")
    deconv_canvas.draw()