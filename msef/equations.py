"""
Equations Module

This module loads user-defined equations from a JSON file and creates symbolic expressions
for the simulation. It defines:
  - t: the symbolic variable for time.
  - unknown_funcs: a list of symbolic functions representing state variables.
  - parameters: symbolic representations of simulation parameters.
  - additional_functions: extra functions required in the equations.
  - all_equations: the list of system equations (as Sympy Eq objects).

Maintenance Notes:
- Update the JSON file (user_data/equations.json) or this module when system equations change.
- Ensure that the symbolic definitions here are consistent with the rest of the code.
"""

import sympy as sp
import os
import json

def load_equations():
    """
    Loads symbolic equations and constructs unknown functions, parameters, and additional functions from a JSON file.
    
    Returns
    -------
    t : sympy.Symbol
        The symbolic time variable.
    unknown_funcs : list
        List of symbolic expressions representing state variables.
    parameters : dict
        Dictionary mapping parameter names to sympy symbols.
    all_equations : list
        List of sympy Eq objects representing the system equations.
    """
    # Define the symbolic variable for time.
    t = sp.symbols('t', real=True)
    
    # Path to the JSON file
    EQ_FILE = os.path.join(os.path.dirname(__file__), "user_data", "object_data.json")
    with open(EQ_FILE, "r") as f:
        eq_data = json.load(f)
    
    unknown_funcs = []
    for name in eq_data.get("unknown_parameters", []):
        func = sp.Function(name)(t)
        unknown_funcs.append(func)
        globals()[name] = sp.Function(name)
    
    # Build parameters from the nested dictionary.
    parameters = {}
    params_dict = eq_data.get("parameters", {})  # Now a dictionary
    for key, val in params_dict.items():
        parameters[key] = sp.symbols(key, real=True)
        globals()[key] = parameters[key]
    
    # Build additional functions.
    for func_name in eq_data.get("additional_functions", []):
        globals()[func_name] = sp.Function(func_name)
    
    local_dict = {"t": t, "diff": sp.diff}
    all_equations = []
    for eq_str in eq_data["equations"]:
        if "=" in eq_str:
            lhs_str, rhs_str = eq_str.split("=")
            lhs = sp.sympify(lhs_str, locals=local_dict)
            rhs = sp.sympify(rhs_str, locals=local_dict)
            eq = sp.Eq(lhs, rhs)
        else:
            expr = sp.sympify(eq_str, locals=local_dict)
            eq = sp.Eq(expr, 0)
        all_equations.append(eq)
        
    return t, unknown_funcs, parameters, all_equations

t, unknown_funcs, parameters, all_equations = load_equations()
__all__ = ["t", "unknown_funcs", "all_equations"]
