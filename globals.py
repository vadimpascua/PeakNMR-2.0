# --------------------------------------------------
# GLOBAL VARIABLES AND EVENT SYSTEM
# --------------------------------------------------
import pandas as pd
from typing import List, Callable, Any

# Data storage
selected_pdata_dirs = []
spectra = []
peak_limits = pd.DataFrame()
peak_limits_path = None

# Analysis results
integration_results = []
concentration_results = []
binning_results = None
peak_picking_results = []
all_peak_picking_results = []
deconvolution_results = []

# Default parameters
tsp_concentration = 0
binning_step = 0.05
selected_spectra_indices = []

# Event system for cross-tab communication
_event_listeners = {}

def add_event_listener(event_name: str, callback: Callable):
    """Add an event listener for cross-tab communication."""
    if event_name not in _event_listeners:
        _event_listeners[event_name] = []
    _event_listeners[event_name].append(callback)

def trigger_event(event_name: str, *args, **kwargs):
    """Trigger an event and call all registered listeners."""
    if event_name in _event_listeners:
        for callback in _event_listeners[event_name]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Error in event listener for {event_name}: {e}")

def update_spectra(new_spectra):
    """Update spectra and notify all listeners."""
    global spectra
    spectra = new_spectra
    trigger_event('spectra_updated', spectra)

def update_peak_limits(new_peak_limits):
    """Update peak limits and notify all listeners."""
    global peak_limits
    peak_limits = new_peak_limits
    trigger_event('peak_limits_updated', peak_limits)