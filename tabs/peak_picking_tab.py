import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import pandas as pd
import analysis.peak_picking as peak_picking_analysis
import globals
import gui

def create_peak_picking_tab(tab_control):
    """Create the peak picking analysis tab."""
    tab = gui.create_themed_frame(tab_control)
    tab_control.add(tab, text="🔍 Peak Picking")
    
    peak_picking_frame = gui.create_themed_frame(tab)
    peak_picking_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Left panel - controls and spectra list
    peak_left_panel = gui.create_themed_frame(peak_picking_frame)
    peak_left_panel.pack(side='left', fill='y', padx=(0, 10))

    # Spectra selection
    spectra_select_frame = gui.create_themed_labelframe(peak_left_panel, text="Spectrum Selection", padding=15)
    spectra_select_frame.pack(fill='x', pady=(0, 15))

    gui.create_themed_label(spectra_select_frame, text="Select spectrum:").pack(anchor='w', pady=(0, 5))
    peak_picking_spectra_listbox = tk.Listbox(spectra_select_frame, height=8, width=25)
    gui.configure_listbox(peak_picking_spectra_listbox)
    peak_picking_spectra_listbox.pack(fill='x', pady=5)
    peak_picking_spectra_listbox.bind('<<ListboxSelect>>', 
                                     lambda event: on_peak_picking_spectrum_select(event, peak_fig, peak_canvas))

    # Peak detection parameters
    params_frame = gui.create_themed_labelframe(peak_left_panel, text="Peak Detection Parameters", padding=15)
    params_frame.pack(fill='x', pady=(15, 0))

    # Height threshold
    gui.create_themed_label(params_frame, text="Height threshold:").grid(row=0, column=0, sticky='w', pady=2)
    peak_height_entry = ttk.Entry(params_frame, width=10)
    peak_height_entry.grid(row=0, column=1, sticky='w', pady=2, padx=(5, 0))
    peak_height_entry.insert(0, "5000000")

    # Minimum distance
    gui.create_themed_label(params_frame, text="Minimum distance:").grid(row=1, column=0, sticky='w', pady=2)
    peak_distance_entry = ttk.Entry(params_frame, width=10)
    peak_distance_entry.grid(row=1, column=1, sticky='w', pady=2, padx=(5, 0))
    peak_distance_entry.insert(0, "10")

    # Prominence
    gui.create_themed_label(params_frame, text="Prominence:").grid(row=2, column=0, sticky='w', pady=2)
    peak_prominence_entry = ttk.Entry(params_frame, width=10)
    peak_prominence_entry.grid(row=2, column=1, sticky='w', pady=2, padx=(5, 0))
    peak_prominence_entry.insert(0, "50000")

    # Baseline detection parameter
    gui.create_themed_label(params_frame, text="Baseline threshold:").grid(row=3, column=0, sticky='w', pady=2)
    peak_baseline_entry = ttk.Entry(params_frame, width=10)
    peak_baseline_entry.grid(row=3, column=1, sticky='w', pady=2, padx=(5, 0))
    peak_baseline_entry.insert(0, "0.01")
    gui.create_themed_label(params_frame, text="(fraction of peak height)").grid(row=3, column=2, sticky='w', pady=2, padx=(5, 0))

    # Underground peak removal parameters
    underground_frame = gui.create_themed_labelframe(peak_left_panel, text="Underground Peak Removal", padding=15)
    underground_frame.pack(fill='x', pady=(15, 0))

    # Intensity threshold
    gui.create_themed_label(underground_frame, text="Intensity threshold:").grid(row=0, column=0, sticky='w', pady=2)
    underground_intensity_entry = ttk.Entry(underground_frame, width=10)
    underground_intensity_entry.grid(row=0, column=1, sticky='w', pady=2, padx=(5, 0))
    underground_intensity_entry.insert(0, "100000")

    # Integral threshold
    gui.create_themed_label(underground_frame, text="Integral threshold:").grid(row=1, column=0, sticky='w', pady=2)
    underground_integral_entry = ttk.Entry(underground_frame, width=10)
    underground_integral_entry.grid(row=1, column=1, sticky='w', pady=2, padx=(5, 0))
    underground_integral_entry.insert(0, "10000")

    # Width threshold
    gui.create_themed_label(underground_frame, text="Width threshold:").grid(row=2, column=0, sticky='w', pady=2)
    underground_width_entry = ttk.Entry(underground_frame, width=10)
    underground_width_entry.grid(row=2, column=1, sticky='w', pady=2, padx=(5, 0))
    underground_width_entry.insert(0, "0.001")
    gui.create_themed_label(underground_frame, text="ppm").grid(row=2, column=2, sticky='w', pady=2, padx=(5, 0))

    # Underground removal buttons
    underground_control_frame = gui.create_themed_frame(underground_frame)
    underground_control_frame.grid(row=3, column=0, columnspan=3, sticky='w', pady=(10, 0))

    remove_underground_btn = gui.create_themed_button(underground_control_frame, text="🗑️ Remove Underground Peaks", 
                                       command=lambda: remove_underground_peaks(
                                           underground_intensity_entry, underground_integral_entry, 
                                           underground_width_entry, peak_picking_spectra_listbox,
                                           peak_picking_table, peak_fig, peak_canvas))
    remove_underground_btn.pack(side='left', padx=(0, 10))

    remove_underground_all_btn = gui.create_themed_button(underground_control_frame, text="🗑️ Remove From All Spectra", 
                                           command=lambda: remove_underground_peaks_all_spectra(
                                               underground_intensity_entry, underground_integral_entry, 
                                               underground_width_entry))
    remove_underground_all_btn.pack(side='left', padx=(0, 10))

    reset_underground_btn = gui.create_themed_button(underground_control_frame, text="🔄 Reset Parameters", 
                                      command=lambda: reset_underground_parameters(
                                          underground_intensity_entry, underground_integral_entry, 
                                          underground_width_entry))
    reset_underground_btn.pack(side='left')

    # Control buttons
    peak_control_frame = gui.create_themed_frame(peak_left_panel)
    peak_control_frame.pack(fill='x', pady=15)

    detect_peaks_btn = gui.create_themed_button(peak_control_frame, text="🔍 Detect Peaks", 
                                 command=lambda: auto_detect_peaks(
                                     peak_picking_spectra_listbox, peak_height_entry, peak_distance_entry,
                                     peak_prominence_entry, peak_baseline_entry, peak_picking_table,
                                     peak_fig, peak_canvas))
    detect_peaks_btn.pack(side='left', padx=(0, 10))

    detect_all_peaks_btn = gui.create_themed_button(peak_control_frame, text="🔍 Detect All Spectra", 
                                     command=detect_peaks_all_spectra)
    detect_all_peaks_btn.pack(side='left')

    # Export buttons
    export_control_frame = gui.create_themed_frame(peak_left_panel)
    export_control_frame.pack(fill='x', pady=10)

    export_peaks_btn = gui.create_themed_button(export_control_frame, text="💾 Export Current", 
                                 command=export_peak_picking)
    export_peaks_btn.pack(side='left', padx=(0, 10))

    export_all_peaks_btn = gui.create_themed_button(export_control_frame, text="📊 Export All Results", 
                                     command=export_all_peak_picking)
    export_all_peaks_btn.pack(side='left')

    # Results table
    # Couldn't get scrolling to work, yet. Opt to remove, can be saved in end report
    peak_results_frame = gui.create_themed_labelframe(peak_left_panel, text="Detected Peaks", padding=15)
    peak_results_frame.pack(fill='both', expand=True, pady=(15, 0))

    # Create results table with Integral and Width columns
    peak_picking_table = ttk.Treeview(peak_results_frame, columns=("Sample", "Peak", "PPM", "Intensity", "Integral", "Width_PPM"), 
                                     show="headings", height=10)
    peak_picking_table.heading("Sample", text="Sample")
    peak_picking_table.heading("Peak", text="Peak")
    peak_picking_table.heading("PPM", text="PPM")
    peak_picking_table.heading("Intensity", text="Intensity")
    peak_picking_table.heading("Integral", text="Integral")
    peak_picking_table.heading("Width_PPM", text="Width (ppm)")
    peak_picking_table.column("Sample", width=100)
    peak_picking_table.column("Peak", width=80)
    peak_picking_table.column("PPM", width=80)
    peak_picking_table.column("Intensity", width=100)
    peak_picking_table.column("Integral", width=100)
    peak_picking_table.column("Width_PPM", width=80)
    peak_picking_table.pack(fill='both', expand=True)

    # Right panel - spectrum plot with peaks
    peak_right_panel = gui.create_themed_frame(peak_picking_frame)
    peak_right_panel.pack(side='right', fill='both', expand=True)

    # Create matplotlib figure for peak picking
    peak_fig = plt.Figure(figsize=(10, 8), dpi=100)
    peak_canvas = FigureCanvasTkAgg(peak_fig, master=peak_right_panel)
    peak_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Toolbar for peak picking plot
    peak_toolbar_frame = gui.create_themed_frame(peak_right_panel)
    peak_toolbar_frame.pack(side=tk.TOP, fill=tk.X)
    peak_toolbar = NavigationToolbar2Tk(peak_canvas, peak_toolbar_frame)
    peak_toolbar.update()

    # Initial plot
    setup_initial_peak_plot(peak_fig, peak_canvas)

    # Description
    #peak_desc_frame = gui.create_themed_labelframe(peak_left_panel, text="About", padding=15)
    #peak_desc_frame.pack(fill='x', pady=(15, 0))

    #description_text = """This module automatically detects peaks in NMR spectra and calculates integrals.
    #                        • 'Detect Peaks': Analyze selected spectrum
    #                        • 'Detect All Spectra': Apply same settings to all spectra
    #                        • 'Remove Underground Peaks': Filter out small/noise peaks
    #                        • 'Export Current': Save current spectrum results
    #                        • 'Export All Results': Save combined results from all spectra
    #                        • Integrals are calculated by finding where peaks intersect baseline

    #Underground peak removal helps eliminate:
    #- Low intensity noise peaks
    #- Peaks with small integrals
    #- Very narrow peaks (potential artifacts)"""
    
