import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import file_io
import globals

def create_dataset_tab(tab_control, status_label):
    """Create the dataset setup tab."""
    tab = ttk.Frame(tab_control)
    tab_control.add(tab, text="📁 Dataset Setup")
    
    setup_frame = ttk.Frame(tab)
    setup_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Peak limits section
    limits_frame = ttk.LabelFrame(setup_frame, text="1. Peak Configuration", padding=15)
    limits_frame.pack(fill='x', pady=(0, 15))

    ttk.Label(limits_frame, text="Upload peak definitions file:").grid(row=0, column=0, sticky='w', pady=5)
    upload_peak_button = ttk.Button(limits_frame, text="📄 Upload peak_limits.xlsx", 
                                   command=lambda: upload_peak_limits(peak_limits_label))
    upload_peak_button.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))

    peak_limits_label = ttk.Label(limits_frame, text="No file selected", foreground="#CCCCCC")
    peak_limits_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 0))

    # Dataset selection section
    dataset_frame = ttk.LabelFrame(setup_frame, text="2. Dataset Selection", padding=15)
    dataset_frame.pack(fill='x', pady=(0, 15))

    ttk.Label(dataset_frame, text="Select processed Bruker NMR dataset:").grid(row=0, column=0, sticky='w', pady=5)
    select_button = ttk.Button(dataset_frame, text="📂 Choose dataset", 
                              command=lambda: browse_directory(selected_dirs_label, status_label))
    select_button.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))

    selected_dirs_label = ttk.Label(dataset_frame, text="No dataset selected", foreground="#CCCCCC")
    selected_dirs_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 0))

    # Instructions
    info_frame = ttk.LabelFrame(setup_frame, text="ℹ️ Instructions", padding=15)
    info_frame.pack(fill='x', pady=(0, 15))

    instructions = """
    1. First upload your peak_limits.xlsx file containing peak definitions
    2. Select your Bruker NMR dataset (folder or zip file)
    3. Navigate to Spectrum Viewer tab to examine individual or multiple spectra
    4. Use other tabs for specific analyses (Concentrations, Binning, Integrations, Peak Picking)
    5. Use Spectral Deconvolution for overlapping peak analysis
    6. Generate comprehensive reports in Automated Reporting tab
    """
    ttk.Label(info_frame, text=instructions, justify='left', font=('Segoe UI', 9)).pack(anchor='w')
    
    return tab

def upload_peak_limits(peak_limits_label):
    """Handle peak limits file upload."""
    file = filedialog.askopenfilename(
        title="Select peak_limits.xlsx",
        filetypes=[("Excel files", "*.xlsx")]
    )

    if file:
        globals.peak_limits_path = file
        peak_limits = file_io.load_peak_limits(file)
        if peak_limits is not None:
            globals.update_peak_limits(peak_limits)
            peak_limits_label.config(text=f"Selected: {os.path.basename(file)}")
            peak_limits_label.config(foreground="#2E8B57")
    else:
        peak_limits_label.config(text="No file selected")
        peak_limits_label.config(foreground="#FF6B6B")

def browse_directory(selected_dirs_label, status_label):
    """Handle directory/zip file selection and load spectra."""
    if globals.peak_limits_path is None:
        messagebox.showerror("Error", "Please upload a peak_limits.xlsx file first.")
        return

    # Ask user if source is zipped
    zipped = messagebox.askquestion("Zipped File or Directory",
                                    "Are you selecting a zipped file?",
                                    icon="question")

    if zipped == "yes":
        root_dir = filedialog.askopenfilename(
            title="Select zipped Bruker NMR dataset"
        )
        if not root_dir:
            return
            
        root_dir = file_io.extract_zip_file(root_dir)
        if root_dir is None:
            return
    else:
        root_dir = filedialog.askdirectory(
            title="Select folder containing processed Bruker NMR data"
        )
        if not root_dir:
            return

    # Update status
    status_label.config(text="Loading spectra...")
    status_label.update()
    
    try:
        # Load spectra
        spectra = file_io.load_spectra_from_directory(root_dir)
        
        if not spectra:
            messagebox.showerror("Error", "No spectra found in the selected directory.")
            status_label.config(text="No spectra found")
            return
        
        # Update global state and trigger events
        globals.selected_pdata_dirs = [root_dir]
        globals.update_spectra(spectra)
        
        # Update UI
        selected_dirs_label.config(text=f"Selected: {os.path.basename(root_dir)}")
        selected_dirs_label.config(foreground="#2E8B57")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load spectra: {str(e)}")
        status_label.config(text="Error loading spectra")