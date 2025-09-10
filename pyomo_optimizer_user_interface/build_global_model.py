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

from .parameters import get_parameter, get_all_parameters
from .parameters import get_lookup_tables
from .discretization import discretize_symbolic_eq
from .equations import get_equations
from .constraint_rules import generate_constraint_rule
from .extra_variables import add_extra_variables

# Import the new discrete logic module.
from .discrete_logic import add_discrete_logic_constraints
from .optimization import add_optimization_objective

# ============================================================================
# MODEL BUILDING FUNCTION
# ============================================================================
def build_global_model(equations=None):
    # Constructs and returns the full Pyomo model for monolithic approach
    # Creates time grid, variables, constraints, and applies transformations
    
    # Load parameters
    dt_value = get_parameter("dt_value")
    final_time = get_parameter("final_time")
    param_mapping = get_parameter("parameters") or {}
    minlp_enabled = get_parameter("minlp_enabled") or False
    discrete_parameters = get_parameter("discrete_parameters") or []
    params_data = get_all_parameters()
    
    # Auto-detect unknown parameters using framework logic (not user config!)
    from pyomo_optimizer_user_interface.parameters import detect_unknown_parameters
    unknown_params = detect_unknown_parameters()
    
    # Extract sparse state variable tensors and initial conditions
    state_variables = {}
    init_conditions = {}
    for var_name in unknown_params:
        if var_name in params_data:
            tensor = params_data[var_name]
            state_variables[var_name] = tensor
            # Extract initial condition (first known value)
            init_value = tensor.sel(time=0).values.item()
            if not np.isnan(init_value):
                init_conditions[f"{var_name}0"] = init_value
    
    # Use provided equations or load fresh equations dynamically
    if equations is None:
        t, unknown_funcs, parameters, equations = get_equations()

    # Build simulation time grid from state variable tensors or fallback to dt_value
    if state_variables:
        # Use time coordinates from first state variable tensor
        first_tensor = next(iter(state_variables.values()))
        tau = first_tensor.coords["time"].values
    else:
        # Fallback to dt_value approach
        tau = np.arange(0, final_time + dt_value, dt_value)
    N = len(tau) - 1

    # Discretize system equations
    discretized_equations = []
    for eq in equations:
        disc = discretize_symbolic_eq(eq, dt_value, unknown_funcs, t, discrete_parameters)
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

    # Add decision variables for unknown functions with bounds
    for f in unknown_funcs:
        fname = str(f.func.__name__)
        # Extract bounds from tensor attributes if available
        bounds = None
        if fname in params_data:
            tensor = params_data[fname]
            if hasattr(tensor, 'attrs') and 'bounds' in tensor.attrs:
                bounds = tensor.attrs['bounds']
                print(f"🔧 DEBUG: Setting bounds for {fname}: {bounds}")
        
        if bounds:
            setattr(model, fname, Var(model.T, domain=Reals, bounds=bounds))
        else:
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
    
    # Add piecewise constraints for lookup tables (loaded dynamically from user data)
    lookup_tables = get_lookup_tables()
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
    
    # Add optimization objective
    optimization_config = params_data.get("optimization", {"enabled": False})
    add_optimization_objective(model, optimization_config)
    
    return model, tau
