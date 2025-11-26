import numpy as np
from scipy.signal import find_peaks, savgol_filter
from scipy.integrate import simpson as simps
from scipy.optimize import curve_fit
from tkinter import messagebox
import matplotlib.pyplot as plt
import gui
import globals

def lorentzian(x, amplitude, mean, gamma):
    """Lorentzian function for peak fitting - better for NMR peaks."""
    return amplitude * (gamma**2) / ((x - mean)**2 + gamma**2)

def multi_lorentzian(x, *params):
    """Sum of multiple Lorentzian functions."""
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        amplitude = params[i]
        mean = params[i+1]
        gamma = params[i+2]
        y += lorentzian(x, amplitude, mean, gamma)
    return y

def find_optimal_peak_count(x_data, y_data, max_peaks=10):
    """
    Suggest optimal number of peaks for deconvolution based on peak prominence.
    """
    # Find all potential peaks
    peaks, properties = find_peaks(y_data, prominence=np.max(y_data)*0.01)
    
    if len(peaks) == 0:
        return 1
    
    # Count prominent peaks
    if 'prominences' in properties:
        prominences = properties['prominences']
        # Count peaks with prominence above 5% of max prominence
        threshold = np.max(prominences) * 0.05
        significant_peaks = len([p for p in prominences if p > threshold])
        return min(significant_peaks, max_peaks)
    
    return min(len(peaks), max_peaks)

