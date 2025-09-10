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

# Position tensor: only initial condition specified, rest unknown
x_data = np.full(len(time_horizon), np.nan)  # All unknown initially
x_data[0] = 1.0  # Only specify known initial condition: x(0) = 1.0
x = xr.DataArray(
    data=x_data,
    coords={"time": time_horizon},
    dims=["time"]
)

# Velocity tensor: only initial condition specified, rest unknown
v_data = np.full(len(time_horizon), np.nan)  # All unknown initially  
v_data[0] = 0.0  # Only specify known initial condition: v(0) = 0.0
v = xr.DataArray(
    data=v_data,
    coords={"time": time_horizon}, 
    dims=["time"]
)

# Framework will auto-detect unknowns - NO coding logic here!

# ============================================================================
# SCALAR PARAMETERS
# ============================================================================
parameters = {
    "m": 100,
    "F": 0,
    "k_soft": 500,
    "k_stiff": 2000
}

# ============================================================================
# TENSOR PARAMETERS (XARRAY)
# ============================================================================
# DAMPING function as tensor - replicate damping = 1+0.1*x over x ∈ [-2,2]
x_coords = np.linspace(-2, 2, 100)
DAMPING = xr.DataArray(
    data=1 + 0.1 * x_coords,
    coords={"x": x_coords},
    dims=["x"]
)

# Example time-varying force (commented for this problem)
# time_coords = np.linspace(0, 1, 5)
# F_time_dependent = xr.DataArray(
#     data=[0, 25, 50, 25, 0],
#     coords={"time": time_coords},
#     dims=["time"]
# )

# Example 2D spatial stiffness matrix (commented for this problem)
# x_pos_coords = np.array([-1.0, 0.0, 1.0])
# y_pos_coords = np.array([-1.0, 0.0, 1.0]) 
# k_spatial_matrix = xr.DataArray(
#     data=[[500, 750, 500],
#           [750, 1000, 750],
#           [500, 750, 500]],
#     coords={"x_pos": x_pos_coords, "y_pos": y_pos_coords},
#     dims=["x_pos", "y_pos"]
# )

# Lookup tables dictionary for compatibility with existing system
lookup_tables = {
    "DAMPING": ("x", DAMPING)
}

# ============================================================================
# ADDITIONAL FUNCTIONS
# ============================================================================
additional_functions = ["DAMPING"]

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
# OPTIMIZATION CONFIGURATION
# ============================================================================
optimization = {
    "enabled": True,
    "mode": "objective_based",
    "objective_type": "minimize", 
    "objective_function": "tracking",
    "targets": {
        "x_target": 0.0
    },
    "weights": {
        "position_weight": 1.0,
        "velocity_weight": 0.1
    },
    "optimization_variables": ["k_eff"]
}

# ============================================================================
# LOGIC PARAMETERS
# ============================================================================
logic_parameters = {}

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
# System data with native sparse tensor support
system_data = {
    "x": x,  # Sparse position tensor (auto-detected unknown)
    "v": v,  # Sparse velocity tensor (auto-detected unknown)
    # NOTE: unknown_parameters auto-detected by framework - no need to specify!
    "parameters": parameters,
    "additional_functions": additional_functions,
    "equations": equations,
    "dt_value": dt_value,
    "final_time": final_time,
    "minlp_enabled": minlp_enabled,
    "solver": solver,
    "solve_mode": solve_mode,
    "discrete_parameters": discrete_parameters,
    "optimization": optimization,
    "logic_parameters": logic_parameters,
    "discrete_logic": discrete_logic,
    "description": description
}
