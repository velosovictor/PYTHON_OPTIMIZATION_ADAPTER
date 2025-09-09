# ============================================================================
# LIVE PLOTTING MODULE
# ============================================================================
# Provides real-time interactive plotting for streaming simulation data
# Handles plot initialization and continuous updates

import matplotlib
try:
    matplotlib.use('TkAgg')
except Exception as e:
    print("Error setting TkAgg backend:", e)
import matplotlib.pyplot as plt

# Configure interactive plotting
plt.ion()
print("Interactive mode enabled. Backend:", matplotlib.get_backend())

# Global plot state storage
_global_live_plot = None

# ============================================================================
# LIVE PLOTTING FUNCTION
# ============================================================================
def plot_dataset_live(ds):
    # Creates or updates live plot using xarray Dataset
    # Handles both initialization and continuous updates
    
    global _global_live_plot
    
    # Validate input dataset
    if ds is None:
        print("No dataset provided for live plotting.")
        return

    num_vars = len(ds.data_vars)
    if num_vars == 0:
        print("Dataset has no data variables!")
        return

    if _global_live_plot is None:
        # Initialize new live plot
        fig, axs = plt.subplots(num_vars, 1, figsize=(10, 4*num_vars), squeeze=False)
        lines = {}
        coord_names = {}
        
        for idx, (var_name, data_array) in enumerate(ds.data_vars.items()):
            ax = axs[idx, 0]
            
            # Get primary coordinate (time)
            coord_name = list(data_array.coords)[0]
            coord_names[var_name] = coord_name
            
            # Create initial plot
            x_data = ds[coord_name].values
            y_data = ds[var_name].values
            line, = ax.plot(x_data, y_data, marker='o', linestyle='-')
            
            # Configure plot appearance
            ax.set_title(f"{var_name} vs. {coord_name}")
            ax.set_xlabel(coord_name)
            ax.set_ylabel(var_name)
            ax.grid(True)
            ax.legend()
            
            lines[var_name] = line
        
        plt.tight_layout()
        plt.show(block=False)
        _global_live_plot = {"fig": fig, "axs": axs, "lines": lines, "coord_names": coord_names}
        print("Live plot initialized.")
    else:
        # Update existing live plot
        fig = _global_live_plot["fig"]
        axs = _global_live_plot["axs"]
        lines = _global_live_plot["lines"]
        coord_names = _global_live_plot["coord_names"]
        
        # Update data for each variable
        for var_name, data_array in ds.data_vars.items():
            coord_name = coord_names.get(var_name)
            if coord_name is None:
                continue
            
            x_data = ds[coord_name].values
            y_data = ds[var_name].values
            
            if var_name in lines:
                lines[var_name].set_xdata(x_data)
                lines[var_name].set_ydata(y_data)
        
        # Refresh plot axes and canvas
        for ax in axs.flatten():
            ax.relim()
            ax.autoscale_view()
        
        fig.canvas.draw_idle()
        plt.pause(0.1)
        print("Live plot updated.")
