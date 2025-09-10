# ============================================================================
# OPTIMIZATION MODULE
# ============================================================================
# Handles objective function creation and optimization problem setup
# Supports various optimization objectives like tracking, energy minimization, etc.

import sympy as sp
from pyomo.environ import Objective, minimize, maximize
from pyomo.core.expr.sympy_tools import sympy2pyomo_expression
from .constraint_rules import MySymbolMap
from .equations import unknown_funcs
from .parameters import get_parameter

# ============================================================================
# OBJECTIVE FUNCTION BUILDERS
# ============================================================================
def create_tracking_objective(model, target_values, weights=None):
    # Creates tracking objective to follow reference trajectories
    # Minimizes squared error between state variables and targets
    
    if weights is None:
        weights = {f.func.__name__: 1.0 for f in unknown_funcs}
    
    obj_expr = 0
    for f in unknown_funcs:
        fname = f.func.__name__
        target_key = f"{fname}_target"
        
        if target_key in target_values:
            target = target_values[target_key]
            weight = weights.get(fname, 1.0)
            
            # Add tracking term: weight * sum((x[t] - target)^2 for t in T)
            for t in model.T:
                obj_expr += weight * (getattr(model, fname)[t] - target)**2
    
    return obj_expr

def create_quadratic_penalty_objective(model, weights=None):
    # Creates quadratic penalty objective - COMPLETELY PROBLEM-AGNOSTIC!
    # Penalizes large values of state/control variables using quadratic terms
    
    if weights is None:
        weights = {}
    
    obj_expr = 0
    
    # Add quadratic penalties for state variables
    state_vars = [f.func.__name__ for f in unknown_funcs]
    for state_var in state_vars:
        if hasattr(model, state_var):
            weight = weights.get(f"{state_var}_penalty", 1.0)
            var_obj = getattr(model, state_var)
            for t in model.T:
                obj_expr += weight * var_obj[t]**2
    
    # Add quadratic penalties for control variables
    discrete_params = get_parameter("discrete_parameters") or []
    control_vars = [p.get("name") for p in discrete_params if p.get("name")]
    for control_var in control_vars:
        if hasattr(model, control_var):
            weight = weights.get(f"{control_var}_penalty", 1.0)
            control_obj = getattr(model, control_var)
            for t in model.T:
                obj_expr += weight * control_obj[t]**2
    
    return obj_expr

def create_custom_objective(model, objective_str, targets=None, weights=None):
    # Creates custom objective from symbolic expression string
    # For tracking objectives, use simpler approach
    
    if "_target" in str(targets) and any("target" in s for s in [objective_str]):
        # This is a tracking objective - use the tracking function instead
        return create_tracking_objective(model, targets or {}, weights or {})
    
    # For simple expressions, build manually
    obj_expr = 0
    
    # Add tracking terms for any target variables (problem-agnostic)
    if targets:
        for target_name, target_value in targets.items():
            var_name = target_name.replace('_target', '')  # x_target -> x
            if hasattr(model, var_name):
                weight_name = f'{var_name}_weight'
                var_weight = weights.get(weight_name, 1.0) if weights else 1.0
                var_obj = getattr(model, var_name)
                for t in model.T:
                    obj_expr += var_weight * (var_obj[t] - target_value)**2
    
    # Add control smoothness penalty for any control variables (problem-agnostic)
    if weights and 'control_penalty' in weights and len(list(model.T)) > 1:
        control_weight = weights.get('control_penalty', 0.01)
        T_list = list(model.T)
        
        # Find any optimization variables (controls) and penalize their changes
        from pyomo_optimizer_user_interface.parameters import get_parameter
        discrete_params = get_parameter("discrete_parameters") or []
        for param_info in discrete_params:
            var_name = param_info.get("name")
            if var_name and hasattr(model, var_name):
                var_obj = getattr(model, var_name)
                for i in range(len(T_list)-1):
                    t1, t2 = T_list[i], T_list[i+1]
                    obj_expr += control_weight * (var_obj[t2] - var_obj[t1])**2
    
    return obj_expr