#    gui.create_themed_label(peak_desc_frame, text=description_text, justify='left', font=('Segoe UI', 9)).pack(anchor='w')
    
    # Register for spectra updates
    globals.add_event_listener('spectra_updated', 
                              lambda spectra: update_peak_picking_spectra_list(peak_picking_spectra_listbox))
    
    return tab, peak_picking_spectra_listbox

def update_peak_picking_spectra_list(peak_picking_spectra_listbox):
    """Update the peak picking spectra listbox."""
    peak_picking_spectra_listbox.delete(0, tk.END)
    
    if not globals.spectra:
        return
        
    for i, (ppm_scale, data, sample_name, pdata_dir) in enumerate(globals.spectra):
        peak_picking_spectra_listbox.insert(tk.END, sample_name)

def on_peak_picking_spectrum_select(event, peak_fig, peak_canvas):
    """Handle spectrum selection in peak picking tab."""
    selection = event.widget.curselection()
    if selection and globals.spectra:
        # Clear previous peak picking results when new spectrum is selected
        globals.peak_picking_results = []
        
        # Plot the spectrum without peaks
        index = selection[0]
        if index < len(globals.spectra):
            ppm_scale, data, sample_name, pdata_dir = globals.spectra[index]
            plot_peak_picking_spectrum(ppm_scale, data, sample_name, [], peak_fig, peak_canvas)

