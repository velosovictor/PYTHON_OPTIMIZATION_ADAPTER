# ============================================================================
# MAIN EXECUTION MODULE
# ============================================================================
# This module executes the MSEF simulation framework with two modes:
# 1. Monolithic: Builds and solves the full model at once
# 2. Timewise: Step-wise solution with real-time parameter updates

from pyomo.environ import TransformationFactory
from .build_global_model import build_global_model
from .solver import solve_model, extract_solution
from .postprocessing import package_solution
from .plotting import plot_dataset, plot_mixed_dataset
from .parameters import dt_value, final_time, minlp_enabled, params_data, initialize_with_data_folder
from .build_sequential_model import run_build_sequential_model
from .optimization import analyze_optimization_results
from .constraint_analyzer import analyze_constraint_structure, analyze_without_logic, suggest_missing_constraints
from .computational_resource_calculator import analyze_computational_requirements
import matplotlib.pyplot as plt

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================
def run(data_folder=None):
    """
    Main execution function that chooses between monolithic and timewise modes
    
    Args:
        data_folder (str, optional): Path to folder containing object_data.json and other config files.
                                   If None, uses current working directory.
    """
    import os
    
    # Set default data folder to current working directory if not specified
    if data_folder is None:
        data_folder = os.getcwd()
    
    # Initialize parameters with the specified data folder
    initialize_with_data_folder(data_folder)
    
    # Dynamic loader functionality is now integrated into parameters module
    
    print(f"\n🎯 PYOMO OPTIMIZER USER INTERFACE")
    print("=" * 50)
    print(f"📁 Using data folder: {data_folder}")
    
    # Analyze the constraint structure according to the theory
    system_type = analyze_constraint_structure()
    degrees_without_logic = analyze_without_logic()
    suggest_missing_constraints(degrees_without_logic)
    
    solve_mode = params_data.get("solve_mode", "monolithic")
    
    if solve_mode == "monolithic":
        # Monolithic approach: build entire time horizon at once
        model, tau = build_global_model()
        solve_model(model)
        
        # Analyze optimization results
        optimization_config = params_data.get("optimization", {"enabled": False})
        analyze_optimization_results(model, optimization_config)
        
        # Extract solution and create dataset
        sol_dict = extract_solution(model, model.T)
        ds = package_solution(tau, sol_dict, dt_value, final_time)
        
        # Display results
        plot_dataset(ds)
        plt.ioff()
        plt.show(block=True)
        plot_mixed_dataset(ds)
    
    else:
        # Timewise approach: step-by-step simulation with live updates
        tau, sol_dict = run_build_sequential_model(plot_in_real_time=True)
        
        # Package and display results
        ds = package_solution(tau, sol_dict, dt_value, final_time, "Timewise results")
        plot_dataset(ds)
        plot_mixed_dataset(ds)

# ============================================================================
# SCRIPT EXECUTION
# ============================================================================
if __name__ == "__main__":
    import sys
    
    # Check if user provided a data folder argument
    if len(sys.argv) > 1:
        data_folder = sys.argv[1]
        print(f"🎯 Using external data folder: {data_folder}")
        run(data_folder=data_folder)
    else:
        print("🎯 Using default configuration")
        run()
