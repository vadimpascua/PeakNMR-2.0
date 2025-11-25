import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import sv_ttk

class Theme:
    """Centralized theme and color management for the entire application."""
    
    # Application colors
    BACKGROUND_PRIMARY = '#404040'
    BACKGROUND_SECONDARY = '#505050'
    BACKGROUND_TERTIARY = '#2b2b2b'
    BACKGROUND_ELEVATED = '#606060'
    
    # Text colors
    TEXT_PRIMARY = 'white'
    TEXT_SECONDARY = '#CCCCCC'
    TEXT_ACCENT = '#0078D7'
    TEXT_SUCCESS = '#2E8B57'
    TEXT_ERROR = '#FF6B6B'
    
    # UI element colors
    BORDER_COLOR = 'white'
    BUTTON_BACKGROUND = '#555555'
    BUTTON_HOVER = '#666666'
    TAB_SELECTED = '#0078D7'
    TAB_UNSELECTED = '#555555'
    
    # Plot colors
    PLOT_BACKGROUND = '#2b2b2b'
    PLOT_AXES = 'white'
    PLOT_GRID = '#444444'
    
    # Spectrum plot colors
    SPECTRUM_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Peak region colors
    PEAK_REGION_FILL = '#ff7f0e'
    PEAK_REGION_ALPHA = 0.3
    
    # Peak detection colors
    PEAK_MARKER_COLOR = 'red'
    BASELINE_COLOR = 'orange'
    INTEGRATION_FILL = 'green'
    INTEGRATION_ALPHA = 0.3
    
    # Deconvolution colors
    DECONVOLUTION_COLORS = ['green', 'orange', 'purple', 'brown', 'pink', 
                           'gray', 'olive', 'cyan']
    
    @classmethod
    def get_spectrum_color(cls, index):
        """Get a spectrum color by index with cycling."""
        return cls.SPECTRUM_COLORS[index % len(cls.SPECTRUM_COLORS)]
    
    @classmethod
    def get_deconvolution_color(cls, index):
        """Get a deconvolution color by index with cycling."""
        return cls.DECONVOLUTION_COLORS[index % len(cls.DECONVOLUTION_COLORS)]
    
    @classmethod
    def setup_matplotlib_style(cls):
        """Set up matplotlib with the application theme."""
        plt.rcParams.update({
            'figure.facecolor': cls.PLOT_BACKGROUND,
            'axes.facecolor': cls.PLOT_BACKGROUND,
            'axes.edgecolor': cls.PLOT_AXES,
            'axes.labelcolor': cls.PLOT_AXES,
            'axes.titlecolor': cls.PLOT_AXES,
            'xtick.color': cls.PLOT_AXES,
            'ytick.color': cls.PLOT_AXES,
            'grid.color': cls.PLOT_GRID,
            'legend.facecolor': cls.BACKGROUND_SECONDARY,
            'legend.edgecolor': cls.BORDER_COLOR,
            'legend.labelcolor': cls.TEXT_PRIMARY,
            'text.color': cls.TEXT_PRIMARY
        })

