import pandas as pd
from tkinter import messagebox, filedialog
import globals

def generate_comprehensive_report():
    """Export a comprehensive report with all selected results including deconvolution."""
    if not globals.spectra:
        messagebox.showerror("Error", "No spectra loaded. Please load data first.")
        return
    
    # Ask for save location
    filename = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save automated report as"
    )
    
    if not filename:
        return
    
    try:
        with pd.ExcelWriter(filename) as writer:
            # 1. Dataset Overview
            dataset_overview = pd.DataFrame({
                'Parameter': ['Total Spectra', 'Samples', 'Peak Limits Loaded', 'Deconvolution Analyses'],
                'Value': [
                    len(globals.spectra), 
                    len(set([s[2] for s in globals.spectra])), 
                    'Yes' if not globals.peak_limits.empty else 'No',
                    len(globals.deconvolution_results) if globals.deconvolution_results else 'No'
                ]
            })
            dataset_overview.to_excel(writer, sheet_name='Dataset Overview', index=False)
            
            # 2. Sample Information
            sample_info = []
            for ppm_scale, data, sample_name, pdata_dir in globals.spectra:
                sample_info.append({
                    'Sample Name': sample_name,
                    'Data Points': len(data),
                    'PPM Range': f"{ppm_scale.min():.2f} - {ppm_scale.max():.2f}",
                    'Max Intensity': f"{data.max():.2e}",
                    'File Path': pdata_dir
                })
            pd.DataFrame(sample_info).to_excel(writer, sheet_name='Sample Information', index=False)
            
            # 3. Peak Limits
            if not globals.peak_limits.empty:
                globals.peak_limits.to_excel(writer, sheet_name='Peak Definitions', index=False)
            
            # 4. Concentration Results
            if globals.concentration_results:
                df_conc = pd.DataFrame(globals.concentration_results)
                df_conc_pivot = df_conc.pivot(index="Sample", columns="Peak", values="Concentration")
                df_conc_pivot.to_excel(writer, sheet_name='Concentrations')
            
            # 5. Integration Results
            if globals.integration_results:
                df_int = pd.DataFrame(globals.integration_results)
                df_int_pivot = df_int.pivot(index="Sample", columns="Peak", values="Integral")
                df_int_pivot.to_excel(writer, sheet_name='Integrations')
            
            # 6. Binning Results
            if globals.binning_results is not None:
                globals.binning_results.to_excel(writer, sheet_name='Binning Results')
            
            # 7. Peak Picking Summary
            if globals.all_peak_picking_results:
                df_peaks = pd.DataFrame(globals.all_peak_picking_results)
                # Create summary tables
                peak_summary_ppm = df_peaks.pivot_table(
                    index='Sample', 
                    columns='Peak', 
                    values='PPM',
                    aggfunc='first'
                )
                peak_summary_integral = df_peaks.pivot_table(
                    index='Sample', 
                    columns='Peak', 
                    values='Integral',
                    aggfunc='first'
                )
                peak_summary_ppm.to_excel(writer, sheet_name='Peak Positions')
                peak_summary_integral.to_excel(writer, sheet_name='Peak Integrals')
            
            # 8. Deconvolution Results
            if globals.deconvolution_results:
                # Create detailed deconvolution results
                df_deconv = pd.DataFrame(globals.deconvolution_results)
                df_deconv.to_excel(writer, sheet_name='Deconvolution Detailed', index=False)
                
                # Create summary tables for deconvolution
                deconv_summary_center = df_deconv.pivot_table(
                    index=None,  # Since deconvolution is per region, not per sample
                    columns='Peak',
                    values='Center_PPM',
                    aggfunc='first'
                )
                
                deconv_summary_integral = df_deconv.pivot_table(
                    index=None,
                    columns='Peak',
                    values='Integral',
                    aggfunc='first'
                )
                
                deconv_summary_amplitude = df_deconv.pivot_table(
                    index=None,
                    columns='Peak',
                    values='Amplitude',
                    aggfunc='first'
                )
                
                deconv_summary_width = df_deconv.pivot_table(
                    index=None,
                    columns='Peak',
                    values='Width',
                    aggfunc='first'
                )
                
                # Write summary tables
                deconv_summary_center.to_excel(writer, sheet_name='Deconv Centers')
                deconv_summary_integral.to_excel(writer, sheet_name='Deconv Integrals')
                deconv_summary_amplitude.to_excel(writer, sheet_name='Deconv Amplitudes')
                deconv_summary_width.to_excel(writer, sheet_name='Deconv Widths')
            
            # 9. Analysis Summary
            summary_data = {
                'Analysis Type': [
                    'Dataset', 
                    'Concentrations', 
                    'Integrations', 
                    'Binning', 
                    'Peak Picking',
                    'Deconvolution'
                ],
                'Status': [
                    'Completed' if globals.spectra else 'Not Started',
                    'Completed' if globals.concentration_results else 'Not Started', 
                    'Completed' if globals.integration_results else 'Not Started',
                    'Completed' if globals.binning_results is not None else 'Not Started',
                    'Completed' if globals.all_peak_picking_results else 'Not Started',
                    'Completed' if globals.deconvolution_results else 'Not Started'
                ],
                'Results Count': [
                    len(globals.spectra),
                    len(globals.concentration_results),
                    len(globals.integration_results),
                    globals.binning_results.shape[0] if globals.binning_results is not None else 0,
                    len(globals.all_peak_picking_results),
                    len(globals.deconvolution_results)
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Analysis Summary', index=False)
        
        messagebox.showinfo("Success", f"Report exported!\n\nFile saved as: {filename}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

def generate_quick_summary():
    """Generate a quick summary of what's been done including deconvolution."""
    if not globals.spectra:
        messagebox.showerror("Error", "No spectra loaded.")
        return
    
    # Create a simple text report
    report_text = "NMR Analysis Summary\n"
    report_text += "=" * 50 + "\n\n"
    
    report_text += f"Dataset Information:\n"
    report_text += f"- Total spectra: {len(globals.spectra)}\n"
    report_text += f"- Samples: {len(set([s[2] for s in globals.spectra]))}\n"
    report_text += f"- Peak definitions: {'Loaded' if not globals.peak_limits.empty else 'Not loaded'}\n\n"
    
    report_text += f"Analysis Status:\n"
    report_text += f"- Concentration analysis: {'Completed' if globals.concentration_results else 'Not performed'}\n"
    report_text += f"- Integration analysis: {'Completed' if globals.integration_results else 'Not performed'}\n"
    report_text += f"- Binning analysis: {'Completed' if globals.binning_results is not None else 'Not performed'}\n"
    report_text += f"- Peak picking: {'Completed' if globals.all_peak_picking_results else 'Not performed'}\n"
    report_text += f"- Deconvolution: {'Completed' if globals.deconvolution_results else 'Not performed'}\n\n"
    
    if globals.concentration_results:
        unique_compounds = len(set([r['Peak'] for r in globals.concentration_results]))
        unique_samples = len(set([r['Sample'] for r in globals.concentration_results]))
        report_text += f"Concentration Analysis:\n"
        report_text += f"- Compounds quantified: {unique_compounds}\n"
        report_text += f"- Samples analyzed: {unique_samples}\n\n"
    
    if globals.all_peak_picking_results:
        total_peaks = len(globals.all_peak_picking_results)
        avg_peaks_per_sample = total_peaks / len(globals.spectra)
        report_text += f"Peak Picking Analysis:\n"
        report_text += f"- Total peaks detected: {total_peaks}\n"
        report_text += f"- Average peaks per sample: {avg_peaks_per_sample:.1f}\n\n"
    
    if globals.deconvolution_results:
        total_deconv_peaks = len(globals.deconvolution_results)
        avg_integral = np.mean([r['Integral'] for r in globals.deconvolution_results])
        avg_width = np.mean([r['Width'] for r in globals.deconvolution_results])
        
        report_text += f"Deconvolution Analysis:\n"
        report_text += f"- Total deconvolved peaks: {total_deconv_peaks}\n"
        report_text += f"- Average integral: {avg_integral:.2e}\n"
        report_text += f"- Average width (FWHM): {avg_width:.4f} ppm\n"
    
    # Show report in message box
    messagebox.showinfo("Summary", report_text)