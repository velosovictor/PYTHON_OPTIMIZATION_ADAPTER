# ============================================================================
# SOLVER MODULE
# ============================================================================
# Provides functions for solving Pyomo optimization models
# Handles solver creation, execution, and solution extraction

from pyomo.environ import SolverFactory, value
from .parameters import solver_name
from .equations import unknown_funcs

# ============================================================================
# MODEL SOLVING FUNCTIONS
# ============================================================================
def solve_model(model):
    # Solves the Pyomo model using the configured solver
    # Returns results object after checking termination condition
    
    solver = SolverFactory(solver_name)
    results = solver.solve(model, tee=True)
    
    # Check for optimal solution
    if results.solver.termination_condition != 'optimal':
        raise ValueError(f"Solver terminated with condition: {results.solver.termination_condition}")
    
    return results

def solve_with_parameters(params):
    # Stub function for specialized parameter-based solving
    # Currently unused but available for future extensions
    pass

def extract_solution(model, time_set):
    # Extracts solution values for all unknown functions
    # Returns dictionary mapping function names to solution arrays
    
    sol_dict = {}
    for f in unknown_funcs:
        fname = f.func.__name__
        sol_dict[fname] = [value(getattr(model, fname)[t]) for t in time_set]
    return sol_dict
