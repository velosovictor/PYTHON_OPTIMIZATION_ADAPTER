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
description = "Automotive ECU Calibration: Engine optimization for 0-100 km/h acceleration"

# ============================================================================
# NUMERICAL RESTRICTIONS (AUTOMOTIVE ENGINE VARIABLES)
# ============================================================================
# Time horizon for acceleration test 
time_horizon = np.linspace(0, 1.0, int(1.0/0.1) + 1)  # [0, 0.1, 0.2, ..., 1.0]

# Collect all tensors in a dictionary for automatic export
tensors = {}

# Vehicle Speed tensor: only initial condition specified, rest unknown
vehicle_speed_data = np.full(len(time_horizon), np.nan)  # All unknown initially
vehicle_speed_data[0] = 0.0  # Only specify known initial condition: v(0) = 0 km/h
tensors["vehicle_speed"] = xr.DataArray(
    data=vehicle_speed_data,
    coords={"time": time_horizon},
    dims=["time"],
    attrs={"bounds": (0.0, 150.0)}  # 0-150 km/h reasonable for acceleration test
)

# Engine RPM tensor: only initial condition specified, rest unknown
engine_rpm_data = np.full(len(time_horizon), np.nan)  # All unknown initially  
engine_rpm_data[0] = 1000.0  # Only specify known initial condition: rpm(0) = 1000
tensors["engine_rpm"] = xr.DataArray(
    data=engine_rpm_data,
    coords={"time": time_horizon}, 
    dims=["time"],
    attrs={"bounds": (800.0, 7000.0)}  # Typical automotive engine RPM range
)

# Engine Power tensor: fully unknown (calculated from fuel + timing)
engine_power_data = np.full(len(time_horizon), np.nan)  # All unknown
tensors["engine_power"] = xr.DataArray(
    data=engine_power_data,
    coords={"time": time_horizon},
    dims=["time"],
    attrs={"bounds": (0.0, 250.0)}  # 0-250 kW reasonable engine power range
)

# Fuel Consumption tensor: fully unknown (calculated from power + efficiency)
fuel_consumption_data = np.full(len(time_horizon), np.nan)  # All unknown
tensors["fuel_consumption"] = xr.DataArray(
    data=fuel_consumption_data,
    coords={"time": time_horizon},
    dims=["time"],
    attrs={"bounds": (0.0, 50.0)}  # 0-50 L/h reasonable fuel consumption range
)

# Framework will auto-detect unknowns - NO coding logic here!

# ============================================================================
# SCALAR PARAMETERS (ZERO DIMENSIONAL TENSORS)
# ============================================================================
parameters = {
    # Engine specifications
    "max_power": 200.0,           # kW - maximum engine power
    "vehicle_mass": 1500.0,       # kg - vehicle mass  
    "transmission_eff": 0.95,     # transmission efficiency
    "base_fuel_rate": 8.0,        # L/100km base consumption
    
    # Control limits
    "min_rpm": 800.0,
    "max_rpm": 7000.0,
    "min_fuel": 5.0,
    "max_fuel": 40.0
}

# ============================================================================
# SYSTEM EQUATIONS
# ============================================================================
equations = [
    # Vehicle dynamics: acceleration from engine power
    "diff(vehicle_speed(t), t) - (engine_power(t) * transmission_eff / vehicle_mass - vehicle_speed(t) * 0.1) * 3.6 = 0",
    
    # Engine dynamics: RPM follows power demand
    "diff(engine_rpm(t), t) - (engine_power(t) * 30.0 / max_power - engine_rpm(t) + 1000.0) * 2.0 = 0",
    
    # Power generation: function of fuel injection and ignition timing
    "engine_power(t) - fuel_injection(t) * ignition_timing(t) * engine_rpm(t) * 0.00001 = 0",
    
    # Fuel consumption: based on power output and efficiency
    "fuel_consumption(t) - engine_power(t) * (base_fuel_rate + 0.001 * engine_rpm(t)) * 0.01 = 0"
]

# ============================================================================
# SIMULATION SETTINGS
# ============================================================================
dt_value = 0.1
final_time = 1.0
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
        "bounds": [5.0, 40.0]
    },
    {
        "name": "ignition_timing",
        "domain": "reals",
        "bounds": [10.0, 45.0]
    }
]

# ============================================================================
# OPTIMIZATION CONFIGURATION - TENSOR-BASED APPROACH
# ============================================================================
optimization = {
    "enabled": True,
    
    # PARAMETER A: What we want to optimize
    "target_parameter": "vehicle_speed",          # The tensor we want optimal values for
    "target_expression": "vehicle_speed[-1]",     # OBJECTIVE: maximize final speed
    "objective_type": "maximize",                 # maximize the target_expression
    
    # PARAMETER B: What we tune to achieve optimal Parameter A  
    "tuning_variables": ["fuel_injection", "ignition_timing"],
    
    # RESULT: Framework returns optimal vehicle_speed(t) + optimal fuel/timing
}

# ============================================================================
# DISCRETE LOGIC CONSTRAINTS
# ============================================================================
discrete_logic = {
    "logic_constraints": [
        {
            "name": "fuel_injection_logic",
            "disjunction": [
                {
                    "conditions": ["vehicle_speed <= 30.0"],
                    "assignments": ["fuel_injection <= 20.0"]  # Economy mode
                },
                {
                    "conditions": ["vehicle_speed >= 70.0"], 
                    "assignments": ["fuel_injection >= 25.0"]  # Performance mode
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
