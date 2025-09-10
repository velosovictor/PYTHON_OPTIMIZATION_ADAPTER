# ============================================================================
# DISCRETIZATION MODULE
# ============================================================================
# Discretizes symbolic differential equations into algebraic expressions
# Uses backward Euler method to convert ODEs into difference equations

import sympy as sp
from .equations import t
from .parameters import get_lookup_tables

# ============================================================================
# DISCRETIZATION FUNCTION
# ============================================================================
def discretize_symbolic_eq(eq, dt, unknown_funcs, t=None, discrete_parameters=None, replacement_dict=None):
    # Discretizes a symbolic ODE using backward Euler method
    # Converts derivatives to finite differences and functions to discrete symbols
    
    # If t not provided, use the imported one (fallback)
    if t is None:
        from .equations import get_equations
        t_temp, _, _, _ = get_equations()
        t = t_temp
    
    res = eq.lhs - eq.rhs  # Compute residual expression

    # Replace derivatives and functions for each unknown variable
    print(f"🔧 DEBUG: discretization unknown_funcs: {unknown_funcs}")
    for i, f in enumerate(unknown_funcs):
        print(f"🔧 DEBUG: Processing f[{i}]: {f}")
        if f is None:
            print(f"🔧 ERROR: f[{i}] is None!")
            continue
        fname = f.func.__name__
        
        # Replace derivative with backward difference: df/dt ≈ (f_i+1 - f_i)/dt
        res = res.replace(
            sp.Derivative(f, t),
            (sp.Symbol(f"{fname}_ip1") - sp.Symbol(f"{fname}_i")) / dt
        )
        
        # Replace function f(t) with discrete symbol f_i+1
        res = res.xreplace({f: sp.Symbol(f"{fname}_ip1")})
    
    # Handle optimization variables (discrete parameters)
    if discrete_parameters:
        for var_def in discrete_parameters:
            var_name = var_def["name"]
            var_func = sp.Function(var_name)(t)  # Create function version
            # Replace optimization function calls with discrete symbols
            res = res.xreplace({var_func: sp.Symbol(var_name)})
            print(f"🔧 DEBUG: Replaced {var_func} with {sp.Symbol(var_name)}")
    
    # Apply additional replacements if provided
    if replacement_dict is not None:
        res = res.xreplace(replacement_dict)
    
    # Replace lookup function calls with discrete symbols (loaded dynamically)
    lookup_tables = get_lookup_tables()
    for key in lookup_tables.keys():
        res = res.subs(sp.Function(key)(sp.Symbol("x_ip1")), sp.Symbol(f"{key.upper()}_ip1"))
    
    return sp.simplify(res)
