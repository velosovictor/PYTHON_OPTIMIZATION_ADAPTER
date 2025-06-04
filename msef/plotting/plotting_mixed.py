"""
Plotting Mixed Module

This module provides specialized plotting functionalities for handling
mixed or combined data types, enabling advanced visualizations.
"""
import matplotlib.pyplot as plt

def plot_mixed_dataset(ds):
    """
    Plots two unknown functions from an xarray Dataset against each other in one figure.
    Expects the dataset 'ds' to have exactly two data variables. The first data variable 
    is used as the x-axis and the second as the y-axis.
    
    Parameters:
      ds : xarray.Dataset
         The dataset containing the solution variables.
         For example, if ds has keys "x" and "y", then "x" will be the abscissa and "y" the ordinate.
    """
    # Get the list of data variable names.
    var_names = list(ds.data_vars.keys())
    if len(var_names) != 2:
        raise ValueError("Dataset must contain exactly two data variables for a mixed plot.")
    
    x_name = var_names[0]
    y_name = var_names[1]
    
    # Option: you can choose a specific coordinate if needed. Here we simply use the data.
    x_data = ds[x_name].values
    y_data = ds[y_name].values

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x_data, y_data, marker='o', linestyle='-')
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name)
    ax.set_title(f"Mixed Plot: {y_name} vs. {x_name}")
    ax.grid(True)
    plt.tight_layout()
    plt.show()