def estimate_baseline_advanced(x_data, y_data, window_size=51, polyorder=2):
    """
    Advanced baseline estimation using Savitzky-Golay filter and iterative approach.
    """
    if len(y_data) < window_size:
        window_size = len(y_data) - 1 if len(y_data) % 2 == 0 else len(y_data)
        if window_size < 3:
            return np.min(y_data)
    
    # Ensure window_size is odd
    if window_size % 2 == 0:
        window_size -= 1
    
    try:
        # Use Savitzky-Golay filter to smooth the data
        smoothed = savgol_filter(y_data, window_size, polyorder)
        
        # Find local minima in the smoothed data
        minima, _ = find_peaks(-smoothed, distance=len(y_data)//10, prominence=np.std(y_data)*0.1)
        
        if len(minima) > 0:
            # Use the minimum of the local minima as baseline
            baseline = np.min(smoothed[minima])
        else:
            # Fallback: use percentiles
            baseline = np.percentile(y_data, 10)
            
        # Ensure baseline is reasonable
        baseline = max(baseline, np.min(y_data) * 0.8)
        baseline = min(baseline, np.percentile(y_data, 25))
        
        return baseline
        
    except:
        # Fallback methods
        try:
            return np.percentile(y_data, 15)
        except:
            return np.min(y_data)

def validate_region_boundaries(ppm_scale, start_ppm, end_ppm):
    """Validate and adjust region boundaries to ensure they're within data range."""
    ppm_min = np.min(ppm_scale)
    ppm_max = np.max(ppm_scale)
    
    # Ensure start_ppm and end_ppm are within data range
    start_ppm = max(ppm_min, min(ppm_max, start_ppm))
    end_ppm = max(ppm_min, min(ppm_max, end_ppm))
    
    # Ensure we have a valid range
    if abs(start_ppm - end_ppm) < 0.01:  # Minimum 0.01 ppm range
        if start_ppm > ppm_min + 0.02:
            start_ppm = start_ppm - 0.01
            end_ppm = end_ppm + 0.01
        else:
            start_ppm = ppm_min
            end_ppm = ppm_min + 0.02
    
    return start_ppm, end_ppm

def find_peak_integration_bounds(x_data, individual_lorentzian, baseline=0, threshold_fraction=0.01):
    """
    Find where the Lorentzian peak intersects with the baseline threshold.
    """
    peak_max = np.max(individual_lorentzian)
    threshold = baseline + (threshold_fraction * peak_max)
    
    # Find where the Lorentzian drops below threshold
    above_threshold = individual_lorentzian > threshold
    
    if not np.any(above_threshold):
        return 0, len(x_data)-1
    
    indices = np.where(above_threshold)[0]
    start_idx = indices[0] if len(indices) > 0 else 0
    end_idx = indices[-1] if len(indices) > 0 else len(x_data)-1
    
    # Ensure indices are within bounds
    start_idx = max(0, start_idx)
    end_idx = min(len(x_data)-1, end_idx)
    
    return start_idx, end_idx

def find_local_maxima_with_refinement(x_data, y_data, candidate_positions, search_radius=10):
    """
    Refine peak positions by finding exact local maxima around candidate positions.
    """
    refined_positions = []
    refined_amplitudes = []
    
    for pos in candidate_positions:
        # Define search window around candidate position
        start_search = max(0, pos - search_radius)
        end_search = min(len(y_data), pos + search_radius + 1)
        
        # Extract the local region
        local_y = y_data[start_search:end_search]
        local_x = x_data[start_search:end_search]
        
        if len(local_y) == 0:
            continue
            
        # Find the exact maximum in this local region
        local_max_idx = np.argmax(local_y)
        exact_pos = start_search + local_max_idx
        
        # Ensure we don't go out of bounds
        if exact_pos < len(y_data):
            refined_positions.append(exact_pos)
            refined_amplitudes.append(y_data[exact_pos])
    
    return refined_positions, refined_amplitudes

def estimate_initial_parameters(x_data, y_data, num_peaks, baseline):
    """
    Better initial parameter estimation using refined local maxima detection.
    """
    # Use the original data (with baseline) for peak detection
    y_for_peak_detection = y_data
    
    # Find peaks in the original data with relaxed parameters
    peaks, properties = find_peaks(y_for_peak_detection, 
                                  height=np.max(y_for_peak_detection)*0.05,  # Lower threshold
                                  distance=len(y_for_peak_detection)//(num_peaks*3),  # More flexible distance
                                  prominence=np.max(y_for_peak_detection)*0.02)  # Lower prominence
    
    initial_params = []
    
    if len(peaks) > 0:
        # Refine peak positions by finding exact local maxima
        refined_peaks, refined_amplitudes = find_local_maxima_with_refinement(x_data, y_data, peaks)
        
        # Use the most prominent peaks based on amplitude
        if len(refined_peaks) >= num_peaks:
            # Sort by amplitude (highest first)
            sorted_indices = np.argsort(refined_amplitudes)[::-1]
            selected_peaks = [refined_peaks[i] for i in sorted_indices[:num_peaks]]
            selected_amplitudes = [refined_amplitudes[i] for i in sorted_indices[:num_peaks]]
        else:
            selected_peaks = refined_peaks
            selected_amplitudes = refined_amplitudes
        
        # Sort peaks by position (left to right)
        sorted_positions = np.argsort(selected_peaks)
        selected_peaks = [selected_peaks[i] for i in sorted_positions]
        selected_amplitudes = [selected_amplitudes[i] for i in sorted_positions]
        
        for peak_idx, amplitude_raw in zip(selected_peaks, selected_amplitudes):
            # Use exact local maximum position and height
            amplitude = amplitude_raw - baseline  # Subtract baseline for fitting
            mean = x_data[peak_idx]
            
            # Estimate gamma from peak width at half maximum (above baseline)
            half_max = baseline + (amplitude_raw - baseline) / 2
            left_idx = peak_idx
            right_idx = peak_idx
            
            # Find left half-maximum with extended search
            for i in range(peak_idx, max(0, peak_idx-50), -1):
                if y_data[i] <= half_max or i == 0:
                    left_idx = i
                    break
                    
            # Find right half-maximum with extended search
            for i in range(peak_idx, min(len(y_data)-1, peak_idx+50)):
                if y_data[i] <= half_max or i == len(y_data)-1:
                    right_idx = i
                    break
            
            # Calculate FWHM - for Lorentzian, gamma = FWHM/2
            fwhm = abs(x_data[right_idx] - x_data[left_idx])
            gamma = max(fwhm / 2, 0.005)  # Minimum gamma
            
            print(f"Initial peak: pos={mean:.3f}, raw_amp={amplitude_raw:.1f}, corrected_amp={amplitude:.1f}, gamma={gamma:.4f}")
            initial_params.extend([amplitude, mean, gamma])
            
    else:
        # Fallback: evenly spaced peaks with local maxima refinement
        peak_positions = np.linspace(0, len(y_data)-1, num_peaks).astype(int)
        refined_peaks, refined_amplitudes = find_local_maxima_with_refinement(x_data, y_data, peak_positions)
        
        for peak_idx, amplitude_raw in zip(refined_peaks, refined_amplitudes):
            amplitude = amplitude_raw - baseline
            mean = x_data[peak_idx]
            
            # Estimate gamma from local curvature
            gamma = 0.015  # Reasonable default for NMR Lorentzian
            
            print(f"Fallback peak: pos={mean:.3f}, raw_amp={amplitude_raw:.1f}, corrected_amp={amplitude:.1f}, gamma={gamma:.4f}")
            initial_params.extend([amplitude, mean, gamma])
    
    # Ensure we have exactly num_peaks
    while len(initial_params) < num_peaks * 3:
        # Add synthetic peaks if needed
        remaining = num_peaks - len(initial_params) // 3
        for i in range(remaining):
            pos = (i + 1) * len(y_data) // (remaining + 1)
            amplitude = np.max(y_data) * 0.3 - baseline
            mean = x_data[pos]
            gamma = 0.02
            initial_params.extend([amplitude, mean, gamma])
            print(f"Added synthetic peak: pos={mean:.3f}, amp={amplitude:.1f}, gamma={gamma:.4f}")
    
    return initial_params

def perform_deconvolution(ppm_scale, data, sample_name, start_ppm, end_ppm, num_peaks, max_iterations,
                         deconv_fig, deconv_canvas):
    """Perform spectral deconvolution with Lorentzian peaks."""
    import globals
    
    # Validate and adjust region boundaries
    start_ppm, end_ppm = validate_region_boundaries(ppm_scale, start_ppm, end_ppm)
    
    # Extract region of interest with bounds checking
    try:
        start_idx = np.abs(ppm_scale - start_ppm).argmin()
        end_idx = np.abs(ppm_scale - end_ppm).argmin()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to find region boundaries: {str(e)}")
        return False
    
    # Ensure proper ordering
    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx
    
    # Add safety margin to indices
    start_idx = max(0, start_idx)
    end_idx = min(len(ppm_scale)-1, end_idx)
    
    # Ensure we have enough data points
    if end_idx - start_idx < 10:  # Minimum 10 data points
        messagebox.showerror("Error", "Selected region is too small. Please select a larger region.")
        return False
    
    x_data = ppm_scale[start_idx:end_idx+1]
    y_data = data[start_idx:end_idx+1]
    
    print(f"Deconvolution region: {len(x_data)} points, {x_data[0]:.2f} to {x_data[-1]:.2f} ppm")
    
    if len(x_data) < num_peaks * 3:
        messagebox.showerror("Error", f"Region too small for {num_peaks} peaks. Region has {len(x_data)} points, need at least {num_peaks * 3}.")
        return False
    
    # Estimate baseline using advanced method
    baseline = estimate_baseline_advanced(x_data, y_data)
    print(f"Estimated baseline: {baseline:.1f}")
    
    # Subtract baseline for fitting
    y_data_corrected = y_data - baseline
    
    # Get better initial parameters using refined local maxima
    initial_params = estimate_initial_parameters(x_data, y_data, num_peaks, baseline)
    
    # Set bounds for parameters
    lower_bounds = []
    upper_bounds = []
    
    x_range = x_data.max() - x_data.min()
    
    for i in range(num_peaks):
        # Wider bounds for mean to allow peak positions to adjust
        mean_lower = x_data.min() - 0.1
        mean_upper = x_data.max() + 0.1
        
        # Allow taller peaks
        amp_upper = np.max(y_data_corrected) * 3
        
        # Allow wider peaks - gamma bounds (Lorentzian width parameter)
        gamma_lower = 0.001
        gamma_upper = min(0.2, x_range * 0.4)
        
        lower_bounds.extend([0, mean_lower, gamma_lower])
        upper_bounds.extend([amp_upper, mean_upper, gamma_upper])
    
    try:
        print("Starting curve fitting with Lorentzian peaks...")
        
        # Perform curve fitting on baseline-corrected data with Lorentzian
        popt, pcov = curve_fit(multi_lorentzian, x_data, y_data_corrected, 
                              p0=initial_params, 
                              maxfev=max_iterations,
                              bounds=(lower_bounds, upper_bounds),
                              method='trf')
        
        print("Lorentzian curve fitting completed successfully")
        
        # Calculate individual peaks and integrals - ACCEPT ALL PEAKS
        globals.deconvolution_results = []
        integration_regions = []
        
        for i in range(0, len(popt), 3):
            amplitude = popt[i]
            mean = popt[i+1]
            gamma = popt[i+2]
            
            print(f"Fitted peak {i//3 + 1}: pos={mean:.3f}, amp={amplitude:.1f}, gamma={gamma:.4f}")
            
            # ACCEPT ALL FITTED PEAKS
            individual_lorentzian = lorentzian(x_data, amplitude, mean, gamma)
            individual_lorentzian_with_baseline = individual_lorentzian + baseline
            
            # Find integration boundaries with bounds checking
            start_int_idx, end_int_idx = find_peak_integration_bounds(x_data, individual_lorentzian_with_baseline, baseline)
            
            # Ensure integration indices are valid
            start_int_idx = max(0, start_int_idx)
            end_int_idx = min(len(x_data)-1, end_int_idx)
            
            if start_int_idx >= end_int_idx:
                start_int_idx = max(0, end_int_idx - 1)
                end_int_idx = min(len(x_data)-1, start_int_idx + 1)
            
            # Extract integration region
            x_integrate = x_data[start_int_idx:end_int_idx+1]
            y_peak_region = individual_lorentzian_with_baseline[start_int_idx:end_int_idx+1]
            
            # Calculate integral - USE RAW DATA APPROACH like integration.py
            if len(x_integrate) > 1:
                # Get the corresponding raw data for this integration region
                start_raw_idx = np.abs(x_data - x_integrate[0]).argmin()
                end_raw_idx = np.abs(x_data - x_integrate[-1]).argmin()
                
                # Ensure indices are valid
                start_raw_idx = max(0, start_raw_idx)
                end_raw_idx = min(len(y_data)-1, end_raw_idx)
                
                if start_raw_idx < end_raw_idx:
                    # Use the same summation method as integration.py
                    integral = y_data[start_raw_idx:end_raw_idx+1].sum()
                else:
                    integral = 0
            else:
                integral = 0
            
            # STORE ALL PEAKS
            integration_regions.append({
                'x': x_integrate,
                'y_peak': y_peak_region,
                'y_baseline': np.full_like(y_peak_region, baseline),
                'peak_number': len(globals.deconvolution_results) + 1,
                'integral': integral
            })
            
            globals.deconvolution_results.append({
                "Sample": sample_name,
                "Region": f"{start_ppm:.2f}-{end_ppm:.2f}",
                "Peak": f"Peak_{len(globals.deconvolution_results) + 1}",
                "Center_PPM": mean,
                "Amplitude": amplitude,
                "Width": gamma * 2,  # FWHM for Lorentzian = 2*gamma
                "Integral": integral,
                "Gamma": gamma,
                "Region_Start": start_ppm,
                "Region_End": end_ppm,
                "Integration_Start_PPM": x_data[start_int_idx] if len(x_data) > start_int_idx else start_ppm,
                "Integration_End_PPM": x_data[end_int_idx] if len(x_data) > end_int_idx else end_ppm,
                "Baseline": baseline
            })
        
        # Plot results with integration regions
        plot_deconvolution_results(x_data, y_data, popt, sample_name, 
                                 start_ppm, end_ppm, deconv_fig, deconv_canvas, 
                                 baseline, integration_regions)
        
        return True
        
    except Exception as e:
        error_msg = f"Deconvolution failed: {str(e)}\n\nTry:\n- Adjusting the region boundaries\n- Reducing the number of peaks\n- Increasing max iterations\n\nDebug info: {len(x_data)} points, {num_peaks} peaks"
        messagebox.showerror("Error", error_msg)
        print(f"Deconvolution error details: {e}")
        return False

def plot_deconvolution_results(x_data, y_data, popt, sample_name, 
                             start_ppm, end_ppm, deconv_fig, deconv_canvas, 
                             baseline, integration_regions):
    """Plot deconvolution results with properly shaded integration areas."""
    deconv_fig.clear()
    ax = deconv_fig.add_subplot(111)
    
    gui.setup_plot_style(ax)
    
    # Plot original data
    ax.plot(x_data, y_data, color=gui.Theme.SPECTRUM_COLORS[0], linewidth=2, label='Original Data')
    
    # Plot baseline
    ax.axhline(y=baseline, color=gui.Theme.BASELINE_COLOR, linestyle='--', 
               alpha=0.7, linewidth=1, label=f'Baseline ({baseline:.1e})')
    
    # Plot fitted curve
    fitted_curve = multi_lorentzian(x_data, *popt) + baseline
    ax.plot(x_data, fitted_curve, color=gui.Theme.TEXT_ERROR, linestyle='--', 
            linewidth=2, label='Fitted Curve', alpha=0.8)
    
    # Plot individual peaks
    for i in range(0, len(popt), 3):
        color = gui.Theme.get_deconvolution_color(i // 3)
        individual_peak = lorentzian(x_data, popt[i], popt[i+1], popt[i+2]) + baseline
        peak_name = f"Peak_{i//3 + 1}"
        ax.plot(x_data, individual_peak, color=color, linestyle=':', 
                linewidth=1.5, label=peak_name, alpha=0.8)
        
        # Mark the peak center
        ax.axvline(x=popt[i+1], color=color, linestyle='-', alpha=0.3, linewidth=1)
    
    # SHADE THE INTEGRATION REGIONS
    for region in integration_regions:
        color = gui.Theme.get_deconvolution_color(region['peak_number'] - 1)
        
        # Fill between peak and baseline
        ax.fill_between(region['x'], region['y_baseline'], region['y_peak'],
                       alpha=gui.Theme.INTEGRATION_ALPHA, 
                       color=color,
                       label=f'Peak {region["peak_number"]} Area' if region['peak_number'] == 1 else "")
        
        # Add integral value annotation
        if len(region['x']) > 0:
            mid_x = np.mean(region['x'])
            max_y = np.max(region['y_peak'])
            ax.text(mid_x, max_y * 0.9, f"{region['integral']:.2e}", 
                   fontsize=8, ha='center', va='bottom', color=color, weight='bold',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.7))
    
    ax.set_xlabel("Chemical Shift (ppm)")
    ax.set_ylabel("Intensity")
    ax.set_title(f"Spectral Deconvolution (Lorentzian): {sample_name}\nRegion: {start_ppm:.2f} - {end_ppm:.2f} ppm")
    ax.invert_xaxis()
    ax.legend(fontsize=8)
    deconv_canvas.draw()