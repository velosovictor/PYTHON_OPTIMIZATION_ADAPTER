# ============================================================================
# DISCRETE LOGIC MODULE
# ============================================================================
# Reads discrete restrictions from JSON and converts to GDP constraints
# Uses Generalized Disjunctive Programming for logic-based optimization

import os
import json
import sympy as sp
from pyomo.gdp import Disjunction
from pyomo.core.expr.sympy_tools import sympy2pyomo_expression
from pyomo.environ import Var
from .parameters import param_mapping, logic_parameters

# ============================================================================
# LOGIC SYMBOL MAPPING CLASS
# ============================================================================
class LogicSymbolMap:
    # Maps Sympy symbols to Pyomo variables for logic expressions
    def __init__(self, model, index):
        self.model = model
        self.index = index
        self.symbol_map = {}
        
        # Map user-defined variables (skip internal piecewise variables)
        for comp in model.component_objects(Var, active=True):
            if comp.name.startswith("PW_"):
                continue
            
            if comp.is_indexed():
                if index in comp.index_set():
                    self.symbol_map[sp.symbols(comp.name)] = comp[index]
            else:
                self.symbol_map[sp.symbols(comp.name)] = comp
        
        # Map parameters and logic parameters
        for key, value in param_mapping.items():
            self.symbol_map[sp.symbols(key)] = value
        for key, value in logic_parameters.items():
            self.symbol_map[sp.symbols(key)] = value

    def getPyomoSymbol(self, sympy_symbol, default=None):
        # Returns Pyomo variable or parameter for given Sympy symbol
        return self.symbol_map.get(sympy_symbol, default)

# ============================================================================
# LOGIC EXPRESSION PARSING FUNCTIONS
# ============================================================================
def parse_logic_expression(expr_str, model, index):
    # Parses logic expression string into Pyomo expression
    # Uses evaluate=False to preserve relational operators
    sym_map = LogicSymbolMap(model, index)
    
    try:
        # Prevent evaluation to keep "x <= threshold" unevaluated
        expr_sympy = sp.sympify(expr_str, evaluate=False)
    except Exception as e:
        raise ValueError(f"Error parsing expression '{expr_str}': {e}")
    
    try:
        pyomo_expr = sympy2pyomo_expression(expr_sympy, sym_map)
    except Exception as e:
        raise ValueError(f"Error converting expression '{expr_sympy}' to Pyomo: {e}")
    
    return pyomo_expr

def load_discrete_logic_json():
    # Loads discrete logic definitions from JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "user_data", "discrete_logic.json")
    
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        raise IOError(f"Error reading discrete logic JSON at {json_path}: {e}")
    
    return data

# ============================================================================
# DISCRETE LOGIC CONSTRAINT FUNCTION
# ============================================================================
def add_discrete_logic_constraints(model):
    # Reads discrete logic definitions from the JSON file and adds corresponding 
    # Pyomo disjunction constraints to the model
    logic_data = load_discrete_logic_json()
    logic_constraints = logic_data.get("logic_constraints", [])
    if not logic_constraints:
        print("No discrete logic constraints found in JSON.")
        return

    for logic in logic_constraints:
        disjunction_def = logic.get("disjunction")
        if not disjunction_def:
            continue
        
        # Use the provided name or default to "discrete_logic"
        logic_name = logic.get("name", "discrete_logic")
        
        # Define a disjunction rule function for the model's time set
        def disj_rule(m, t, disjunction_def=disjunction_def):
            disjuncts = []
            for disj in disjunction_def:
                constraints = []
                # Process each condition
                for cond_str in disj.get("conditions", []):
                    expr = parse_logic_expression(cond_str, m, t)
                    constraints.append(expr)
                # Process each assignment
                for assign_str in disj.get("assignments", []):
                    expr = parse_logic_expression(assign_str, m, t)
                    constraints.append(expr)
                disjuncts.append(constraints)
            return disjuncts

        # Attach the disjunction to the model using the specified name
        disj_component_name = logic_name
        if hasattr(model, disj_component_name):
            disj_component_name = disj_component_name + "_dup"
        setattr(model, disj_component_name, Disjunction(model.T, rule=disj_rule))
        print(f"Added discrete logic disjunction '{disj_component_name}' to the model.")
