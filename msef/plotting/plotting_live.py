"""
Plotting Live Module

This module provides real-time or interactive plotting capabilities
for streaming or live-updated simulation data.
"""
import matplotlib
try:
    matplotlib.use('TkAgg')
except Exception as e:
    print("Error setting TkAgg backend:", e)
import matplotlib.pyplot as plt

# Turn on interactive mode
plt.ion()
print("Interactive mode enabled. Backend:", matplotlib.get_backend())

_global_live_plot = None

def plot_dataset_live(ds):
    """
    Creates or updates a live plot using an xarray Dataset.
    This function unifies the initialization and updating routines for live visualization.

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset containing the solution variables.
    """
    global _global_live_plot
    if ds is None:
        print("No dataset provided for live plotting.")
        return

    # Ensure the dataset has at least one data variable.
    num_vars = len(ds.data_vars)
    if num_vars == 0:
        print("Dataset has no data variables!")
        return

    if _global_live_plot is None:
        # Create a new live plot.
        fig, axs = plt.subplots(num_vars, 1, figsize=(10, 4*num_vars), squeeze=False)
        lines = {}
        coord_names = {}
        for idx, (var_name, data_array) in enumerate(ds.data_vars.items()):
            ax = axs[idx, 0]
            # Assume the first coordinate is the primary coordinate (e.g., "time")
            coord_name = list(data_array.coords)[0]
            coord_names[var_name] = coord_name
            x_data = ds[coord_name].values
            y_data = ds[var_name].values
            line, = ax.plot(x_data, y_data, marker='o', linestyle='-')
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
        # Update the existing live plot.
        fig = _global_live_plot["fig"]
        axs = _global_live_plot["axs"]
        lines = _global_live_plot["lines"]
        coord_names = _global_live_plot["coord_names"]
        for var_name, data_array in ds.data_vars.items():
            coord_name = coord_names.get(var_name)
            if coord_name is None:
                continue
            x_data = ds[coord_name].values
            y_data = ds[var_name].values
            if var_name in lines:
                lines[var_name].set_xdata(x_data)
                lines[var_name].set_ydata(y_data)
        for ax in axs.flatten():
            ax.relim()
            ax.autoscale_view()
        fig.canvas.draw_idle()
        plt.pause(0.1)
        print("Live plot updated.")
