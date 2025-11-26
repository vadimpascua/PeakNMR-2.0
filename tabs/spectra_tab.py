import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import globals
import gui

def create_spectra_tab(tab_control):
    """Create the spectrum viewer tab."""
    tab = gui.create_themed_frame(tab_control)
    tab_control.add(tab, text="📊 Spectrum Viewer")
    
    spectra_frame = gui.create_themed_frame(tab)
    spectra_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Left panel - spectra list and controls
    left_panel = gui.create_themed_frame(spectra_frame)
    left_panel.pack(side='left', fill='y', padx=(0, 10))

    gui.create_themed_label(left_panel, text="Spectra List:", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(0, 10))

    # Control buttons
    control_frame = gui.create_themed_frame(left_panel)
    control_frame.pack(fill='x', pady=(0, 10))

    view_all_btn = gui.create_themed_button(control_frame, text="👁️ View All", 
                             command=lambda: plot_all_spectra(view_fig, view_canvas))
    view_all_btn.pack(side='left', padx=(0, 5))

    view_selected_btn = gui.create_themed_button(control_frame, text="🔍 Overlay Selected", 
                                  command=lambda: plot_selected_spectra(spectra_listbox, view_fig, view_canvas))
    view_selected_btn.pack(side='left', padx=(0, 5))

    clear_btn = gui.create_themed_button(control_frame, text="🗑️ Clear Selection", 
                          command=lambda: clear_selection(spectra_listbox, view_fig, view_canvas))
    clear_btn.pack(side='left')

    # Spectra listbox with scrollbar
    list_frame = gui.create_themed_labelframe(left_panel, text="Available Spectra")
    list_frame.pack(fill='both', expand=True, pady=(10, 0))

    spectra_listbox = tk.Listbox(list_frame, height=20, width=30)
    gui.configure_listbox(spectra_listbox)
    spectra_listbox.pack(side='left', fill='both', expand=True)

    list_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=spectra_listbox.yview)
    spectra_listbox.configure(yscrollcommand=list_scrollbar.set)
    list_scrollbar.pack(side='right', fill='y')

    spectra_listbox.bind('<<ListboxSelect>>', 
                        lambda event: on_spectrum_select(event, spectra_listbox, view_fig, view_canvas))

    # Instructions
    spectra_info = gui.create_themed_labelframe(left_panel, text="Viewing Options")
    spectra_info.pack(fill='x', pady=(10, 0))

    instructions_text = """
    • Click on a spectrum to view it individually
    • Use Ctrl+Click to select multiple spectra
    • Click 'Overlay Selected' to compare spectra
    • 'View All' shows all spectra together
    • Peak regions are highlighted
    """
    gui.create_themed_label(spectra_info, text=instructions_text, justify='left', font=('Segoe UI', 8)).pack(anchor='w', padx=5, pady=5)

    # Right panel - spectrum plot
    right_panel = gui.create_themed_frame(spectra_frame)
    right_panel.pack(side='right', fill='both', expand=True)

    # Create matplotlib figure for spectrum view
    view_fig = plt.Figure(figsize=(10, 8), dpi=100)
    view_canvas = FigureCanvasTkAgg(view_fig, master=right_panel)
    view_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Toolbar for spectrum view
    view_toolbar_frame = gui.create_themed_frame(right_panel)
    view_toolbar_frame.pack(side=tk.TOP, fill=tk.X)
    view_toolbar = NavigationToolbar2Tk(view_canvas, view_toolbar_frame)
    view_toolbar.update()

    # Initial plot
    setup_initial_plot(view_fig, view_canvas)
    
    # Register for spectra updates
    globals.add_event_listener('spectra_updated', 
                              lambda spectra: update_spectra_list(spectra_listbox))
    
    return tab, spectra_listbox

