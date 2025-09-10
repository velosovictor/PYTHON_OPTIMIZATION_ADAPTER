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
from .parameters import param_mapping

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

def create_energy_minimization_objective(model, weights=None):
    # Creates energy minimization objective
    # Minimizes kinetic + potential energy of the system
    
    if weights is None:
        weights = {"kinetic": 1.0, "potential": 1.0}
    
    obj_expr = 0
    
    # Add kinetic energy: 0.5 * m * v^2
    if hasattr(model, 'v') and 'm' in param_mapping:
        m_val = param_mapping['m']
        kinetic_weight = weights.get("kinetic", 1.0)
        for t in model.T:
            obj_expr += kinetic_weight * 0.5 * m_val * model.v[t]**2
    
    # Add potential energy: 0.5 * k * x^2
    if hasattr(model, 'x') and hasattr(model, 'k_eff'):
        potential_weight = weights.get("potential", 1.0)
        for t in model.T:
            obj_expr += potential_weight * 0.5 * model.k_eff[t] * model.x[t]**2
    
    return obj_expr

def create_custom_objective(model, objective_str, targets=None, weights=None):
    # Creates custom objective from symbolic expression string
    # For tracking objectives, use simpler approach
    
    if "sum((x(t) - x_target)**2" in objective_str:
        # This is a tracking objective - use the tracking function instead
        return create_tracking_objective(model, targets or {}, weights or {})
    
    # For simple expressions, build manually
    obj_expr = 0
    
    # Add position tracking term: sum((x[t] - target)^2)
    if hasattr(model, 'x') and targets and 'x_target' in targets:
        x_target = targets['x_target']
        position_weight = weights.get('position_weight', 1.0) if weights else 1.0
        for t in model.T:
            obj_expr += position_weight * (model.x[t] - x_target)**2
    
    # Add velocity penalty term: sum(v[t]^2)
    if hasattr(model, 'v'):
        velocity_weight = weights.get('velocity_weight', 0.1) if weights else 0.1
        for t in model.T:
            obj_expr += velocity_weight * model.v[t]**2
    
    # Add control penalty on k_eff changes
    if hasattr(model, 'k_eff') and len(list(model.T)) > 1:
        control_weight = weights.get('control_penalty', 0.01) if weights else 0.01
        T_list = list(model.T)
        for i in range(len(T_list)-1):
            t1, t2 = T_list[i], T_list[i+1]
            obj_expr += control_weight * (model.k_eff[t2] - model.k_eff[t1])**2
    
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
    elif obj_function == "energy":
        obj_expr = create_energy_minimization_objective(model, weights)
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