def auto_detect_peaks(peak_picking_spectra_listbox, peak_height_entry, peak_distance_entry,
                     peak_prominence_entry, peak_baseline_entry, peak_picking_table,
                     peak_fig, peak_canvas):
    """Auto-detect peaks in selected spectrum."""
    selection = peak_picking_spectra_listbox.curselection()
    if not selection or not globals.spectra:
        messagebox.showinfo("Info", "Please select a spectrum first.")
        return
    
    # Get peak detection parameters
    try:
        height = float(peak_height_entry.get())
        distance = int(peak_distance_entry.get())
        prominence = float(peak_prominence_entry.get())
        baseline_threshold = float(peak_baseline_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid peak detection parameters.")
        return
    
    # Get selected spectrum
    index = selection[0]
    if index >= len(globals.spectra):
        return
        
    ppm_scale, data, sample_name, pdata_dir = globals.spectra[index]
    
    # Detect peaks
    globals.peak_picking_results = peak_picking_analysis.detect_peaks(
        ppm_scale, data, sample_name, height, distance, prominence, baseline_threshold)
    
    # Display results
    display_peak_picking_results(peak_picking_table)
    
    # Plot with detected peaks
    peaks = [result["Index"] for result in globals.peak_picking_results]
    plot_peak_picking_spectrum(ppm_scale, data, sample_name, peaks, peak_fig, peak_canvas)

def detect_peaks_all_spectra():
    """Detect peaks in all spectra."""
    if not globals.spectra:
        messagebox.showinfo("Info", "No spectra loaded.")
        return
    
    # Get peak detection parameters (using default values for now)
    try:
        height = 5000000
        distance = 10
        prominence = 50000
        baseline_threshold = 0.01
    except ValueError:
        messagebox.showerror("Error", "Invalid peak detection parameters.")
        return
    
    all_peak_picking_results = []
    
    # Process all spectra
    for ppm_scale, data, sample_name, pdata_dir in globals.spectra:
        # Detect peaks
        peaks = peak_picking_analysis.detect_peaks(
            ppm_scale, data, sample_name, height, distance, prominence, baseline_threshold)
        all_peak_picking_results.extend(peaks)
    
    globals.all_peak_picking_results = all_peak_picking_results
    messagebox.showinfo("Success", f"Detected {len(all_peak_picking_results)} peaks across {len(globals.spectra)} spectra.")

def display_peak_picking_results(peak_picking_table):
    """Display peak picking results in the table."""
    # Clear the table
    for row in peak_picking_table.get_children():
        peak_picking_table.delete(row)
    
    # Populate with results
    for result in globals.peak_picking_results:
        peak_picking_table.insert("", "end", values=(
            result["Sample"],
            result["Peak"],
            f"{result['PPM']:.3f}",
            f"{result['Intensity']:.6f}",
            f"{result['Integral']:.6f}",
            f"{result['Width_PPM']:.3f}"
        ))

def plot_peak_picking_spectrum(ppm_scale, data, sample_name, peaks, peak_fig, peak_canvas):
    """Plot spectrum with detected peaks."""
    peak_fig.clear()
    ax = peak_fig.add_subplot(111)
    
    gui.setup_plot_style(ax)
    
    # Plot spectrum
    ax.plot(ppm_scale, data, color=gui.Theme.SPECTRUM_COLORS[0], linewidth=1, label=sample_name)
    
    if peaks:
        # Plot detected peaks
        ax.plot(ppm_scale[peaks], data[peaks], "x", color=gui.Theme.PEAK_MARKER_COLOR, 
                markersize=8, label='Detected Peaks')
        
        # Plot integration regions and baselines
        for i, result in enumerate(globals.peak_picking_results):
            if i < len(peaks):
                # Draw baseline
                ax.hlines(y=result['Baseline'], xmin=result['Start_PPM'], xmax=result['End_PPM'], 
                         color=gui.Theme.BASELINE_COLOR, linestyle='--', alpha=0.7, linewidth=1)
                
                # Fill integration region
                start_idx = np.abs(ppm_scale - result['Start_PPM']).argmin()
                end_idx = np.abs(ppm_scale - result['End_PPM']).argmin()
                if start_idx > end_idx: 
                    start_idx, end_idx = end_idx, start_idx
                
                ax.fill_between(ppm_scale[start_idx:end_idx+1], 
                               data[start_idx:end_idx+1], 
                               result['Baseline'],
                               alpha=gui.Theme.INTEGRATION_ALPHA, 
                               color=gui.Theme.INTEGRATION_FILL, 
                               label='Integration Area' if i == 0 else "")
        
        # Annotate peaks with integration values
        for i, peak_idx in enumerate(peaks):
            if i < len(globals.peak_picking_results):
                result = globals.peak_picking_results[i]
                ax.annotate(f'Peak {i+1}\n{result["PPM"]:.3f} ppm\nArea: {result["Integral"]:.2e}', 
                           xy=(ppm_scale[peak_idx], data[peak_idx]),
                           xytext=(10, 10), textcoords='offset points',
                           color=gui.Theme.TEXT_PRIMARY, fontsize=8,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', color=gui.Theme.TEXT_PRIMARY, alpha=0.7))
    
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.set_title(f"Peak Detection: {sample_name}")
    ax.invert_xaxis()
    ax.legend()
    peak_canvas.draw()

def remove_underground_peaks(underground_intensity_entry, underground_integral_entry, 
                            underground_width_entry, peak_picking_spectra_listbox,
                            peak_picking_table, peak_fig, peak_canvas):
    """Remove underground peaks from current results."""
    if not globals.peak_picking_results:
        messagebox.showinfo("Info", "No peaks detected. Please run peak detection first.")
        return
    
    try:
        intensity_threshold = float(underground_intensity_entry.get())
        integral_threshold = float(underground_integral_entry.get())
        width_threshold = float(underground_width_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric thresholds.")
        return
    
    original_count = len(globals.peak_picking_results)
    
    # Filter peaks based on thresholds
    filtered_peaks = []
    for peak in globals.peak_picking_results:
        # Check if peak meets any removal criteria
        if (peak["Intensity"] < intensity_threshold or 
            peak["Integral"] < integral_threshold or 
            peak["Width_PPM"] < width_threshold):
            continue  # Skip this peak
        else:
            filtered_peaks.append(peak)
    
    # Update global results
    globals.peak_picking_results = filtered_peaks
    
    # Update display
    display_peak_picking_results(peak_picking_table)
    
    # Update plot
    selection = peak_picking_spectra_listbox.curselection()
    if selection and globals.peak_picking_results:
        index = selection[0]
        if index < len(globals.spectra):
            ppm_scale, data, sample_name, pdata_dir = globals.spectra[index]
            peak_indices = [peak["Index"] for peak in globals.peak_picking_results]
            plot_peak_picking_spectrum(ppm_scale, data, sample_name, peak_indices, peak_fig, peak_canvas)
    
    removed_count = original_count - len(globals.peak_picking_results)
    messagebox.showinfo("Underground Peaks Removed", 
                       f"Removed {removed_count} out of {original_count} peaks.\n"
                       f"Remaining: {len(globals.peak_picking_results)} peaks.")

def remove_underground_peaks_all_spectra(underground_intensity_entry, underground_integral_entry, 
                                        underground_width_entry):
    """Remove underground peaks from all spectra results."""
    if not globals.all_peak_picking_results:
        messagebox.showinfo("Info", "No peaks detected across all spectra. Please run 'Detect Peaks All Spectra' first.")
        return
    
    try:
        intensity_threshold = float(underground_intensity_entry.get())
        integral_threshold = float(underground_integral_entry.get())
        width_threshold = float(underground_width_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric thresholds.")
        return
    
    original_count = len(globals.all_peak_picking_results)
    
    # Filter peaks based on thresholds
    filtered_peaks = []
    for peak in globals.all_peak_picking_results:
        # Check if peak meets any removal criteria
        if (peak["Intensity"] < intensity_threshold or 
            peak["Integral"] < integral_threshold or 
            peak["Width_PPM"] < width_threshold):
            continue  # Skips this peak
        else:
            filtered_peaks.append(peak)
    
    # Update global results
    globals.all_peak_picking_results = filtered_peaks
    
    removed_count = original_count - len(globals.all_peak_picking_results)
    messagebox.showinfo("Underground Peaks Removed", 
                       f"Removed {removed_count} out of {original_count} peaks across all spectra.\n"
                       f"Remaining: {len(globals.all_peak_picking_results)} peaks.")

def reset_underground_parameters(underground_intensity_entry, underground_integral_entry, 
                                underground_width_entry):
    """Reset underground peak removal parameters to defaults."""
    underground_intensity_entry.delete(0, tk.END)
    underground_intensity_entry.insert(0, "100000")
    underground_integral_entry.delete(0, tk.END)
    underground_integral_entry.insert(0, "10000")
    underground_width_entry.delete(0, tk.END)
    underground_width_entry.insert(0, "0.001")

def export_peak_picking():
    """Export current peak picking results."""
    if not globals.peak_picking_results:
        messagebox.showerror("Error", "No peak picking results to export.")
        return
        
    filename = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save peak picking results as"
    )
    
    if filename:
        df = pd.DataFrame(globals.peak_picking_results)
        df = df[["Sample", "Peak", "PPM", "Intensity", "Integral", "Width_PPM", "Start_PPM", "End_PPM", "Baseline", "Index"]]
        with pd.ExcelWriter(filename) as writer:
            df.to_excel(writer, sheet_name="Peak Picking", index=False)
        messagebox.showinfo("Success", f"Peak picking results saved to {filename}")

def export_all_peak_picking():
    """Export all peak picking results."""
    if not globals.all_peak_picking_results:
        messagebox.showerror("Error", "No peak picking results to export. Run 'Detect Peaks All Spectra' first.")
        return
        
    filename = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save all peak picking results as"
    )
    
    if filename:
        # Create detailed results sheet
        df_detailed = pd.DataFrame(globals.all_peak_picking_results)
        df_detailed = df_detailed[["Sample", "Peak", "PPM", "Intensity", "Integral", "Width_PPM", "Start_PPM", "End_PPM", "Baseline", "Index"]]
        
        # Create summary sheet (pivot table) for PPM values
        df_summary_ppm = df_detailed.pivot_table(
            index='Sample', 
            columns='Peak', 
            values='PPM',
            aggfunc='first'
        )
        
        # Create summary sheet for Integral values
        df_summary_integral = df_detailed.pivot_table(
            index='Sample', 
            columns='Peak', 
            values='Integral',
            aggfunc='first'
        )
        
        with pd.ExcelWriter(filename) as writer:
            df_detailed.to_excel(writer, sheet_name="Detailed Results", index=False)
            df_summary_ppm.to_excel(writer, sheet_name="PPM by Sample")
            df_summary_integral.to_excel(writer, sheet_name="Integrals by Sample")
            
            # Also create intensity summary
            df_intensity_summary = df_detailed.pivot_table(
                index='Sample', 
                columns='Peak', 
                values='Intensity',
                aggfunc='first'
            )
            df_intensity_summary.to_excel(writer, sheet_name="Intensity by Sample")
            
            # Create width summary
            df_width_summary = df_detailed.pivot_table(
                index='Sample', 
                columns='Peak', 
                values='Width_PPM',
                aggfunc='first'
            )
            df_width_summary.to_excel(writer, sheet_name="Width by Sample")
        
        messagebox.showinfo("Success", f"All peak picking results saved to {filename}\n\n"
                                      f"Found {len(globals.all_peak_picking_results)} peaks across {len(globals.spectra)} spectra.")

def setup_initial_peak_plot(peak_fig, peak_canvas):
    """Set up the initial empty plot for peak picking."""
    ax = peak_fig.add_subplot(111)
    gui.setup_plot_style(ax)
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.invert_xaxis()
    ax.set_title("Select a spectrum and detect peaks")
    peak_canvas.draw()