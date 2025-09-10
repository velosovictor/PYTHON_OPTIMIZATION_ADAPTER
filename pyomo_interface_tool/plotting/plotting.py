# ============================================================================
# PLOTTING MODULE
# ============================================================================
# Provides general plotting functionalities for simulation results
# Creates subplots for each variable in the dataset

import matplotlib.pyplot as plt

# ============================================================================
# DATASET PLOTTING FUNCTION
# ============================================================================
def plot_dataset(ds):
    # Plots each DataArray in xarray Dataset against primary coordinate
    # Creates subplots with one plot per data variable
    
    num_vars = len(ds.data_vars)
    
    # Create subplots (one per variable)
    fig, axs = plt.subplots(num_vars, 1, figsize=(10, 4*num_vars), squeeze=False)
    
    # Plot each variable
    for idx, (var_name, data_array) in enumerate(ds.data_vars.items()):
        ax = axs[idx, 0]
        
        # Get primary coordinate (usually time)
        coord_name = list(data_array.coords)[0]
        x_coord = ds[coord_name].values
        
        # Create plot with markers and grid
        ax.plot(x_coord, data_array.values, marker='o', linestyle='-')
        ax.set_title(f"{var_name} vs. {coord_name}")
        ax.set_xlabel(coord_name)
        ax.set_ylabel(var_name)
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()