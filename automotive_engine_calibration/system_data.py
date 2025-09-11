# ============================================================================
# SYSTEM DATA SPECIFICATION
# ============================================================================
# Automotive Engine Calibration - ECU Optimization Example
# Real-world test case: 0-100 km/h acceleration optimization

import numpy as np
import xarray as xr

# ============================================================================
# PROBLEM IDENTIFICATION
# ============================================================================
description = "Simple Engine Calibration: Fuel injection optimization for steady-state operation"

# ============================================================================
# SIMPLE ENGINE OPERATING POINTS
# ============================================================================
# Time horizon for engine calibration
time_horizon = np.linspace(0, 2.0, int(2.0/0.5) + 1)  # [0, 0.5, 1.0, 1.5, 2.0] - 5 points

# Collect all tensors in a dictionary for automatic export
tensors = {}

# Engine Power - simple output we want to maximize
power_data = np.full(len(time_horizon), np.nan)  # All unknown - to be calculated
power_data[0] = 50.0  # Initial condition: start at 50 kW
tensors["engine_power"] = xr.DataArray(
    data=power_data,
    coords={"time": time_horizon},
    dims=["time"],
    attrs={"bounds": (40.0, 200.0), "units": "kW", "description": "Engine power output"}
)

# Fuel Rate - what we want to control
fuel_rate_data = np.full(len(time_horizon), np.nan)  # All unknown - to be calculated  
fuel_rate_data[0] = 5.0  # Initial condition: start at 5 g/s
tensors["fuel_rate"] = xr.DataArray(
    data=fuel_rate_data,
    coords={"time": time_horizon},
    dims=["time"],
    attrs={"bounds": (3.0, 20.0), "units": "g/s", "description": "Fuel consumption rate"}
)

# Framework will auto-detect unknowns - NO coding logic here!

# ============================================================================
# ENGINE PARAMETERS (SIMPLE MODEL)
# ============================================================================
parameters = {
    # Engine calibration coefficients (simple linear model)
    "power_gain": 4.0,            # kW per mg fuel injection
    "timing_boost": 0.5,          # power boost per degree timing advance
    "base_consumption": 2.0,      # g/s base fuel consumption
    "consumption_rate": 0.15,     # fuel consumption per kW power
}

# ============================================================================
# SIMPLE ENGINE EQUATIONS
# ============================================================================
equations = [
    # Power dynamics: simple differential equation
    "diff(engine_power(t), t) - (fuel_injection(t) * power_gain + ignition_timing(t) * timing_boost - engine_power(t)) * 2.0 = 0",
    
    # Fuel consumption model: linear relationship to power
    "fuel_rate(t) - (base_consumption + engine_power(t) * consumption_rate) = 0"
]

# ============================================================================
# SIMULATION SETTINGS
# ============================================================================
dt_value = 0.5      # Time step
final_time = 2.0    # Total simulation time
minlp_enabled = True
solver = "scip"
solve_mode = "monolithic"

# ============================================================================
# DISCRETE PARAMETERS
# ============================================================================
discrete_parameters = [
    {
        "name": "fuel_injection",
        "domain": "reals", 
        "bounds": [8.0, 30.0]  # Narrower, safer range
    },
    {
        "name": "ignition_timing",
        "domain": "reals",
        "bounds": [15.0, 35.0]  # Conservative timing range
    }
]

# ============================================================================
# ENGINE OPTIMIZATION OBJECTIVE
# ============================================================================
optimization = {
    "enabled": True,
    
    # OBJECTIVE: Maximize final engine power
    "target_parameter": "engine_power",
    "target_expression": "engine_power[-1]",      # Maximize final power
    "objective_type": "maximize",
    
    # TUNING VARIABLES: Fuel injection and ignition timing
    "tuning_variables": ["fuel_injection", "ignition_timing"],
    
    # RESULT: Optimal fuel injection and ignition timing for maximum power
}

# ============================================================================
# DISCRETE LOGIC CONSTRAINTS (DISABLED FOR SIMPLICITY)
# ============================================================================
discrete_logic = {
    "logic_constraints": []
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
