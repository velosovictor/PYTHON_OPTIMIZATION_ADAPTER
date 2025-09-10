# ============================================================================
# EQUATIONS MODULE
# ============================================================================
# Loads user-defined equations from JSON and creates symbolic expressions
# Defines time variable, unknown functions, parameters, and system equations

import sympy as sp
import os
import json

# ============================================================================
# EQUATION LOADING FUNCTION
# ============================================================================
def load_equations():
    # Loads symbolic equations and constructs symbolic representations
    # Returns time variable, unknown functions, parameters, and equations
    
    # Define symbolic time variable
    t = sp.symbols('t', real=True)
    
    # Load configuration from parameters module (problem-agnostic)
    from .parameters import params_data
    eq_data = params_data
    
    # Create unknown functions (state variables)
    unknown_funcs = []
    for name in eq_data.get("unknown_parameters", []):
        func = sp.Function(name)(t)
        unknown_funcs.append(func)
        globals()[name] = sp.Function(name)
    
    # Build parameter symbols from dictionary
    parameters = {}
    params_dict = eq_data.get("parameters", {})
    for key, val in params_dict.items():
        parameters[key] = sp.symbols(key, real=True)
        globals()[key] = parameters[key]
    
    # Build additional functions (like DAMPING, etc.)
    for func_name in eq_data.get("additional_functions", []):
        globals()[func_name] = sp.Function(func_name)
    
    # Parse equations from string format to symbolic equations
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

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================
t, unknown_funcs, parameters, all_equations = load_equations()
__all__ = ["t", "unknown_funcs", "all_equations"]
