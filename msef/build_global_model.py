"""
Build Model Module

This module constructs the full optimization model for the simulation
framework. It generates a Pyomo ConcreteModel, sets up the simulation time grid,
initiates decision variables corresponding to the unknown functions, applies 
initial conditions, adds piecewise constraints from lookup tables, discretizes
the system equations, and incorporates extra model variables when required.

Maintenance Notes:
- Each section is clearly documented to ease future modifications.
- Update the corresponding sections if new equations, parameters, or lookup tables are added.
"""

from pyomo.environ import (
    ConcreteModel, Var, Constraint, Objective, RangeSet, Reals,
    minimize, Piecewise
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

# Import auxiliary functions for constraint generation and extra variable addition.
from .constraint_rules import generate_constraint_rule
from .extra_variables import add_extra_variables

# Import the new discrete logic module.
from .discrete_logic import add_discrete_logic_constraints

def build_global_model(equations=None):
    """
    Constructs and returns the full Pyomo model along with the simulation time grid.
    
    Parameters:
      equations (optional): A list of symbolic equations to be discretized.
                            Defaults to the module-level 'all_equations'.
    
    Process:
      1. Build the simulation time grid from time 0 to 'final_time' with step 'dt_value'.
      2. Discretize each equation using the provided discretization function.
      3. Create a ConcreteModel and define the time index set.
      4. Add decision variables for each unknown function (e.g., x, v).
      5. Set initial conditions for these variables if provided.
      6. Add piecewise constraints for lookup tables (e.g., for DAMPING functions).
      7. If enabled, add extra model variables for MINLP problems.
      8. Attach discretized ODE constraints to the model.
      9. Add discrete logic constraints from JSON.
      10. Define a dummy objective (required by Pyomo solvers).
    
    Returns:
      model: A Pyomo ConcreteModel representing the optimization model.
      tau: A numpy array representing the simulation time grid.
    """
    # Use the provided equations or default to all_equations.
    if equations is None:
        equations = all_equations

    # ------------------------------------------------
    # Step 1: Build the simulation time grid.
    # ------------------------------------------------
    tau = np.arange(0, final_time + dt_value, dt_value)
    N = len(tau) - 1  # Number of time steps.

    # ------------------------------------------------
    # Step 2: Discretize each equation.
    # ------------------------------------------------
    discretized_equations = []
    for eq in equations:
        # Discretize from symbolic to a numerical expression.
        disc = discretize_symbolic_eq(eq, dt_value, unknown_funcs)
        # Replace any function call t(t) with a unified symbol 't'.
        disc = disc.xreplace({sp.Function("t")(sp.Symbol("t")): sp.Symbol("t")})
        
        # Unify all symbols representing 't' into one master symbol.
        t_master = sp.Symbol("t")
        replacements = {}
        for s in disc.free_symbols:
            if s.name == "t" and s != t_master:
                replacements[s] = t_master
        if replacements:
            disc = disc.xreplace(replacements)
        
        discretized_equations.append(disc)

    # ------------------------------------------------
    # Step 3: Create the Pyomo model and define the time set.
    # ------------------------------------------------
    model = ConcreteModel(name="MonolithicODE_MINLP")
    model.T = RangeSet(0, N)

    # ------------------------------------------------
    # Step 4: Add decision variables for each unknown function.
    # ------------------------------------------------
    for f in unknown_funcs:
        fname = str(f.func.__name__)
        # Create a continuous variable for every time index.
        setattr(model, fname, Var(model.T, domain=Reals))
    
    # ------------------------------------------------
    # Step 5: Apply initial conditions, if provided.
    # ------------------------------------------------
    for f in unknown_funcs:
        fname = str(f.func.__name__)
        key0 = f"{fname}0"  # Convention: variable name followed by 0 denotes initial condition.
        if key0 in init_conditions:
            # Define a constraint to set the initial condition.
            def init_rule(m, i=None, fname=fname, key0=key0):
                idx = 0 if i is None else i
                return getattr(m, fname)[idx] == init_conditions[key0]
            setattr(model, f"init_{fname}", Constraint(rule=init_rule))
    
    # ------------------------------------------------
    # Step 6: Add piecewise constraints for lookup tables.
    # ------------------------------------------------
    for key, (indep_var_name, data_array) in lookup_tables.items():
        # Introduce a new variable to hold lookup values.
        setattr(model, key.lower(), Var(model.T, domain=Reals))
        indep_var = getattr(model, indep_var_name)
        pw_pts = data_array.coords[indep_var_name].values.tolist()
        pw_vals = data_array.values.tolist()
        pw_map = dict(zip(pw_pts, pw_vals))

        # Constrain the domain of the independent variable.
        for t_idx in model.T:
            var_obj = indep_var[t_idx]
            if var_obj.lb is None:
                var_obj.setlb(min(pw_pts))
            if var_obj.ub is None:
                var_obj.setub(max(pw_pts))
        
        # Define a piecewise mapping rule.
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

    # ------------------------------------------------
    # Step 7: Add extra variables for MINLP problems.
    # ------------------------------------------------
    if minlp_enabled and discrete_parameters:
        add_extra_variables(model, model.T, discrete_parameters)
    
    # ------------------------------------------------
    # Step 8: Attach the discretized ODE constraints to the model.
    # ------------------------------------------------
    for j, disc_eq in enumerate(discretized_equations, start=1):
        comp_name = f"ode{j}_constraints"
        c_rule = generate_constraint_rule(
            disc_eq,
            unknown_funcs,
            param_mapping,
            discrete_parameters=discrete_parameters if minlp_enabled else None,
            time_array=tau  # Passing the time grid for reference.
        )
        setattr(model, comp_name, Constraint(range(N), rule=c_rule))
    
    # ------------------------------------------------
    # Step 9: Add discrete logic constraints from JSON.
    # ------------------------------------------------
    if minlp_enabled:
        add_discrete_logic_constraints(model)
        # Apply GDP transformation for monolithic mode
        from pyomo.environ import TransformationFactory
        TransformationFactory('gdp.hull').apply_to(model)
    
    # ------------------------------------------------
    # Step 10: Define a dummy objective (required by Pyomo).
    # ------------------------------------------------
    model.obj = Objective(expr=0, sense=minimize)
    
    # Return the completed model and the time grid.
    return model, tau
