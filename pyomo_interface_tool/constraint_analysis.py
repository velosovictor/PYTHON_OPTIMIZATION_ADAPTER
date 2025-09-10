# ============================================================================
# CONSTRAINT ANALYSIS MODULE
# ============================================================================
# Analyzes the degrees of freedom in the optimization problem
# Detects under-constrained systems and suggests missing constraints

import numpy as np
from .equations import unknown_funcs, all_equations
from .parameters import discrete_parameters, minlp_enabled

# ============================================================================
# SYSTEM ANALYSIS FUNCTIONS
# ============================================================================
def count_degrees_of_freedom(time_steps):
    # Count total variables and constraints in the system
    
    # Count unknown functions (state variables)
    state_variables = len(unknown_funcs) * time_steps
    
    # Count optimization variables (parameters to be tuned)
    optimization_variables = 0
    if minlp_enabled and discrete_parameters:
        for var_def in discrete_parameters:
            if var_def.get("optimize", True):  # Default: optimize this variable
                optimization_variables += time_steps  # Time-varying parameter
    
    total_variables = state_variables + optimization_variables
    
    # Count constraints
    ode_constraints = len(all_equations) * (time_steps - 1)  # ODEs discretized
    initial_constraints = len(unknown_funcs)  # Initial conditions
    
    total_constraints = ode_constraints + initial_constraints
    
    return {
        "total_variables": total_variables,
        "state_variables": state_variables, 
        "optimization_variables": optimization_variables,
        "total_constraints": total_constraints,
        "ode_constraints": ode_constraints,
        "initial_constraints": initial_constraints,
        "degrees_of_freedom": total_variables - total_constraints
    }

def analyze_constraint_status(analysis):
    # Determine the type of problem based on degrees of freedom
    
    dof = analysis["degrees_of_freedom"]
    
    if dof == 0:
        return {
            "problem_type": "fully_constrained",
            "status": "SIMULATION",
            "description": "System has unique solution - no optimization needed",
            "action": "solve_simulation"
        }
    elif dof > 0:
        return {
            "problem_type": "under_constrained", 
            "status": "OPTIMIZATION",
            "description": f"System has {dof} degrees of freedom - optimization needed",
            "missing_constraints": dof,
            "action": "add_optimization_constraints"
        }
    else:  # dof < 0
        return {
            "problem_type": "over_constrained",
            "status": "INFEASIBLE", 
            "description": f"System has {abs(dof)} conflicting constraints",
            "action": "remove_constraints"
        }

def suggest_optimization_constraints(analysis, constraint_status):
    # Suggest what kind of optimization constraints to add
    
    if constraint_status["problem_type"] != "under_constrained":
        return []
    
    missing = constraint_status["missing_constraints"]
    suggestions = []
    
    # Suggest simple constraint types
    if missing >= 1:
        suggestions.append({
            "constraint_type": "scalar_target",
            "description": "Set target value for a parameter",
            "example": {"k_eff_target": 5000},
            "constraint_form": "k_eff = k_eff_target"
        })
    
    if missing >= 2:
        suggestions.append({
            "constraint_type": "trajectory_target", 
            "description": "Set target trajectory for state variable",
            "example": {"x_trajectory": [2.0, 1.5, 1.0, 0.5, 0.5]},
            "constraint_form": "x[t] = x_trajectory[t] (for specified time points)"
        })
    
    if missing >= 3:
        suggestions.append({
            "constraint_type": "performance_criterion",
            "description": "Add performance measure to optimize",
            "example": {"minimize": "energy", "maximize": "settling_time"},
            "constraint_form": "minimize sum(v[t]^2) or maximize performance_metric"
        })
    
    return suggestions

# ============================================================================
# AUTOMATIC CONSTRAINT ADDITION
# ============================================================================
def add_missing_constraints_automatically(model, optimization_config, analysis):
    # Automatically add the simplest missing constraints based on user config
    
    constraint_status = analyze_constraint_status(analysis)
    
    if constraint_status["problem_type"] != "under_constrained":
        return None
    
    missing = constraint_status["missing_constraints"]
    constraints_added = []
    
    # Add scalar target constraints
    targets = optimization_config.get("targets", {})
    for target_name, target_value in targets.items():
        if missing > 0:
            # Extract variable name (remove '_target' suffix)
            var_name = target_name.replace("_target", "")
            
            if hasattr(model, var_name):
                # Add target constraint: var = target_value (at final time)
                var_obj = getattr(model, var_name)
                final_time = max(model.T)
                
                def target_constraint_rule(m):
                    return var_obj[final_time] == target_value
                
                constraint_name = f"target_{var_name}"
                setattr(model, constraint_name, 
                       model.Constraint(rule=target_constraint_rule))
                
                constraints_added.append({
                    "type": "scalar_target",
                    "variable": var_name,
                    "target": target_value,
                    "constraint": f"{var_name}[final_time] = {target_value}"
                })
                missing -= 1
    
    return {
        "constraints_added": constraints_added,
        "remaining_dof": missing
    }

# ============================================================================
# REPORTING FUNCTIONS  
# ============================================================================
def print_system_analysis(time_steps):
    # Print detailed analysis of the constraint structure
    
    analysis = count_degrees_of_freedom(time_steps)
    constraint_status = analyze_constraint_status(analysis)
    
    print("=" * 70)
    print("CONSTRAINT ANALYSIS")
    print("=" * 70)
    
    print(f"State Variables:         {analysis['state_variables']}")
    print(f"Optimization Variables:  {analysis['optimization_variables']}")
    print(f"Total Variables:         {analysis['total_variables']}")
    print()
    print(f"ODE Constraints:         {analysis['ode_constraints']}")
    print(f"Initial Constraints:     {analysis['initial_constraints']}")
    print(f"Total Constraints:       {analysis['total_constraints']}")
    print()
    print(f"Degrees of Freedom:      {analysis['degrees_of_freedom']}")
    print()
    print(f"Problem Type:            {constraint_status['status']}")
    print(f"Description:             {constraint_status['description']}")
    
    if constraint_status["problem_type"] == "under_constrained":
        print()
        print("OPTIMIZATION NEEDED:")
        suggestions = suggest_optimization_constraints(analysis, constraint_status)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion['description']}")
            print(f"     Example: {suggestion['example']}")
    
    print("=" * 70)
    
    return analysis, constraint_status
