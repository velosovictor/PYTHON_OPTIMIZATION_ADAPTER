"""
Constraint Rules Module

This module provides utility functions for generating constraint rules
used in the Pyomo model. These functions translate discretized symbolic 
equations into callable constraint functions for the optimization model.

Maintenance Notes:
- Each function is documented to ease future modifications.
- Update these functions if the discretization strategy or variable mapping changes.
"""

from pyomo.environ import Constraint
from pyomo.core.expr.sympy_tools import sympy2pyomo_expression
import sympy as sp
from .parameters import dt_value
from .user_data.lookup import lookup_tables

class MySymbolMap:
    def __init__(self):
        self.symbol_map = {}
    def getPyomoSymbol(self, sympy_symbol, default=None):
        # Returns the Pyomo variable mapped to the given sympy_symbol.
        return self.symbol_map.get(sympy_symbol, default)

def generate_constraint_rule(discretized_expr, unknown_funcs, param_mapping, 
                             discrete_parameters=None, time_array=None):
    """
    Generates a Pyomo constraint rule from a discretized Sympy expression.
    
    Parameters:
      discretized_expr : sympy expression
          The discretized equation representing an ODE constraint.
      unknown_funcs : list
          List of unknown functions (symbols) used in the model.
      param_mapping : dict
          Mapping of parameter symbols to their numerical values.
      discrete_parameters : list, optional
          Definitions of extra model variables for MINLP problems.
      time_array : array_like, optional
          Simulation time grid for contextual reference.
    
    Returns:
      A function that, when called with a Pyomo model and index, returns a constraint
      (an equality that should be zero).
    """
    def rule(model, i):
        my_map = MySymbolMap()
        # Map the f_ip1 and f_i symbols to their corresponding Pyomo variables.
        for f in unknown_funcs:
            fname = str(f.func.__name__)
            my_map.symbol_map[sp.Symbol(f"{fname}_ip1")] = getattr(model, fname)[i+1]
            my_map.symbol_map[sp.Symbol(f"{fname}_i")]   = getattr(model, fname)[i]

        # Map parameters (e.g. m, F) into the symbol map.
        for key, val in param_mapping.items():
            my_map.symbol_map[sp.Symbol(key)] = val

        # Map the time step (dt).
        my_map.symbol_map[sp.Symbol("dt")] = dt_value

        # Map lookup values by reading from the model variables for each lookup key.
        for key in lookup_tables.keys():
            my_map.symbol_map[sp.Symbol(f"{key.upper()}_ip1")] = getattr(model, key.lower())[i+1]

        # Map extra model variables if provided.
        if discrete_parameters is not None:
            for var_def in discrete_parameters:
                name = var_def["name"]
                if hasattr(model, name):
                    my_map.symbol_map[sp.Symbol(name)]       = getattr(model, name)[i+1]
                    my_map.symbol_map[sp.Symbol(name+"_ip1")] = getattr(model, name)[i+1]
                    my_map.symbol_map[sp.Symbol(name+"_i")]   = getattr(model, name)[i]

        # Map the time symbol to the actual time value if a time array is provided.
        if time_array is not None:
            my_map.symbol_map[sp.Symbol("t")] = time_array[i]

        # Optional: detect any leftover symbols that haven't been mapped.
        missing_symbols = discretized_expr.free_symbols - set(my_map.symbol_map.keys())
        if missing_symbols:
            raise ValueError(f"Unmapped symbols detected: {missing_symbols}")

        # Convert the Sympy expression into a Pyomo expression.
        pyomo_expr = sympy2pyomo_expression(discretized_expr, my_map)
        return pyomo_expr == 0

    return rule

def generate_logic_constraint_rule(constraint_data):
    """
    Generates a Pyomo constraint rule from a logic constraint definition.
    
    The logic constraint is defined as a dictionary containing:
      - "expression": a string expression to be evaluated.
      - "parameters": (optional) a dictionary of parameters.
      - "variables": (optional) list of variable names to be mapped from the model.
      
    Returns:
      A function that can be used as a constraint rule in the model.
    """
    expr_str = constraint_data["expression"]
    constraint_params = constraint_data.get("parameters", {})
    used_vars = constraint_data.get("variables", [])
    
    def rule(m, i):
        local_dict = {"i": i}
        local_dict.update(constraint_params)
        for var in used_vars:
            local_dict[var] = getattr(m, var)
        return eval(expr_str, {}, local_dict)
    
    return rule
