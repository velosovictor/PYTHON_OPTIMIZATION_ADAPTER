# ============================================================================
# MIXED PLOTTING MODULE
# ============================================================================
# Provides specialized plotting for phase-space and variable-vs-variable plots
# Creates plots of one variable against another (e.g., position vs velocity)

import matplotlib.pyplot as plt

# ============================================================================
# MIXED DATASET PLOTTING FUNCTION
# ============================================================================
def plot_mixed_dataset(ds):
    # Plots two variables against each other in phase space
    # Requires exactly two data variables in the dataset
    
    var_names = list(ds.data_vars.keys())
    if len(var_names) != 2:
        raise ValueError("Dataset must contain exactly two data variables for a mixed plot.")
    
    x_name = var_names[0]
    y_name = var_names[1]
    
    # Extract data arrays
    x_data = ds[x_name].values
    y_data = ds[y_name].values

    # Create phase space plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x_data, y_data, marker='o', linestyle='-')
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name)
    ax.set_title(f"Phase Space: {y_name} vs. {x_name}")
    ax.grid(True)
    
    plt.tight_layout()
    plt.show()
