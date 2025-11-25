import gui
import globals
from tabs.dataset_tab import create_dataset_tab
from tabs.spectra_tab import create_spectra_tab, update_spectra_list
from tabs.concentration_tab import create_concentration_tab
from tabs.binning_tab import create_binning_tab
from tabs.integration_tab import create_integration_tab
from tabs.peak_picking_tab import create_peak_picking_tab, update_peak_picking_spectra_list
from tabs.deconvolution_tab import create_deconvolution_tab, update_deconvolution_spectra_list
from tabs.reporting_tab import create_reporting_tab

class NMRApplication:
    def __init__(self):
        self.root = None
        self.status_label = None
        self.tab_control = None
        self.spectra_listbox = None
        self.peak_picking_spectra_listbox = None
        self.deconvolution_spectra_listbox = None
        
    def setup_event_handlers(self):
        """Set up event handlers for cross-tab communication."""
        # When spectra are updated, update all listboxes
        globals.add_event_listener('spectra_updated', self.on_spectra_updated)
        
        # When peak limits are updated, notify relevant tabs
        globals.add_event_listener('peak_limits_updated', self.on_peak_limits_updated)
    
    def on_spectra_updated(self, spectra):
        """Handle spectra updated event."""
        print(f"Spectra updated: {len(spectra)} spectra loaded")
        
        # Update status label
        if self.status_label:
            self.status_label.config(text=f"Loaded {len(spectra)} spectra")
        
        # Update all listboxes
        if self.spectra_listbox:
            update_spectra_list(self.spectra_listbox)
        
        if self.peak_picking_spectra_listbox:
            update_peak_picking_spectra_list(self.peak_picking_spectra_listbox)
            
        if self.deconvolution_spectra_listbox:
            update_deconvolution_spectra_list(self.deconvolution_spectra_listbox)
    
    def on_peak_limits_updated(self, peak_limits):
        """Handle peak limits updated event."""
        print(f"Peak limits updated: {len(peak_limits)} peaks defined")
    
    def run(self):
        """Run the application."""
        # Create main application window
        self.root = gui.create_main_window()
        
        # Create header and get status label
        self.status_label = gui.create_header(self.root)
        
        # Create main frame with tabs
        self.tab_control = gui.create_main_frame(self.root)
        
        # Setup event handlers
        self.setup_event_handlers()
        
        # Create all tabs and store references to listboxes
        dataset_tab = create_dataset_tab(self.tab_control, self.status_label)
        spectra_tab, self.spectra_listbox = create_spectra_tab(self.tab_control)
        concentration_tab = create_concentration_tab(self.tab_control)
        binning_tab = create_binning_tab(self.tab_control)
        integration_tab = create_integration_tab(self.tab_control)
        peak_picking_tab, self.peak_picking_spectra_listbox = create_peak_picking_tab(self.tab_control)
        deconvolution_tab, self.deconvolution_spectra_listbox = create_deconvolution_tab(self.tab_control)
        reporting_tab = create_reporting_tab(self.tab_control)
        
        # Start the application
        self.root.mainloop()

def main():
    app = NMRApplication()
    app.run()

if __name__ == "__main__":
    main()