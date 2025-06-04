"""
Extra Variables Module

This module defines a routine to add extra variables to a Pyomo model based on
external definitions (for example, loaded from JSON). Possible domains include
Reals, Integers, and Binary.

Maintenance Notes:
- Update the domain lookup logic if additional data types are introduced.
- Ensure that added variables are compatible with other constraints in the model.
"""

# extra_variables.py

from pyomo.environ import Var, Reals, Integers, Binary

def add_extra_variables(model, T, extra_vars):
    """
    Adds additional decision variables to 'model' for each time index in 'T'. 
    The domain and bounds are determined by 'extra_vars', which is a list of dictionaries
    with keys like "name", "domain", and "bounds".
    
    Each new variable is attached to the model using 'setattr', allowing Pyomo to
    manage them during optimization.
    """
    for var_def in extra_vars:
        name = var_def["name"]
        domain_str = var_def["domain"].lower()

        if domain_str == "reals":
            domain = Reals
        elif domain_str == "integers":
            domain = Integers
        elif domain_str == "binary":
            domain = Binary
        else:
            raise ValueError(f"Unknown domain: {domain_str}")

        bounds = var_def.get("bounds", None)
        if bounds is not None:
            lb, ub = bounds
        else:
            lb, ub = None, None

        setattr(model, name, Var(T, domain=domain, bounds=(lb, ub)))
