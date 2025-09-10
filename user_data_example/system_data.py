# ============================================================================
# SYSTEM DATA SPECIFICATION
# ============================================================================
# Unified Python specification for optimization problems
# Replaces object_data.json + lookup.py with single file approach
# Supports scalars, xarray tensors, and all numerical restrictions

import numpy as np
import xarray as xr

# ============================================================================
# PROBLEM IDENTIFICATION
# ============================================================================
description = "Spring-mass with OPTIMIZATION - Find k to minimize final position"

# ============================================================================
# NUMERICAL RESTRICTIONS (EVERY NUMERICAL RESTRICTION IS A N-DIMENSIONAL TENSOR)
# ============================================================================
# Time-dependent state variables as xarray tensors with initial conditions specified
time_horizon = np.linspace(0, 1.0, int(1.0/0.5) + 1)  # [0, 0.5, 1.0]

# Collect all tensors in a dictionary for automatic export
tensors = {}

# Position tensor: only initial condition specified, rest unknown
x_data = np.full(len(time_horizon), np.nan)  # All unknown initially
x_data[0] = 1.0  # Only specify known initial condition: x(0) = 1.0
tensors["x"] = xr.DataArray(
    data=x_data,
    coords={"time": time_horizon},
    dims=["time"]
)

# Velocity tensor: only initial condition specified, rest unknown
v_data = np.full(len(time_horizon), np.nan)  # All unknown initially  
v_data[0] = 0.0  # Only specify known initial condition: v(0) = 0.0
tensors["v"] = xr.DataArray(
    data=v_data,
    coords={"time": time_horizon}, 
    dims=["time"]
)

# DAMPING tensor: fully specified (framework will detect it's NOT unknown)  
# Coordinate system matches the x tensor values (position-dependent damping)
x_coordinates = np.linspace(-2, 2, 100)  # Position range for damping lookup
tensors["DAMPING"] = xr.DataArray(
    data=1 + 0.1 * x_coordinates,
    coords={"x": x_coordinates},  # Uses same 'x' coordinate name as position tensor
    dims=["x"]
)

# Framework will auto-detect unknowns - NO coding logic here!

# ============================================================================
# SCALAR PARAMETERS (ZERO DIMENSIONAL TENSORS) - we dont need to use xarray here
# ============================================================================
parameters = {
    "m": 100,
    "F": 0,
    "k_soft": 500,
    "k_stiff": 2000
}

# Framework will auto-detect lookup functions from equations!

# ============================================================================
# SYSTEM EQUATIONS
# ============================================================================
equations = [
    "diff(x(t), t) - v(t) = 0",
    "m*diff(v(t), t) + DAMPING(x(t))*v(t) + k_eff*x(t) - F = 0"
]

# ============================================================================
# SIMULATION SETTINGS
# ============================================================================
dt_value = 0.5
final_time = 1.0
minlp_enabled = True
solver = "scip"
solve_mode = "monolithic"

# ============================================================================
# DISCRETE PARAMETERS
# ============================================================================
discrete_parameters = [
    {
        "name": "k_eff",
        "domain": "reals", 
        "bounds": [100, 3000]
    }
]

# ============================================================================
# OPTIMIZATION CONFIGURATION - PURE TENSOR-BASED APPROACH
# ============================================================================
# Pure optimization philosophy: find optimal tensor A by tuning parameters B
# Parameter A: TARGET (what we want optimal) -> Results in optimal xarray tensor
# Parameter B: TUNING VARIABLES (what we adjust to achieve optimal A)

# AVAILABLE TARGET EXPRESSION OPTIONS:
# =====================================
# POINT-WISE TARGETS:
# - "x[0]"           → Initial position
# - "x[-1]"          → Final position  
# - "v[1]"           → Velocity at t=1
# - "x[0] + v[-1]"   → Combined expression
#
# GLOBAL TENSOR TARGETS:
# - "sum(x**2)"      → Minimize total quadratic energy
# - "sum(abs(x))"    → Minimize total absolute deviation
# - "max(abs(x))"    → Minimize maximum absolute position
# - "sum(x)"         → Minimize total position (could be negative!)
# - "var(x)"         → Minimize position variance (smoothness)
# - "x"              → Auto-detect best global metric (framework decides)
#
# MULTI-PARAMETER TARGETS:
# - "0.5*m*sum(v**2) + 0.5*k_eff*sum(x**2)"  → Total mechanical energy
# - "sum(x**2) + 0.1*sum(v**2)"              → Weighted position+velocity
# - "sum((x - x_ref)**2)"                    → Tracking reference trajectory

optimization = {
    "enabled": True,
    
    # PARAMETER A: What we want to optimize (the target tensor/parameter)
    "target_parameter": "x",              # The tensor we want optimal values for
    "target_expression": "sum(x**2)",     # GLOBAL: minimize total quadratic position
    "objective_type": "minimize",          # minimize or maximize the target_expression
    
    # PARAMETER B: What we tune to achieve optimal Parameter A  
    "tuning_variables": ["k_eff"],        # Variables we adjust to find optimal target
    
    # RESULT: Framework returns optimal x(t) xarray tensor + optimal k_eff value
}

# ============================================================================
# DISCRETE LOGIC CONSTRAINTS
# ============================================================================
discrete_logic = {
    "logic_constraints": [
        {
            "name": "spring_stiffness_logic",
            "disjunction": [
                {
                    "conditions": ["x <= 0.5"],
                    "assignments": ["k_eff == k_soft"]
                },
                {
                    "conditions": ["x >= 0.5"], 
                    "assignments": ["k_eff == k_stiff"]
                }
            ]
        }
    ]
}

# ============================================================================
# SYSTEM DATA DICTIONARY
# ============================================================================
# All tensors automatically included via tensors dictionary!
system_data = {
    **tensors,  # Unpack all tensors automatically
    "parameters": parameters,
    "equations": equations,
    "dt_value": dt_value,
    "final_time": final_time,
    "minlp_enabled": minlp_enabled,
    "solver": solver,
    "solve_mode": solve_mode,
    "discrete_parameters": discrete_parameters,
    "optimization": optimization,
    "discrete_logic": discrete_logic,
    "description": description
}
