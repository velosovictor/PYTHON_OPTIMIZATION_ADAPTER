"""
Parameters Module

This module handles the loading and updating of simulation parameters from a JSON file.
It defines key parameters such as the time step (dt_value), simulation duration (final_time),
initial conditions, solver settings, logic parameters, and other configuration flags.
"""

import os
import json

PARAMS_FILE = os.path.join(os.path.dirname(__file__), "user_data", "object_data.json")
SPECIAL_KEYS = (
    "init_conditions", "dt_value", "final_time", "minlp_enabled",
    "solver", "discrete_parameters", "logic_constraints",
    "solve_mode", "live_plotting",
    "unknown_parameters", "additional_functions", "equations"
)

# We will store all standard numeric parameters in `config_parameters`,
# and store the discrete logic parameters in `logic_parameters`.
config_parameters = {}
logic_parameters = {}

def load_parameters():
    with open(PARAMS_FILE, "r") as f:
        data = json.load(f)

    global config_parameters, dt_value, final_time
    global init_conditions, minlp_enabled, solver_name
    global discrete_parameters, solve_mode, live_plotting
    global logic_parameters

    # Load primary numeric parameters:
    config_parameters = data.get("parameters", {})

    # Load logic parameters here instead of in logic_definitions.py
    logic_parameters = data.get("logic_parameters", {})

    dt_value         = data.get("dt_value", 0.1)
    final_time       = data.get("final_time", 10)
    init_conditions  = data.get("init_conditions", {})
    minlp_enabled    = data.get("minlp_enabled", False)
    solver_name      = data.get("solver", "ipopt")
    discrete_parameters = data.get("discrete_parameters", [])
    solve_mode       = data.get("solve_mode", "monolithic")
    live_plotting    = data.get("live_plotting", False)

    return data

# Perform the initial load once on import.
params_data = load_parameters()

# For convenience, expose config_parameters under a common alias.
param_mapping = config_parameters

def update_parameters():
    new_params = load_parameters()
    print("Updated m =", new_params.get("parameters", {}).get("m"))

def update_parameters_with_json(json_data):
    """
    Update the in-memory parameters with whatever is in json_data.
    Now also update logic_parameters so the logic constraints pick up new values.
    """
    global config_parameters, logic_parameters, live_plotting

    # Update numeric 'parameters' 
    config_parameters.update(json_data.get("parameters", {}))

    # Update the logic_parameters too.
    if "logic_parameters" in json_data:
        logic_parameters.update(json_data["logic_parameters"])

    # Update the live_plotting flag if present.
    live_plotting = json_data.get("live_plotting", live_plotting)
