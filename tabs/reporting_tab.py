import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import analysis.reporting as reporting_analysis
import globals
import gui

def create_reporting_tab(tab_control):
    """Create the automated reporting tab."""
    tab = gui.create_themed_frame(tab_control)
    tab_control.add(tab, text="📋 Automated Reporting")
    
    report_frame = gui.create_themed_frame(tab)
    report_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Main content area
    report_main_frame = gui.create_themed_frame(report_frame)
    report_main_frame.pack(fill='both', expand=True, pady=20)

    # Title
    title_frame = gui.create_themed_frame(report_main_frame)
    title_frame.pack(fill='x', pady=(0, 30))

    gui.create_themed_label(title_frame, text="📋 Reporting", 
             font=('Segoe UI', 18, 'bold')).pack(anchor='center')

    # Report options frame
    options_frame = gui.create_themed_labelframe(report_main_frame, text="Report Options", padding=20)
    options_frame.pack(fill='x', pady=(0, 20))

    # Comprehensive report section
    comp_report_frame = gui.create_themed_frame(options_frame)
    comp_report_frame.pack(fill='x', pady=(0, 20))

    gui.create_themed_label(comp_report_frame, text="📊 Comprehensive Analysis Report", 
             font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 10))

    comp_description = """Generate a complete Excel report with all available analysis results including:
• Dataset overview and sample information
• Concentration results
• Integration results
• Binning results
• Peak picking summary
• Analysis status summary"""
    
    gui.create_themed_label(comp_report_frame, text=comp_description, justify='left', 
                           font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 15))

    generate_full_btn = gui.create_themed_button(comp_report_frame, text="🚀 Export Report", 
                              command=generate_automated_report)
    generate_full_btn.pack(anchor='w')

    
    # Description
    desc_frame = gui.create_themed_labelframe(report_main_frame, text="About", padding=15)
    desc_frame.pack(fill='x')

    description_text = """The Automated Reporting module generates comprehensive analysis reports suitable for publications,
theses, or project documentation. All results from previous analyses are automatically included
in the report, providing a complete overview of your NMR data analysis workflow.

Features:
• Click report generation
• Excel with multiple sheets
• Dataset overview and metadata
• Analysis results from all modules
• Status summary and quality metrics"""
    
    gui.create_themed_label(desc_frame, text=description_text, justify='left', font=('Segoe UI', 10)).pack(anchor='w')
    
    return tab

def generate_automated_report():
    """Generate comprehensive automated report."""
    reporting_analysis.generate_comprehensive_report()

def generate_quick_report():
    """Generate quick summary report."""
    reporting_analysis.generate_quick_summary()