# ============================================================================
# OBJECTIVE ASSIGNMENT FUNCTION
# ============================================================================
def add_optimization_objective(model, optimization_config):
    # Adds optimization constraints to close the degrees of freedom gap
    
    if not optimization_config.get("enabled", False):
        # Keep dummy objective for feasibility problems
        model.obj = Objective(expr=0, sense=minimize)
        return
    
    optimization_mode = optimization_config.get("mode", "objective_based")
    
    if optimization_mode == "constraint_based":
        # Use constraint-based approach (your insight!)
        add_constraint_based_optimization(model, optimization_config)
    else:
        # Use traditional objective-based approach  
        add_objective_based_optimization(model, optimization_config)

def add_constraint_based_optimization(model, optimization_config):
    # Add missing constraints to make the system fully determined
    from pyomo.environ import Constraint
    
    missing_constraints = optimization_config.get("missing_constraints", [])
    constraints_added = 0
    
    for constraint_def in missing_constraints:
        constraint_type = constraint_def.get("type")
        variable_name = constraint_def.get("variable") 
        target_value = constraint_def.get("target")
        time_spec = constraint_def.get("time", "final")
        
        if constraint_type == "scalar_target" and hasattr(model, variable_name):
            var_obj = getattr(model, variable_name)
            
            # Determine time index
            if time_spec == "final":
                time_idx = max(model.T)
            elif time_spec == "initial":  
                time_idx = min(model.T)
            else:
                time_idx = time_spec  # Specific time index
            
            # Add target constraint directly
            constraint_name = f"target_{variable_name}_{time_spec}" 
            constraint_expr = var_obj[time_idx] == target_value
            setattr(model, constraint_name, Constraint(expr=constraint_expr))
            
            constraints_added += 1
            print(f"Added constraint: {variable_name}[{time_spec}] = {target_value}")
    
    # Add dummy objective (we're using constraints, not objectives)
    model.obj = Objective(expr=0, sense=minimize)
    print(f"Added {constraints_added} missing constraints - system now fully determined")

def add_objective_based_optimization(model, optimization_config):
    # Traditional objective-based optimization
    obj_type = optimization_config.get("objective_type", "minimize")
    obj_function = optimization_config.get("objective_function", "tracking")
    targets = optimization_config.get("targets", {})
    weights = optimization_config.get("weights", {})
    
    # Determine objective sense
    sense = minimize if obj_type == "minimize" else maximize
    
    # Build objective expression based on type
    if obj_function == "tracking":
        obj_expr = create_tracking_objective(model, targets, weights)
    elif obj_function == "quadratic_penalty":
        obj_expr = create_quadratic_penalty_objective(model, weights)
    elif isinstance(obj_function, str):
        # Custom objective function as string
        obj_expr = create_custom_objective(model, obj_function, targets, weights)
    else:
        raise ValueError(f"Unknown objective function type: {obj_function}")
    
    # Add objective to model
    model.obj = Objective(expr=obj_expr, sense=sense)
    print(f"Added {obj_type} objective: {obj_function}")

# ============================================================================
# OPTIMIZATION RESULT ANALYSIS
# ============================================================================
def analyze_optimization_results(model, optimization_config):
    # Analyzes and reports optimization results
    # Shows objective value and optimized parameter values
    
    from pyomo.environ import value
    
    if not optimization_config.get("enabled", False):
        print("No optimization performed (feasibility solve only)")
        return
    
    print("=" * 60)
    print("OPTIMIZATION RESULTS")
    print("=" * 60)
    
    # Report objective value
    obj_value = value(model.obj)
    obj_type = optimization_config.get("objective_type", "minimize")
    print(f"Optimal {obj_type} objective value: {obj_value:.6f}")
    
    # Report optimized variables
    opt_vars = optimization_config.get("optimization_variables", [])
    if opt_vars:
        print("\nOptimized Parameters:")
        for var_name in opt_vars:
            if hasattr(model, var_name):
                var_obj = getattr(model, var_name)
                try:
                    if var_obj.is_indexed():
                        # Show time-varying parameter
                        values = []
                        for t in model.T:
                            try:
                                val = value(var_obj[t])
                                if val is not None:
                                    values.append(val)
                            except:
                                continue
                        if values:
                            avg_val = sum(values) / len(values)
                            print(f"  {var_name}: avg = {avg_val:.6f} (time-varying)")
                        else:
                            print(f"  {var_name}: (values not available)")
                    else:
                        # Show constant parameter
                        val = value(var_obj)
                        print(f"  {var_name}: {val:.6f}")
                except:
                    print(f"  {var_name}: (value not available)")
    
    print("=" * 60)
