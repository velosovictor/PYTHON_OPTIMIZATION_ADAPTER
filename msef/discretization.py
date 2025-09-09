# ============================================================================
# DISCRETIZATION MODULE
# ============================================================================
# Discretizes symbolic differential equations into algebraic expressions
# Uses backward Euler method to convert ODEs into difference equations

import sympy as sp
from .equations import t
from .user_data.lookup import lookup_tables

# ============================================================================
# DISCRETIZATION FUNCTION
# ============================================================================
def discretize_symbolic_eq(eq, dt, unknown_funcs, replacement_dict=None):
    # Discretizes a symbolic ODE using backward Euler method
    # Converts derivatives to finite differences and functions to discrete symbols
    
    res = eq.lhs - eq.rhs  # Compute residual expression

    # Replace derivatives and functions for each unknown variable
    for f in unknown_funcs:
        fname = f.func.__name__
        
        # Replace derivative with backward difference: df/dt ≈ (f_i+1 - f_i)/dt
        res = res.replace(
            sp.Derivative(f, t),
            (sp.Symbol(f"{fname}_ip1") - sp.Symbol(f"{fname}_i")) / dt
        )
        
        # Replace function f(t) with discrete symbol f_i+1
        res = res.xreplace({f: sp.Symbol(f"{fname}_ip1")})
    
    # Apply additional replacements if provided
    if replacement_dict is not None:
        res = res.xreplace(replacement_dict)
    
    # Replace lookup function calls with discrete symbols
    for key in lookup_tables.keys():
        res = res.subs(sp.Function(key)(sp.Symbol("x_ip1")), sp.Symbol(f"{key.upper()}_ip1"))
    
    return sp.simplify(res)