def update_spectra_list(spectra_listbox):
    """Update the spectra listbox with loaded spectra."""
    spectra_listbox.delete(0, tk.END)
    
    if not globals.spectra:
        return
        
    for i, (ppm_scale, data, sample_name, pdata_dir) in enumerate(globals.spectra):
        spectra_listbox.insert(tk.END, sample_name)

def on_spectrum_select(event, spectra_listbox, view_fig, view_canvas):
    """Handle spectrum selection in the listbox."""
    selection = spectra_listbox.curselection()
    if selection and globals.spectra:
        sorted_indices = sorted(spectra_listbox.curselection())
        if sorted_indices:
            index = sorted_indices[0]
            if index < len(globals.spectra):
                ppm_scale, data, sample_name, pdata_dir = globals.spectra[index]
                plot_single_spectrum(ppm_scale, data, sample_name, view_fig, view_canvas)

def plot_single_spectrum(ppm_scale, data, sample_name, view_fig, view_canvas):
    """Plot a single spectrum with peak regions."""
    view_fig.clear()
    ax = view_fig.add_subplot(111)
    
    gui.setup_plot_style(ax)
    
    # Plot spectrum
    ax.plot(ppm_scale, data, color=gui.Theme.SPECTRUM_COLORS[0], linewidth=1, label=sample_name)
    
    # Plot peak regions if available
    if not globals.peak_limits.empty:
        ymax = data.max()
        ymin = data.min()
        
        for _, row in globals.peak_limits.iterrows():
            name = row["Peak identity"]
            start = row["ppm start"]
            end = row["ppm end"]
            
            s = np.abs(ppm_scale - start).argmin()
            e = np.abs(ppm_scale - end).argmin()
            if s > e: s, e = e, s
            
            # Fill peak region
            ax.fill_between(ppm_scale[s:e+1], data[s:e+1], 
                           alpha=gui.Theme.PEAK_REGION_ALPHA, 
                           color=gui.Theme.PEAK_REGION_FILL)
            
            # Find maximum y-value for label positioning
            peak_max = data[s:e+1].max()
            
            # Add peak label
            mid = (start + end) / 2
            ax.text(mid, peak_max * 1.02, name, rotation=90, ha="center", va="bottom", 
                   color=gui.Theme.TEXT_PRIMARY, fontsize=8, 
                   bbox=dict(boxstyle="round,pad=0.1", facecolor='black', alpha=0.7))
    
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.set_title(f"Spectrum: {sample_name}")
    ax.invert_xaxis()
    ax.legend()
    view_canvas.draw()

def plot_all_spectra(view_fig, view_canvas):
    """Plot all spectra in overlay."""
    if not globals.spectra:
        return
        
    view_fig.clear()
    ax = view_fig.add_subplot(111)
    
    gui.setup_plot_style(ax)
    
    # Plot all spectra
    for i, (ppm_scale, data, sample_name, pdata_dir) in enumerate(globals.spectra):
        color = gui.Theme.get_spectrum_color(i)
        ax.plot(ppm_scale, data, color=color, linewidth=0.7, alpha=0.8, label=sample_name)
    
    # Plot peak regions if available
    if not globals.peak_limits.empty:
        ymax = max([data.max() for _, data, _, _ in globals.spectra])
        
        for _, row in globals.peak_limits.iterrows():
            name = row["Peak identity"]
            start = row["ppm start"]
            end = row["ppm end"]
            
            # Use first spectrum for peak region coordinates
            ppm_scale_first = globals.spectra[0][0]
            s = np.abs(ppm_scale_first - start).argmin()
            e = np.abs(ppm_scale_first - end).argmin()
            if s > e: s, e = e, s
            
            # Find maximum intensity in this peak region across all spectra
            peak_max = 0
            for ppm_scale, data, _, _ in globals.spectra:
                s_idx = np.abs(ppm_scale - start).argmin()
                e_idx = np.abs(ppm_scale - end).argmin()
                if s_idx > e_idx: s_idx, e_idx = e_idx, s_idx
                region_max = data[s_idx:e_idx+1].max()
                peak_max = max(peak_max, region_max)
            
            # Fill peak region
            ax.fill_between(ppm_scale_first[s:e+1], 0, ymax * 1.1, 
                           alpha=0.2, color=gui.Theme.PEAK_REGION_FILL)
            
            # Add peak label
            mid = (start + end) / 2
            ax.text(mid, peak_max * 1.05, name, rotation=90, ha="center", va="bottom", 
                   color=gui.Theme.TEXT_PRIMARY, fontsize=8, 
                   bbox=dict(boxstyle="round,pad=0.1", facecolor='black', alpha=0.7))
    
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.set_title("All Spectra Overlay")
    ax.invert_xaxis()
    ax.legend(fontsize=6)
    view_canvas.draw()

