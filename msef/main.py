"""
Main Module

This module executes the simulation framework. This file supports two modes of operation:
1. Monolithic approach: Builds and solves the full model at once.
2. Timewise simulation: Step-wise solution with real-time parameter updates.

It also handles postprocessing, plotting, and insertion into the database.
"""

from pyomo.environ import TransformationFactory
from .build_global_model import build_global_model      # Builds the full optimization model for monolithic approach.
from .solver import solve_model, extract_solution  # Solves the model and extracts the solution.
from .postprocessing import package_solution  # Packages the solution data.
from .plotting.plotting import plot_dataset  # Standard plotting routine.
from .plotting.plotting_mixed import plot_mixed_dataset  # Mixed plot for two key variables.
from .parameters import dt_value, final_time, minlp_enabled, params_data
# Removed the old logic definitions import.
from .build_sequential_model import run_build_sequential_model  # Runs simulation step-by-step.
import matplotlib.pyplot as plt

def run():
    """
    Main execution function.

    Chooses between the monolithic and timewise simulation modes based on configuration.
    """
    # Determine the solve mode from configuration parameters.
    solve_mode = params_data.get("solve_mode", "monolithic")
    
    if solve_mode == "monolithic":
        # ---------------------------------------------
        # MONOLITHIC APPROACH
        # ---------------------------------------------
        # Build the full model and time grid.
        model, tau = build_global_model()
        
        # Solve the full model.
        solve_model(model)
        
        # Extract the solution and package the data.
        sol_dict = extract_solution(model, model.T)
        ds = package_solution(tau, sol_dict, dt_value, final_time)
  
        # Plot the dataset using standard plotting routines.
        plot_dataset(ds)
        
        # End interactive plotting mode and wait for window closure.
        plt.ioff()
        plt.show(block=True)
        plot_mixed_dataset(ds)
    
    else:
        # ---------------------------------------------
        # TIMEWISE SIMULATION
        # ---------------------------------------------
        # Run simulation step-by-step with live parameter updates.
        tau, sol_dict = run_build_sequential_model(plot_in_real_time=True)
        
        # Package the solution for postprocessing.
        ds = package_solution(tau, sol_dict, dt_value, final_time, "Timewise results")
        
        # Plot the dataset using standard plotting routines.
        plot_dataset(ds)
        # Additionally, create a mixed plot when exactly two key variables are available.
        plot_mixed_dataset(ds)

# Run the simulation if this script is executed directly.
if __name__ == "__main__":
    run()
