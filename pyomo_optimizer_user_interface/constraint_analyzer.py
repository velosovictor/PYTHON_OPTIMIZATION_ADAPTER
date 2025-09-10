# ============================================================================
# CONSTRAINT ANALYZER MODULE
# ============================================================================
# Analyzes the constraint structure to determine if system is over/under/fully constrained
# Implements the theory: Parameters vs Restrictions analysis

import numpy as np
from .parameters import get_parameter, get_all_parameters
from .equations import unknown_funcs, all_equations

# ============================================================================
# CONSTRAINT COUNTING FUNCTIONS
# ============================================================================
def count_time_steps():
    # Count discretized time steps
    final_time = get_parameter("final_time")
    dt_value = get_parameter("dt_value")
    if final_time is None or dt_value is None:
        raise ValueError("final_time and dt_value must be defined in the problem data")
    return int(final_time / dt_value)

def count_parameters():
    # Count total parameters to be determined
    N = count_time_steps() + 1  # Include t=0
    discrete_parameters = get_parameter("discrete_parameters") or []
    
    # Unknown functions (state variables)
    state_params = len(unknown_funcs) * N
    
    # Optimization variables (like k_eff)
    opt_params = 0
    if discrete_parameters:
        for var_def in discrete_parameters:
            opt_params += N  # Time-varying optimization variables
    
    total_params = state_params + opt_params
    
    print(f"Parameter Count Analysis:")
    final_time = get_parameter("final_time")
    dt_value = get_parameter("dt_value")
    print(f"  Time steps: {N} (t=0 to t={final_time}, dt={dt_value})")
    print(f"  State variables: {len(unknown_funcs)} × {N} = {state_params}")
    print(f"  Optimization variables: {len(discrete_parameters)} × {N} = {opt_params}")
    print(f"  TOTAL PARAMETERS: {total_params}")
    
    return total_params, state_params, opt_params

def count_restrictions():
    # Count total restrictions/constraints
    N = count_time_steps()
    init_conditions = get_parameter("init_conditions") or {}
    
    # Initial conditions
    init_constraints = len(init_conditions)
    
    # ODE constraints (one per equation per time interval)
    ode_constraints = len(all_equations) * N
    
    # Logic constraints (if enabled)
    logic_constraints = 0
    params_data = get_all_parameters()
    if params_data.get("minlp_enabled", False):
        logic_data = load_logic_constraints()
        if logic_data:
            # Each time step has logic constraints
            logic_constraints = (N + 1)  # Logic applies at each time point
    
    total_constraints = init_constraints + ode_constraints + logic_constraints
    
    print(f"Restriction Count Analysis:")
    print(f"  Initial conditions: {init_constraints}")
    print(f"  ODE constraints: {len(all_equations)} equations × {N} steps = {ode_constraints}")
    print(f"  Logic constraints: {logic_constraints}")
    print(f"  TOTAL RESTRICTIONS: {total_constraints}")
    
    return total_constraints, init_constraints, ode_constraints, logic_constraints

def load_logic_constraints():
    # Load discrete logic constraints from consolidated object_data.json
    try:
        import os
        import json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "user_data", "object_data.json")
        with open(json_path, "r") as f:
            data = json.load(f)
            return data.get("discrete_logic", None)
    except:
        return None

# ============================================================================
# CONSTRAINT ANALYSIS FUNCTION
# ============================================================================
def analyze_constraint_structure():
    # Perform complete constraint analysis according to the theory
    
    print("=" * 80)
    print("CONSTRAINT STRUCTURE ANALYSIS")
    print("=" * 80)
    
    # Count parameters and restrictions
    total_params, state_params, opt_params = count_parameters()
    total_constraints, init_constraints, ode_constraints, logic_constraints = count_restrictions()
    
    print()
    print("=" * 80)
    print("SYSTEM CLASSIFICATION")
    print("=" * 80)
    
    degrees_of_freedom = total_params - total_constraints
    
    print(f"Parameters:     {total_params}")
    print(f"Restrictions:   {total_constraints}")
    print(f"Degrees of Freedom: {degrees_of_freedom}")
    print()
    
    if degrees_of_freedom == 0:
        print("🎯 SYSTEM TYPE: FULLY CONSTRAINED")
        print("   → Unique solution exists")
        print("   → No optimization needed")
        return "fully_constrained"
        
    elif degrees_of_freedom > 0:
        print("🚀 SYSTEM TYPE: UNDER-CONSTRAINED (OPTIMIZATION PROBLEM)")
        print(f"   → {degrees_of_freedom} degrees of freedom")
        print(f"   → Need {degrees_of_freedom} additional constraints")
        print("   → This is where optimization comes in!")
        return "under_constrained"
        
    else:  # degrees_of_freedom < 0
        print("❌ SYSTEM TYPE: OVER-CONSTRAINED")
        print(f"   → {abs(degrees_of_freedom)} redundant constraints") 
        print("   → May have no solution or conflicting constraints")
        return "over_constrained"

def analyze_without_logic():
    # Analyze what happens if we remove logic constraints
    print("\n" + "=" * 80)
    print("ANALYSIS WITHOUT LOGIC CONSTRAINTS")
    print("=" * 80)
    
    N = count_time_steps()
    discrete_parameters = get_parameter("discrete_parameters") or []
    init_conditions = get_parameter("init_conditions") or {}
    total_params = (len(unknown_funcs) + len(discrete_parameters)) * (N + 1)
    total_constraints = len(init_conditions) + len(all_equations) * N
    
    degrees_of_freedom = total_params - total_constraints
    
    print(f"Parameters (without logic):     {total_params}")
    print(f"Restrictions (without logic):   {total_constraints}")
    print(f"Degrees of Freedom: {degrees_of_freedom}")
    
    if degrees_of_freedom > 0:
        print(f"🎯 OPTIMIZATION OPPORTUNITY: {degrees_of_freedom} missing constraints needed!")
        print("   This is where we can add optimization objectives or additional constraints.")
    
    return degrees_of_freedom

# ============================================================================
# MISSING CONSTRAINT SUGGESTIONS
# ============================================================================
def suggest_missing_constraints(degrees_of_freedom):
    # Suggest what types of constraints could be added
    
    if degrees_of_freedom <= 0:
        return
    
    print("\n" + "=" * 80)
    print("SUGGESTED MISSING CONSTRAINTS")
    print("=" * 80)
    
    print(f"You need {degrees_of_freedom} additional constraints. Here are some options:")
    print()
    
    print("📍 ENDPOINT CONSTRAINTS:")
    print("   - Final position: x(final_time) = target_value")
    print("   - Final velocity: v(final_time) = 0.0")
    
    print("\n🎯 PATH CONSTRAINTS:")
    print("   - Maximum position: max(x(t)) ≤ limit")
    print("   - Smooth trajectory: minimize sum((x[t+1] - x[t])²)")
    
    print("\n⚡ CONTROL CONSTRAINTS:")
    print("   - Constant control: k_eff(t) = constant")  
    print("   - Smooth control: minimize sum((k_eff[t+1] - k_eff[t])²)")
    
    print("\n🔧 OPTIMIZATION OBJECTIVES (pick the best solution):")
    print("   - Minimize energy: minimize sum(k_eff[t] * x[t]²)")
    print("   - Minimize time: reach target as fast as possible")
    print("   - Minimize control effort: minimize sum(k_eff[t]²)")
