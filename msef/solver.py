"""
Solver Module

This module provides functions for creating and executing the solver for the 
Pyomo optimization model. It also includes functionality to extract solutions 
for the unknown functions after solving.

Maintenance Notes:
- Update solver selection logic as needed (for example, switching between ipopt and scip).
- Ensure that the solution extraction logic matches the modeling structure.
"""

from pyomo.environ import SolverFactory, value
from .parameters import solver_name
from .equations import unknown_funcs

def solve_model(model):
    """
    Solves the given Pyomo model using the solver specified in 'solver_name'.

    Steps:
      1. Create a SolverFactory instance based on 'solver_name'.
      2. Solve the model, printing solver output to the console.
      3. Check if the solver terminated successfully; raise an error otherwise.
      4. Return the solver results object.
    """
    solver = SolverFactory(solver_name)
    results = solver.solve(model, tee=True)
    if results.solver.termination_condition != 'optimal':
        raise ValueError(f"Solver terminated with condition: {results.solver.termination_condition}")
    return results

def solve_with_parameters(params):
    """
    An example stub function to demonstrate how parameters might be passed 
    to a specialized solve routine. Currently unused.
    """
    pass

def extract_solution(model, time_set):
    """
    Extracts solution values for each unknown function over the given time_set.
    Returns a dictionary mapping function names to lists of values.
    """
    sol_dict = {}
    for f in unknown_funcs:
        fname = f.func.__name__
        sol_dict[fname] = [value(getattr(model, fname)[t]) for t in time_set]
    return sol_dict
