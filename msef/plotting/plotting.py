"""
Plotting Module

This module provides general plotting functionalities for system simulations.
"""
import matplotlib.pyplot as plt

def plot_dataset(ds):
    """
    Automatically plots each DataArray in an xarray Dataset against its primary coordinate.
    
    Parameters:
      ds : xarray.Dataset
         The dataset containing the solution variables. Each data variable is expected 
         to be one-dimensional with a coordinate (e.g., time).
    """
    # Determine the number of data variables to plot.
    num_vars = len(ds.data_vars)
    
    # Create subplots: one per data variable.
    # If there's just one variable, axs will be a single Axes object.
    fig, axs = plt.subplots(num_vars, 1, figsize=(10, 4*num_vars), squeeze=False)
    
    # Loop over each variable and its corresponding Axes object.
    for idx, (var_name, data_array) in enumerate(ds.data_vars.items()):
        ax = axs[idx, 0]
        # Assume that the first coordinate is the primary coordinate (e.g., "time").
        # Get the name of the coordinate.
        coord_name = list(data_array.coords)[0]
        x_coord = ds[coord_name].values
        
        # Plot the variable versus its coordinate.
        ax.plot(x_coord, data_array.values, marker='o', linestyle='-')
        ax.set_title(f"{var_name} vs. {coord_name}")
        ax.set_xlabel(coord_name)
        ax.set_ylabel(var_name)
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()