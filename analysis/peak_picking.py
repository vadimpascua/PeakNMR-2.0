import numpy as np
from scipy.signal import find_peaks

def detect_peaks(ppm_scale, data, sample_name, height, distance, prominence, baseline_threshold):
    """Detect peaks in spectrum with intelligent integration."""
    peaks, properties = find_peaks(data, height=height, distance=distance, prominence=prominence)
    
    peak_results = []
    
    for i, peak_idx in enumerate(peaks):
        ppm_value = ppm_scale[peak_idx]
        intensity = data[peak_idx]
        
        # Estimate baseline around this peak
        baseline = estimate_baseline(ppm_scale, data, peak_idx)
        
        # Find peak boundaries where it intersects baseline
        left_bound, right_bound = find_peak_boundaries(ppm_scale, data, peak_idx, baseline, baseline_threshold)
        
        # Calculate integral above baseline
        peak_region = data[left_bound:right_bound+1]
        baseline_region = np.full_like(peak_region, baseline)
        integral = np.sum(peak_region - baseline_region)
        
        # Store peak width information
        peak_width_ppm = ppm_scale[left_bound] - ppm_scale[right_bound]
        
        peak_results.append({
            "Sample": sample_name,
            "Peak": f"Peak_{i+1}",
            "PPM": ppm_value,
            "Intensity": intensity,
            "Integral": integral,
            "Baseline": baseline,
            "Start_PPM": ppm_scale[left_bound],
            "End_PPM": ppm_scale[right_bound],
            "Width_PPM": abs(peak_width_ppm),
            "Index": peak_idx
        })
    
    return peak_results

def estimate_baseline(ppm_scale, data, peak_idx, window_size=50):
    """
    Estimate baseline around a peak by taking the average of data points
    on both sides of the peak, excluding the peak region itself.
    """
    # Define regions to the left and right of the peak for baseline estimation
    left_start = max(0, peak_idx - window_size * 2)
    left_end = max(0, peak_idx - window_size)
    
    right_start = min(len(data)-1, peak_idx + window_size)
    right_end = min(len(data)-1, peak_idx + window_size * 2)
    
    # Calculate baseline as average of left and right regions
    left_baseline = np.mean(data[left_start:left_end]) if left_end > left_start else data[peak_idx]
    right_baseline = np.mean(data[right_start:right_end]) if right_end > right_start else data[peak_idx]
    
    baseline = (left_baseline + right_baseline) / 2
    
    return baseline

def find_peak_boundaries(ppm_scale, data, peak_idx, baseline, prominence_threshold=0.01):
    """
    Find where the peak intersects with the baseline by scanning left and right
    from the peak center until we reach the baseline level.
    """
    peak_height = data[peak_idx] - baseline
    
    # Threshold for considering we've reached the baseline (percentage of peak height)
    threshold = baseline + prominence_threshold * peak_height
    
    # Scan left from peak
    left_bound = peak_idx
    for i in range(peak_idx, max(0, peak_idx - 500), -1):
        if data[i] <= threshold or i == 0:
            left_bound = i
            break
    
    # Scan right from peak
    right_bound = peak_idx
    for i in range(peak_idx, min(len(data)-1, peak_idx + 500)):
        if data[i] <= threshold or i == len(data)-1:
            right_bound = i
            break
    
    return left_bound, right_bound