def setup_theme():
    """Configure the application theme using centralized colors."""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure colors using Theme class
    style.configure('TFrame', background=Theme.BACKGROUND_PRIMARY)
    style.configure('TLabel', background=Theme.BACKGROUND_PRIMARY, 
                   foreground=Theme.TEXT_PRIMARY, font=('Segoe UI', 10))
    style.configure('TButton', background=Theme.BUTTON_BACKGROUND, 
                   foreground=Theme.TEXT_PRIMARY, font=('Segoe UI', 10),
                   borderwidth=1, focuscolor='none')
    style.configure('TNotebook', background=Theme.BACKGROUND_PRIMARY, borderwidth=0)
    style.configure('TNotebook.Tab', background=Theme.TAB_UNSELECTED, 
                   foreground=Theme.TEXT_PRIMARY, padding=[10, 5], font=('Segoe UI', 10))
    style.map('TNotebook.Tab', background=[('selected', Theme.TAB_SELECTED)])
    style.configure('TEntry', fieldbackground=Theme.BACKGROUND_SECONDARY, 
                   foreground=Theme.TEXT_PRIMARY)
    style.configure('TProgressbar', background=Theme.TEXT_ACCENT, 
                   troughcolor=Theme.BACKGROUND_PRIMARY)
    
    # Configure treeview
    style.configure("Treeview", 
                   background=Theme.BACKGROUND_SECONDARY,
                   foreground=Theme.TEXT_PRIMARY,
                   fieldbackground=Theme.BACKGROUND_SECONDARY,
                   borderwidth=0,
                   font=('Segoe UI', 9))
    style.configure("Treeview.Heading", 
                   background=Theme.BACKGROUND_ELEVATED,
                   foreground=Theme.TEXT_PRIMARY,
                   borderwidth=0,
                   font=('Segoe UI', 9, 'bold'))
    style.map('Treeview', background=[('selected', Theme.TAB_SELECTED)])
    
    # Configure LabelFrame
    style.configure('TLabelframe', background=Theme.BACKGROUND_PRIMARY,
                   foreground=Theme.TEXT_PRIMARY)
    style.configure('TLabelframe.Label', background=Theme.BACKGROUND_PRIMARY,
                   foreground=Theme.TEXT_PRIMARY)
    
    # Setup matplotlib style
    Theme.setup_matplotlib_style()

def create_main_window():
    """Create and configure the main application window."""
    root = tk.Tk()
    root.title("Bruker 1D NMR Analysis Suite")
    root.geometry("1400x900")
    root.configure(bg=Theme.BACKGROUND_PRIMARY)
    
    setup_theme()
    sv_ttk.set_theme("dark")
    
    return root

def create_header(parent):
    """Create the application header."""
    header_frame = ttk.Frame(parent)
    header_frame.pack(fill='x', padx=20, pady=10)

    title_main = tk.Label(header_frame, text="Bruker NMR 1D Analysis Suite", 
                         font=('Segoe UI', 20, "bold"), bg=Theme.BACKGROUND_PRIMARY, 
                         fg=Theme.TEXT_PRIMARY)
    title_main.pack(side='left')

    status_label = tk.Label(header_frame, text="Ready to process data", 
                           font=('Segoe UI', 10), bg=Theme.BACKGROUND_PRIMARY, 
                           fg=Theme.TEXT_SECONDARY)
    status_label.pack(side='right')
    
    return status_label

def create_main_frame(parent):
    """Create the main frame with tabs."""
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill='both', expand=True, padx=20, pady=10)

    tab_control = ttk.Notebook(main_frame)
    tab_control.pack(expand=1, fill="both")
    
    return tab_control

def configure_listbox(listbox):
    """Configure a listbox with theme colors."""
    listbox.configure(bg=Theme.BACKGROUND_SECONDARY, fg=Theme.TEXT_PRIMARY,
                     selectbackground=Theme.TAB_SELECTED, font=('Segoe UI', 10))

def create_themed_label(parent, text, **kwargs):
    """Create a label with theme colors."""
    return tk.Label(parent, text=text, bg=Theme.BACKGROUND_PRIMARY, 
                   fg=Theme.TEXT_PRIMARY, **kwargs)

def create_themed_button(parent, text, command, **kwargs):
    """Create a button with theme colors."""
    return ttk.Button(parent, text=text, command=command, **kwargs)

def create_themed_frame(parent, **kwargs):
    """Create a frame with theme colors."""
    return ttk.Frame(parent, **kwargs)

def create_themed_labelframe(parent, text, **kwargs):
    """Create a labelframe with theme colors."""
    return ttk.LabelFrame(parent, text=text, **kwargs)

def setup_plot_style(ax):
    """Set up consistent plot styling using theme colors."""
    ax.set_facecolor(Theme.PLOT_BACKGROUND)
    ax.tick_params(colors=Theme.PLOT_AXES)
    ax.xaxis.label.set_color(Theme.PLOT_AXES)
    ax.yaxis.label.set_color(Theme.PLOT_AXES)
    ax.spines['bottom'].set_color(Theme.PLOT_AXES)
    ax.spines['top'].set_color(Theme.PLOT_AXES) 
    ax.spines['right'].set_color(Theme.PLOT_AXES)
    ax.spines['left'].set_color(Theme.PLOT_AXES)
    ax.title.set_color(Theme.TEXT_PRIMARY)