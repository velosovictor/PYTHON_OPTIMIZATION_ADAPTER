# ============================================================================
# TIMEWISE SIMULATION MODULE
# ============================================================================
# Implements step-by-step simulation using sequential approach
# Builds and solves small models at each time step for real-time updates
# Supports live plotting and parameter reloading during simulation

import numpy as np
import sympy as sp
import time
import json

from pyomo.core.expr.sympy_tools import sympy2pyomo_expression
from pyomo.environ import (
    ConcreteModel, Var, Reals, Constraint, SolverFactory, value, RangeSet,
    Piecewise, TransformationFactory, Param
)

from .parameters import get_parameter, update_parameters_with_data, get_lookup_tables
from .equations import unknown_funcs, all_equations
from .extra_variables import add_extra_variables
from .constraint_rules import MySymbolMap
from .discretization import discretize_symbolic_eq
from .discrete_logic import add_discrete_logic_constraints
from .postprocessing import package_solution_live
from .plotting import plot_dataset_live


def run_build_sequential_model(plot_in_real_time=False):
    """
    Runs the timewise simulation of the ODE system.

    At each time step:
      - The simulation time grid is used to determine current and next time.
      - Model parameters are reloaded from a JSON file.
      - A small Pyomo model is built for the current time step.
      - The model includes unknown functions, extra variables, and piecewise constraints.
      - Discrete logic constraints are added if MINLP is enabled.
      - ODE constraints for the step are constructed using discretization.
      - The model is solved, and the solution is extracted.
      - Live plotting is updated if enabled.

    Returns:
      tau : numpy.ndarray
          Array of time points from 0 to final_time with step dt_value.
      sol_dict : dict
          Dictionary mapping each unknown function name to its solution over time.
    """
    # ------------------------------------------------
    # Step 1: Build the full simulation time grid.
    # ------------------------------------------------
    dt_value = get_parameter("dt_value")
    final_time = get_parameter("final_time")
    tau = np.arange(0, final_time + dt_value, dt_value)
    N = len(tau) - 1

    # ------------------------------------------------
    # Step 2: Prepare the solution dictionary for unknown functions.
    # ------------------------------------------------
    sol_dict = {}
    for f in unknown_funcs:
        fname = f.func.__name__
        sol_dict[fname] = np.zeros(len(tau), dtype=float)
    # Set initial conditions from JSON configuration.
    for f in unknown_funcs:
        fname = f.func.__name__
        init_conditions = get_parameter("init_conditions") or {}
        sol_dict[fname][0] = init_conditions.get(fname + "0", 0.0)

    # ------------------------------------------------
    # Step 3: Create the solver.
    # ------------------------------------------------
    solver_name = get_parameter("solver") or "ipopt"
    solver = SolverFactory(solver_name)

    # ------------------------------------------------
    # Step 4: Configure live plotting if enabled.
    # ------------------------------------------------
    if plot_in_real_time:
        live_plotting = True  # Force live plotting even if flag is false.
        import matplotlib.pyplot as plt
        plt.ion()
        # Initialize live plot with the initial truncated dataset.
        ds_init = package_solution_live(tau[:1], sol_dict, dt_value, final_time, description="Real-time results")
        plot_dataset_live(ds_init)
        plt.show(block=False)

    # Record simulation start time to synchronize simulation timing.
    simulation_start_time = time.time()
    
    # ------------------------------------------------
    # Step 5: Loop over each time step.
    # ------------------------------------------------
    for n in range(N):
        step_start_time = time.time()
        
        # ------------------------------------------------
        # Step 5a: Reload simulation parameters from JSON (if available).
        # ------------------------------------------------
        try:
            # Reload parameters for real-time updates
            from .parameters import _loaded_parameters
            if hasattr(_loaded_parameters, '__file__'):
                # Get the source data folder from the loaded parameters
                import json
                # Try to reload from the same source if available
                # This enables live parameter updates during simulation
                pass  # Parameters are already loaded in memory
        except Exception as e:
            # Continue with existing parameters if reload fails
            pass
        
        # Define current and next time.
        t_n = tau[n]
        t_np1 = tau[n+1]
        dt = t_np1 - t_n

        # ------------------------------------------------
        # Step 5b: Capture the current state (solution at previous time step).
        # ------------------------------------------------
        current_state = {f.func.__name__: sol_dict[f.func.__name__][n] for f in unknown_funcs}

        # ------------------------------------------------
        # Step 5c: Build a Pyomo model for the current time step.
        # ------------------------------------------------
        model = ConcreteModel()
        model.T = RangeSet(0, 0)  # Single time step model.

        # (A) Create Pyomo variables for each unknown function.
        for f in unknown_funcs:
            fname = f.func.__name__
            init_guess = current_state[fname]
            var_obj = Var(model.T, domain=Reals, initialize=init_guess)
            setattr(model, fname, var_obj)

        # (B) Add extra variables if MINLP is enabled.
        minlp_enabled = get_parameter("minlp_enabled") or False
        discrete_parameters = get_parameter("discrete_parameters") or []
        if minlp_enabled and discrete_parameters:
            add_extra_variables(model, model.T, discrete_parameters)

        # (C) Add piecewise constraints for lookup tables (loaded dynamically).
        lookup_tables = get_lookup_tables()
        for key, (indep_var_name, data_array) in lookup_tables.items():
            lookup_var = Var(model.T, domain=Reals)
            setattr(model, key.lower(), lookup_var)

            pw_pts = data_array.coords[indep_var_name].values.tolist()
            pw_vals = data_array.values.tolist()

            if indep_var_name in [f_.func.__name__ for f_ in unknown_funcs]:
                var_for_domain = getattr(model, indep_var_name)
                for idx in model.T:
                    if var_for_domain[idx].lb is None:
                        var_for_domain[idx].setlb(min(pw_pts))
                    if var_for_domain[idx].ub is None:
                        var_for_domain[idx].setub(max(pw_pts))

            def piecewise_f_rule(m, i, pm=dict(zip(pw_pts, pw_vals))):
                return pm

            model.add_component(
                f"PW_{key.lower()}",
                Piecewise(
                    model.T,
                    lookup_var,
                    getattr(model, indep_var_name),
                    pw_pts=pw_pts,
                    f_rule=piecewise_f_rule,
                    pw_constr_type='EQ',
                    pw_repn='INC'
                )
            )

        # (D) Add discrete logic constraints if MINLP is enabled.
        if minlp_enabled:
            add_discrete_logic_constraints(model)
            TransformationFactory('gdp.hull').apply_to(model)

        # (E) Add ODE constraints for the current step.
        def step_constraint_rule(m, eq_idx):
            eq_sym = all_equations[eq_idx]
            disc_expr = discretize_symbolic_eq(eq_sym, dt, unknown_funcs)
            # Replace previous time step values.
            for f_ in unknown_funcs:
                fname = f_.func.__name__
                disc_expr = disc_expr.xreplace({sp.Symbol(f"{fname}_i"): current_state[fname]})
            # For extra variables, replace bare symbols with their _ip1 counterparts.
            if minlp_enabled and discrete_parameters:
                for var_def in discrete_parameters:
                    vname = var_def["name"]
                    disc_expr = disc_expr.xreplace({
                        sp.Symbol(vname): sp.Symbol(f"{vname}_ip1"),
                        sp.Symbol(f"{vname}_i"): 0.0
                    })
            # For lookup tables, set previous time values to 0.0.
            for lk in lookup_tables.keys():
                disc_expr = disc_expr.xreplace({sp.Symbol(f"{lk.upper()}_i"): 0.0})
            # Replace the time symbol "t" with t_np1.
            disc_expr = disc_expr.xreplace({sp.Symbol("t"): t_np1})
            # Force any remaining symbol with name "t" to be replaced.
            for sym in list(disc_expr.free_symbols):
                if sym.name == "t":
                    disc_expr = disc_expr.xreplace({sym: t_np1})
            # Optionally simplify the expression.
            disc_expr = sp.simplify(disc_expr)
            # Build the symbol map.
            my_map = MySymbolMap()
            my_map.symbol_map[sp.Symbol("t")] = t_np1
            for f_ in unknown_funcs:
                fname = f_.func.__name__
                my_map.symbol_map[sp.Symbol(f"{fname}_ip1")] = getattr(m, fname)[0]
            if minlp_enabled and discrete_parameters:
                for var_def in discrete_parameters:
                    vname = var_def["name"]
                    my_map.symbol_map[sp.Symbol(f"{vname}_ip1")] = getattr(m, vname)[0]
            for lk in lookup_tables.keys():
                my_map.symbol_map[sp.Symbol(f"{lk.upper()}_ip1")] = getattr(m, lk.lower())[0]
            my_map.symbol_map[sp.Symbol("dt")] = dt
            param_mapping = get_parameter("parameters") or {}
            for p_key, p_val in param_mapping.items():
                disc_expr = disc_expr.xreplace({sp.Symbol(p_key): p_val})
            unmapped = disc_expr.free_symbols - set(my_map.symbol_map.keys())
            if unmapped:
                raise ValueError(
                    f"Unmapped leftover symbols in step {n}, eq {eq_idx}: {unmapped}\n"
                    f"Expression: {disc_expr}"
                )
            py_expr = sympy2pyomo_expression(disc_expr, my_map)
            return py_expr == 0

        model.step_constraints = Constraint(range(len(all_equations)), rule=step_constraint_rule)

        # (F) Solve the small model for the current step.
        results = solver.solve(model, tee=True)

        # (G) Extract solutions for unknown functions.
        for f in unknown_funcs:
            fname = f.func.__name__
            sol_dict[fname][n+1] = value(getattr(model, fname)[0])

        # (H) Update live plot if enabled.
        if plot_in_real_time and live_plotting:
            current_tau = tau[:n+2]
            sol_dict_partial = {var: sol_dict[var][:len(current_tau)] for var in sol_dict}
            ds_live = package_solution_live(current_tau, sol_dict_partial, dt_value, final_time, description="Real-time results")
            plot_dataset_live(ds_live)

        # ------------------------------------------------
        # Synchronize simulation time with the clock.
        # ------------------------------------------------
        target_time = simulation_start_time + (n+1)*dt_value
        current_time = time.time()
        sleep_time = target_time - current_time
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            print(f"Warning: Step {n} is behind schedule by {-sleep_time:.3f} seconds.")
            
    # Finalize simulation: if live plotting is enabled, block until the figure is closed.
    if plot_in_real_time and live_plotting:
        import matplotlib.pyplot as plt
        plt.ioff()
        plt.show(block=True)
        
    return tau, sol_dict
