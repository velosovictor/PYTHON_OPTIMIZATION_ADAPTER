"""
Discrete Logic Module

This module reads logical/discrete restrictions from a JSON file (user_data/discrete_logic.json)
and converts them into Pyomo-compatible logic constraints using Generalized Disjunctive Programming (GDP).
The user can define logic constraints in the JSON file, and this module will process them,
generating disjunctions in the Pyomo model.
"""

import os
import json
import sympy as sp

from pyomo.gdp import Disjunction
from pyomo.core.expr.sympy_tools import sympy2pyomo_expression
from pyomo.environ import Var

from .parameters import param_mapping, logic_parameters

# -----------------------------------------------------------------------------
# Helper class to build a symbol map for logic expressions.
# -----------------------------------------------------------------------------
class LogicSymbolMap:
    def __init__(self, model, index):
        self.model = model
        self.index = index
        self.symbol_map = {}
        # Map only those Vars that are user-defined (skip piecewise/internal ones)
        for comp in model.component_objects(Var, active=True):
            # Skip any component that is part of a piecewise constraint (names starting with "PW_")
            if comp.name.startswith("PW_"):
                continue
            # If the variable is indexed, only map it if the index is valid.
            if comp.is_indexed():
                if index in comp.index_set():
                    self.symbol_map[sp.symbols(comp.name)] = comp[index]
                else:
                    continue
            else:
                self.symbol_map[sp.symbols(comp.name)] = comp
        # Also map parameters (from object_data.json) and logic parameters.
        for key, value in param_mapping.items():
            self.symbol_map[sp.symbols(key)] = value
        for key, value in logic_parameters.items():
            self.symbol_map[sp.symbols(key)] = value

    def getPyomoSymbol(self, sympy_symbol, default=None):
        """Return the Pyomo variable or parameter corresponding to sympy_symbol."""
        return self.symbol_map.get(sympy_symbol, default)

# -----------------------------------------------------------------------------
def parse_logic_expression(expr_str, model, index):
    """
    Parses a logic expression string into a Pyomo expression using sympy.
    The 'evaluate=False' flag is used to prevent premature evaluation of relational expressions.
    """
    sym_map = LogicSymbolMap(model, index)
    try:
        # Prevent evaluation so that "x <= threshold" remains unevaluated.
        expr_sympy = sp.sympify(expr_str, evaluate=False)
    except Exception as e:
        raise ValueError(f"Error parsing expression '{expr_str}': {e}")
    try:
        pyomo_expr = sympy2pyomo_expression(expr_sympy, sym_map)
    except Exception as e:
        raise ValueError(f"Error converting sympy expression '{expr_sympy}' to Pyomo expression: {e}")
    return pyomo_expr

# -----------------------------------------------------------------------------
def load_discrete_logic_json():
    """
    Loads the discrete logic definitions from 'user_data/discrete_logic.json'.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "user_data", "discrete_logic.json")
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        raise IOError(f"Error reading discrete logic JSON file at {json_path}: {e}")
    return data

# -----------------------------------------------------------------------------
def add_discrete_logic_constraints(model):
    """
    Reads discrete logic definitions from the JSON file and adds corresponding 
    Pyomo disjunction constraints to the model.
    
    The JSON file should have the following structure:
    
    {
      "logic_constraints": [
        {
          "name": "spring_logic",    // Optional; if not provided a default name is used.
          "disjunction": [
            {
              "conditions": ["x <= threshold"],
              "assignments": ["k_eff == k_high"]
            },
            {
              "conditions": ["x >= threshold"],
              "assignments": ["k_eff == k_low"]
            }
          ]
        }
      ]
    }
    
    For each logic constraint, a disjunction is added over the model’s time set (model.T).
    """
    logic_data = load_discrete_logic_json()
    logic_constraints = logic_data.get("logic_constraints", [])
    if not logic_constraints:
        print("No discrete logic constraints found in JSON.")
        return

    for logic in logic_constraints:
        disjunction_def = logic.get("disjunction")
        if not disjunction_def:
            continue  # Skip if no disjunction is defined.
        # Use the provided name or default to "discrete_logic"
        logic_name = logic.get("name", "discrete_logic")
        
        # Define a disjunction rule function for the model's time set.
        def disj_rule(m, t, disjunction_def=disjunction_def):
            disjuncts = []
            for disj in disjunction_def:
                constraints = []
                # Process each condition.
                for cond_str in disj.get("conditions", []):
                    expr = parse_logic_expression(cond_str, m, t)
                    constraints.append(expr)
                # Process each assignment.
                for assign_str in disj.get("assignments", []):
                    expr = parse_logic_expression(assign_str, m, t)
                    constraints.append(expr)
                disjuncts.append(constraints)
            return disjuncts

        # Attach the disjunction to the model using the specified (or default) name.
        disj_component_name = logic_name
        if hasattr(model, disj_component_name):
            disj_component_name = disj_component_name + "_dup"
        setattr(model, disj_component_name, Disjunction(model.T, rule=disj_rule))
        print(f"Added discrete logic disjunction '{disj_component_name}' to the model.")
