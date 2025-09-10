# ============================================================================
# UNIFIED PLOTTING MODULE
# ============================================================================
# Consolidates all plotting functionality into a single, clean module
# Handles static plots, live updates, and phase-space visualizations

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# Configure matplotlib backend
try:
    matplotlib.use('TkAgg')
except Exception as e:
    print(f"Warning: Could not set TkAgg backend: {e}")

# Global state for live plotting
_live_plot_state = None

# ============================================================================
# CORE PLOTTING FUNCTIONS
# ============================================================================

def plot_dataset(ds, live=False, mixed=False):
    """
    Unified plotting function for xarray Datasets
    
    Args:
        ds: xarray Dataset with simulation results
        live: bool, if True enables live updating mode
        mixed: bool, if True creates phase-space plot (requires exactly 2 variables)
    """
    if ds is None or len(ds.data_vars) == 0:
        print("Warning: No data to plot")
        return
    
    if mixed:
        _plot_phase_space(ds)
    elif live:
        _plot_live_update(ds)
    else:
        _plot_static(ds)

def _plot_static(ds):
    """Create static plots with subplots for each variable"""
    num_vars = len(ds.data_vars)
    
    # Create subplots layout
    fig, axs = plt.subplots(num_vars, 1, figsize=(10, 4*num_vars), squeeze=False)
    
    for idx, (var_name, data_array) in enumerate(ds.data_vars.items()):
        ax = axs[idx, 0]
        
        # Get time coordinate
        coord_name = list(data_array.coords)[0]
        x_data = ds[coord_name].values
        y_data = data_array.values
        
        # Create plot
        ax.plot(x_data, y_data, marker='o', linestyle='-', linewidth=2, markersize=4)
        ax.set_title(f"{var_name} vs. {coord_name}", fontsize=12, fontweight='bold')
        ax.set_xlabel(coord_name)
        ax.set_ylabel(var_name)
        ax.grid(True, alpha=0.3)
        
        # Add value annotations at key points
        if len(x_data) <= 10:  # Only for small datasets
            for i, (x, y) in enumerate(zip(x_data, y_data)):
                ax.annotate(f'{y:.3f}', (x, y), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=8)
    
    plt.tight_layout()
    plt.show()

def _plot_phase_space(ds):
    """Create phase-space plot (variable vs variable)"""
    var_names = list(ds.data_vars.keys())
    
    if len(var_names) != 2:
        print(f"Warning: Phase plot requires exactly 2 variables, got {len(var_names)}")
        print("Falling back to regular plot...")
        _plot_static(ds)
        return
    
    x_name, y_name = var_names[0], var_names[1]
    x_data = ds[x_name].values
    y_data = ds[y_name].values
    
    # Create phase-space plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot trajectory with gradient coloring
    points = np.array([x_data, y_data]).T
    for i in range(len(points)-1):
        alpha = 0.3 + 0.7 * (i / len(points))  # Fade from start to end
        ax.plot([points[i,0], points[i+1,0]], [points[i,1], points[i+1,1]], 
               'b-', alpha=alpha, linewidth=2)
    
    # Mark start and end points
    ax.plot(x_data[0], y_data[0], 'go', markersize=8, label='Start')
    ax.plot(x_data[-1], y_data[-1], 'ro', markersize=8, label='End')
    
    ax.set_xlabel(x_name, fontsize=12)
    ax.set_ylabel(y_name, fontsize=12)
    ax.set_title(f"Phase Space: {y_name} vs. {x_name}", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.show()

def _plot_live_update(ds):
    """Handle live plotting with continuous updates"""
    global _live_plot_state
    
    num_vars = len(ds.data_vars)
    
    if _live_plot_state is None:
        # Initialize live plot
        plt.ion()
        fig, axs = plt.subplots(num_vars, 1, figsize=(10, 4*num_vars), squeeze=False)
        
        lines = {}
        coord_names = {}
        
        for idx, (var_name, data_array) in enumerate(ds.data_vars.items()):
            ax = axs[idx, 0]
            
            # Get coordinate info
            coord_name = list(data_array.coords)[0]
            coord_names[var_name] = coord_name
            
            # Create initial plot
            x_data = ds[coord_name].values
            y_data = ds[var_name].values
            line, = ax.plot(x_data, y_data, 'b-o', linewidth=2, markersize=4)
            
            # Setup axes
            ax.set_title(f"{var_name} vs. {coord_name} (Live)", fontweight='bold')
            ax.set_xlabel(coord_name)
            ax.set_ylabel(var_name)
            ax.grid(True, alpha=0.3)
            
            lines[var_name] = line
        
        plt.tight_layout()
        plt.show(block=False)
        
        _live_plot_state = {
            "fig": fig, 
            "axs": axs, 
            "lines": lines, 
            "coord_names": coord_names
        }
        print("✅ Live plot initialized")
        
    else:
        # Update existing live plot
        fig = _live_plot_state["fig"]
        axs = _live_plot_state["axs"]
        lines = _live_plot_state["lines"]
        coord_names = _live_plot_state["coord_names"]
        
        # Update each line
        for var_name, data_array in ds.data_vars.items():
            if var_name not in lines:
                continue
                
            coord_name = coord_names[var_name]
            x_data = ds[coord_name].values
            y_data = ds[var_name].values
            
            # Update line data
            lines[var_name].set_data(x_data, y_data)
        
        # Refresh axes limits and redraw
        for ax in axs.flatten():
            ax.relim()
            ax.autoscale_view()
        
        fig.canvas.draw_idle()
        plt.pause(0.01)  # Small pause for smooth animation

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def finalize_live_plot():
    """Close live plotting mode and show final result"""
    global _live_plot_state
    
    if _live_plot_state is not None:
        plt.ioff()
        plt.show(block=True)
        _live_plot_state = None
        print("✅ Live plot finalized")

def reset_live_plot():
    """Reset live plot state for new simulation"""
    global _live_plot_state
    
    if _live_plot_state is not None:
        plt.close(_live_plot_state["fig"])
        _live_plot_state = None
        print("🔄 Live plot reset")

# ============================================================================
# BACKWARDS COMPATIBILITY
# ============================================================================

def plot_dataset_live(ds):
    """Backwards compatibility wrapper for live plotting"""
    plot_dataset(ds, live=True)

def plot_mixed_dataset(ds):
    """Backwards compatibility wrapper for phase-space plotting"""
    plot_dataset(ds, mixed=True)

# ============================================================================
# MODULE INFO
# ============================================================================

__all__ = [
    'plot_dataset',           # Main unified function
    'finalize_live_plot',     # Live plot control
    'reset_live_plot',        # Live plot control
    'plot_dataset_live',      # Backwards compatibility
    'plot_mixed_dataset'      # Backwards compatibility
]
