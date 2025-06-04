"""
Discretization Module

This module provides functions to discretize symbolic differential equations
into algebraic expressions appropriate for inclusion in a Pyomo model.
Typical schemes such as the backward Euler method are used to approximate 
derivatives, thereby converting ODEs into difference equations.

Maintenance Notes:
- Update the discretization logic if a different numerical scheme is required.
- Ensure consistency with the symbolic definitions in the equations module.
"""

import sympy as sp
from .equations import t   # The symbolic variable representing time.
from .user_data.lookup import lookup_tables

def discretize_symbolic_eq(eq, dt, unknown_funcs, replacement_dict=None):
    """
    Discretizes a symbolic ODE using a backward Euler type method.
    
    Parameters:
      eq : sympy expression
          The symbolic differential equation to discretize.
      dt : float
          The time step for discretization.
      unknown_funcs : list
          A list of unknown function symbols in the equation.
      replacement_dict : dict, optional
          Additional replacements to apply to the expression.
    
    Returns:
      disc_expr : sympy expression
          The discretized algebraic equation.
    """
    res = eq.lhs - eq.rhs  # Compute the residual expression.

    # For each unknown function, replace the derivative and update the function reference.
    for f in unknown_funcs:
        fname = f.func.__name__
        # Replace the derivative using backward difference approximation.
        res = res.replace(
            sp.Derivative(f, t),
            (sp.Symbol(f"{fname}_ip1") - sp.Symbol(f"{fname}_i")) / dt
        )
        # Replace the function f(t) with the future time symbol (f_ip1) in the discretized expression.
        res = res.xreplace({f: sp.Symbol(f"{fname}_ip1")})
    
    # Apply any custom replacements provided.
    if replacement_dict is not None:
        res = res.xreplace(replacement_dict)
    
    # Replace calls to lookup functions (e.g., DAMPING(x_ip1)) with a corresponding symbol.
    for key in lookup_tables.keys():
        res = res.subs(sp.Function(key)(sp.Symbol("x_ip1")), sp.Symbol(f"{key.upper()}_ip1"))
    
    # Simplify the resulting expression before returning.
    return sp.simplify(res)
