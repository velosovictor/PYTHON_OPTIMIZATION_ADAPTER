# ============================================================================
# SOLVER MODULE
# ============================================================================
# Provides functions for solving Pyomo optimization models
# Handles solver creation, execution, and solution extraction

import os
from pyomo.environ import SolverFactory, value
from .parameters import get_parameter
from .equations import get_equations
from .solver_config import get_scip_path, is_scip_configured

# ============================================================================
# MODEL SOLVING FUNCTIONS
# ============================================================================
def solve_model(model):
    # Solves the Pyomo model using the configured solver
    # Returns results object after checking termination condition
    
    # Configure SCIP solver if needed
    solver_name = get_parameter("solver") or "ipopt"
    if solver_name.lower() == 'scip' and is_scip_configured():
        scip_path = get_scip_path()
        scip_exe = os.path.join(scip_path, "bin", "scip.exe")
        if os.path.exists(scip_exe):
            solver = SolverFactory(solver_name, executable=scip_exe)
        else:
            solver = SolverFactory(solver_name)
    else:
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
    
    # Load equations dynamically
    t, unknown_funcs, parameters, all_equations = get_equations()
    
    sol_dict = {}
    for f in unknown_funcs:
        fname = f.func.__name__
        values = []
        for t in time_set:
            var = getattr(model, fname)[t]
            try:
                val = value(var)
                values.append(val)
            except ValueError as e:
                if "No value for uninitialized" in str(e):
                    print(f"⚠️  Warning: {fname}[{t}] uninitialized, using NaN")
                    values.append(float('nan'))
                else:
                    raise e
        sol_dict[fname] = values
    return sol_dict
