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
from .plotting.plotting import plot_dataset
from .plotting.plotting_mixed import plot_mixed_dataset
from .parameters import dt_value, final_time, minlp_enabled, params_data
from .build_sequential_model import run_build_sequential_model
from .optimization import analyze_optimization_results
from .constraint_analysis import print_system_analysis
from .constraint_analyzer import analyze_constraint_structure, analyze_without_logic, suggest_missing_constraints
from .problem_selector import get_current_problem_info
import matplotlib.pyplot as plt

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================
def run():
    # Main execution function that chooses between monolithic and timewise modes
    
    # Show current problem info
    problem_num, problem_desc = get_current_problem_info()
    print(f"\n🎯 CURRENT PROBLEM: {problem_num} - {problem_desc}")
    
    # Analyze the constraint structure according to the theory
    system_type = analyze_constraint_structure()
    degrees_without_logic = analyze_without_logic()
    suggest_missing_constraints(degrees_without_logic)
    
    solve_mode = params_data.get("solve_mode", "monolithic")
    
    if solve_mode == "monolithic":
        # Analyze constraint structure first
        time_steps = len(range(0, int(final_time / dt_value) + 1))
        analysis, constraint_status = print_system_analysis(time_steps)
        
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
    run()