def plot_selected_spectra(spectra_listbox, view_fig, view_canvas):
    """Plot selected spectra in overlay."""
    selection = spectra_listbox.curselection()
    if not selection or not globals.spectra:
        return
    
    view_fig.clear()
    ax = view_fig.add_subplot(111)
    
    gui.setup_plot_style(ax)
    
    # Plot selected spectra
    for i, idx in enumerate(selection):
        if idx < len(globals.spectra):
            ppm_scale, data, sample_name, pdata_dir = globals.spectra[idx]
            color = gui.Theme.get_spectrum_color(i)
            ax.plot(ppm_scale, data, color=color, linewidth=1, label=sample_name)
    
    # Plot peak regions if available
    if not globals.peak_limits.empty:
        selected_data = [globals.spectra[idx][1] for idx in selection if idx < len(globals.spectra)]
        ymax = max([data.max() for data in selected_data]) if selected_data else 0
        
        for _, row in globals.peak_limits.iterrows():
            name = row["Peak identity"]
            start = row["ppm start"]
            end = row["ppm end"]
            
            if selection and selection[0] < len(globals.spectra):
                ppm_scale_first = globals.spectra[selection[0]][0]
                s = np.abs(ppm_scale_first - start).argmin()
                e = np.abs(ppm_scale_first - end).argmin()
                if s > e: s, e = e, s
                
                # Find maximum intensity in this peak region across selected spectra
                peak_max = 0
                for idx in selection:
                    if idx < len(globals.spectra):
                        ppm_scale, data, _, _ = globals.spectra[idx]
                        s_idx = np.abs(ppm_scale - start).argmin()
                        e_idx = np.abs(ppm_scale - end).argmin()
                        if s_idx > e_idx: s_idx, e_idx = e_idx, s_idx
                        region_max = data[s_idx:e_idx+1].max()
                        peak_max = max(peak_max, region_max)
                
                # Fill peak region
                ax.fill_between(ppm_scale_first[s:e+1], 0, ymax * 1.1, 
                               alpha=0.2, color=gui.Theme.PEAK_REGION_FILL)
                
                # Add peak label
                mid = (start + end) / 2
                ax.text(mid, peak_max * 1.05, name, rotation=90, ha="center", va="bottom", 
                       color=gui.Theme.TEXT_PRIMARY, fontsize=8, 
                       bbox=dict(boxstyle="round,pad=0.1", facecolor='black', alpha=0.7))
    
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.set_title(f"Overlay of {len(selection)} Selected Spectra")
    ax.invert_xaxis()
    ax.legend()
    view_canvas.draw()

def clear_selection(spectra_listbox, view_fig, view_canvas):
    """Clear spectrum selection and plot all spectra."""
    spectra_listbox.selection_clear(0, tk.END)
    plot_all_spectra(view_fig, view_canvas)

def setup_initial_plot(view_fig, view_canvas):
    """Set up the initial empty plot."""
    ax = view_fig.add_subplot(111)
    gui.setup_plot_style(ax)
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.invert_xaxis()
    ax.set_title("Load data to view spectra")
    view_canvas.draw()