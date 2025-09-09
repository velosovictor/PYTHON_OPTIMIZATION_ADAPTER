# ============================================================================
# EXTRA VARIABLES MODULE
# ============================================================================
# Adds additional decision variables to Pyomo models for MINLP problems
# Supports Reals, Integers, and Binary domains with bounds

from pyomo.environ import Var, Reals, Integers, Binary

# ============================================================================
# VARIABLE ADDITION FUNCTION
# ============================================================================
def add_extra_variables(model, T, extra_vars):
    # Adds decision variables to model based on JSON definitions
    # Creates variables for each time index with specified domain and bounds
    
    for var_def in extra_vars:
        name = var_def["name"]
        domain_str = var_def["domain"].lower()

        # Map domain string to Pyomo domain
        if domain_str == "reals":
            domain = Reals
        elif domain_str == "integers":
            domain = Integers
        elif domain_str == "binary":
            domain = Binary
        else:
            raise ValueError(f"Unknown domain: {domain_str}")

        # Extract bounds if specified
        bounds = var_def.get("bounds", None)
        if bounds is not None:
            lb, ub = bounds
        else:
            lb, ub = None, None

        # Add variable to model
        setattr(model, name, Var(T, domain=domain, bounds=(lb, ub)))
