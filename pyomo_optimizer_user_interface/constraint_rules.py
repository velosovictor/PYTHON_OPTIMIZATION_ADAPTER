# ============================================================================
# CONSTRAINT RULES MODULE
# ============================================================================
# Provides utility functions for generating Pyomo constraint rules
# Translates discretized symbolic equations into callable constraints

from pyomo.environ import Constraint
from pyomo.core.expr.sympy_tools import sympy2pyomo_expression
import sympy as sp
from .parameters import get_parameter
from .parameters import get_lookup_tables

# ============================================================================
# SYMBOL MAPPING CLASS
# ============================================================================
class MySymbolMap:
    # Maps Sympy symbols to Pyomo variables for expression conversion
    def __init__(self):
        self.symbol_map = {}
    
    def getPyomoSymbol(self, sympy_symbol, default=None):
        # Returns the Pyomo variable mapped to the given Sympy symbol
        return self.symbol_map.get(sympy_symbol, default)

# ============================================================================
# CONSTRAINT GENERATION FUNCTIONS
# ============================================================================
def generate_constraint_rule(discretized_expr, unknown_funcs, param_mapping, 
                             discrete_parameters=None, time_array=None):
    # Generates Pyomo constraint rule from discretized Sympy expression
    # Maps symbols to Pyomo variables and creates constraint function
    
    def rule(model, i):
        my_map = MySymbolMap()
        
        # Map unknown function symbols (f_i+1 and f_i)
        for f in unknown_funcs:
            fname = str(f.func.__name__)
            my_map.symbol_map[sp.Symbol(f"{fname}_ip1")] = getattr(model, fname)[i+1]
            my_map.symbol_map[sp.Symbol(f"{fname}_i")]   = getattr(model, fname)[i]

        # Map parameter symbols to their values
        for key, val in param_mapping.items():
            my_map.symbol_map[sp.Symbol(key)] = val

        # Map time step
        dt_value = get_parameter("dt_value")
        my_map.symbol_map[sp.Symbol("dt")] = dt_value

        # Map lookup table symbols (loaded dynamically)
        lookup_tables = get_lookup_tables()
        for key in lookup_tables.keys():
            my_map.symbol_map[sp.Symbol(f"{key.upper()}_ip1")] = getattr(model, key.lower())[i+1]

        # Map discrete variables if present
        if discrete_parameters is not None:
            for var_def in discrete_parameters:
                name = var_def["name"]
                if hasattr(model, name):
                    my_map.symbol_map[sp.Symbol(name)]       = getattr(model, name)[i+1]
                    my_map.symbol_map[sp.Symbol(name+"_ip1")] = getattr(model, name)[i+1]
                    my_map.symbol_map[sp.Symbol(name+"_i")]   = getattr(model, name)[i]

        # Map time symbol if time array provided
        if time_array is not None:
            my_map.symbol_map[sp.Symbol("t")] = time_array[i]

        # Check for unmapped symbols
        missing_symbols = discretized_expr.free_symbols - set(my_map.symbol_map.keys())
        if missing_symbols:
            raise ValueError(f"Unmapped symbols detected: {missing_symbols}")

        # Convert to Pyomo expression and return constraint
        pyomo_expr = sympy2pyomo_expression(discretized_expr, my_map)
        return pyomo_expr == 0

    return rule

def generate_logic_constraint_rule(constraint_data):
    # Generates Pyomo constraint rule from logic constraint definition
    # Used for custom constraint expressions with parameters and variables
    
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
