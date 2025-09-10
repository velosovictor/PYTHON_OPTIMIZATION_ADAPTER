# ============================================================================
# BUILD GLOBAL MODEL MODULE
# ============================================================================
# Constructs the full optimization model for monolithic approach
# Generates Pyomo ConcreteModel with time grid, variables, constraints
# Handles initial conditions, piecewise functions, and MINLP variables

from pyomo.environ import (
    ConcreteModel, Var, Constraint, Objective, RangeSet, Reals,
    minimize, Piecewise, TransformationFactory
)
import numpy as np
import sympy as sp

from .parameters import (
    dt_value, final_time, init_conditions, param_mapping, 
    minlp_enabled, discrete_parameters
)
from .user_data.lookup import lookup_tables
from .discretization import discretize_symbolic_eq
from .equations import unknown_funcs, all_equations
from .constraint_rules import generate_constraint_rule
from .extra_variables import add_extra_variables

# Import the new discrete logic module.
from .discrete_logic import add_discrete_logic_constraints

# ============================================================================
# MODEL BUILDING FUNCTION
# ============================================================================
def build_global_model(equations=None):
    # Constructs and returns the full Pyomo model for monolithic approach
    # Creates time grid, variables, constraints, and applies transformations
    
    # Use provided equations or default to all_equations
    if equations is None:
        equations = all_equations

    # Build simulation time grid
    tau = np.arange(0, final_time + dt_value, dt_value)
    N = len(tau) - 1

    # Discretize system equations
    discretized_equations = []
    for eq in equations:
        disc = discretize_symbolic_eq(eq, dt_value, unknown_funcs)
        # Replace function calls with unified symbols
        disc = disc.xreplace({sp.Function("t")(sp.Symbol("t")): sp.Symbol("t")})
        
        # Unify all time symbols
        t_master = sp.Symbol("t")
        replacements = {}
        for s in disc.free_symbols:
            if s.name == "t" and s != t_master:
                replacements[s] = t_master
        if replacements:
            disc = disc.xreplace(replacements)
        
        discretized_equations.append(disc)

    # Create Pyomo model
    model = ConcreteModel(name="MonolithicODE_MINLP")
    model.T = RangeSet(0, N)

    # Add decision variables for unknown functions
    for f in unknown_funcs:
        fname = str(f.func.__name__)
        setattr(model, fname, Var(model.T, domain=Reals))
    
    # Apply initial conditions
    for f in unknown_funcs:
        fname = str(f.func.__name__)
        key0 = f"{fname}0"
        if key0 in init_conditions:
            def init_rule(m, i=None, fname=fname, key0=key0):
                idx = 0 if i is None else i
                return getattr(m, fname)[idx] == init_conditions[key0]
            setattr(model, f"init_{fname}", Constraint(rule=init_rule))
    
    # Add piecewise constraints for lookup tables
    for key, (indep_var_name, data_array) in lookup_tables.items():
        setattr(model, key.lower(), Var(model.T, domain=Reals))
        indep_var = getattr(model, indep_var_name)
        pw_pts = data_array.coords[indep_var_name].values.tolist()
        pw_vals = data_array.values.tolist()
        pw_map = dict(zip(pw_pts, pw_vals))

        # Set variable bounds based on lookup table domain
        for t_idx in model.T:
            var_obj = indep_var[t_idx]
            if var_obj.lb is None:
                var_obj.setlb(min(pw_pts))
            if var_obj.ub is None:
                var_obj.setub(max(pw_pts))
        
        # Create piecewise constraint
        def piecewise_f_rule(m, i, pm=pw_map):
            return pm
        
        setattr(model, f"PW_{key.lower()}", Piecewise(
            model.T,
            getattr(model, key.lower()),
            indep_var,
            pw_pts=pw_pts,
            f_rule=piecewise_f_rule,
            pw_constr_type='EQ',
            pw_repn='INC'
        ))

    # Add extra variables for MINLP problems
    if minlp_enabled and discrete_parameters:
        add_extra_variables(model, model.T, discrete_parameters)
    
    # Add discretized ODE constraints
    for j, disc_eq in enumerate(discretized_equations, start=1):
        comp_name = f"ode{j}_constraints"
        c_rule = generate_constraint_rule(
            disc_eq,
            unknown_funcs,
            param_mapping,
            discrete_parameters=discrete_parameters if minlp_enabled else None,
            time_array=tau
        )
        setattr(model, comp_name, Constraint(range(N), rule=c_rule))
    
    # Add discrete logic constraints and apply GDP transformation
    if minlp_enabled:
        add_discrete_logic_constraints(model)
        TransformationFactory('gdp.hull').apply_to(model)
    
    # Define dummy objective (required by solvers)
    model.obj = Objective(expr=0, sense=minimize)
    
    return model, tau
