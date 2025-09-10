# ============================================================================
# PARAMETERS MODULE
# ============================================================================
# Handles loading and updating of simulation parameters from JSON configuration
# Manages time step, simulation duration, initial conditions, solver settings,
# logic parameters, and other configuration flags

import os
import json

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================
PARAMS_FILE = os.path.join(os.path.dirname(__file__), "user_data", "object_data.json")
SPECIAL_KEYS = (
    "init_conditions", "dt_value", "final_time", "minlp_enabled",
    "solver", "discrete_parameters", "logic_constraints",
    "solve_mode", "live_plotting",
    "unknown_parameters", "additional_functions", "equations"
)

# ============================================================================
# GLOBAL PARAMETER STORAGE
# ============================================================================
config_parameters = {}  # Standard numeric parameters
logic_parameters = {}   # Discrete logic parameters

# ============================================================================
# PARAMETER LOADING FUNCTIONS
# ============================================================================
def load_parameters():
    # Load all parameters from the JSON configuration file
    with open(PARAMS_FILE, "r") as f:
        data = json.load(f)

    global config_parameters, dt_value, final_time
    global init_conditions, minlp_enabled, solver_name
    global discrete_parameters, solve_mode, live_plotting
    global logic_parameters

    # Load primary numeric parameters
    config_parameters = data.get("parameters", {})
    logic_parameters = data.get("logic_parameters", {})

    # Load simulation settings
    dt_value = data.get("dt_value", 0.1)
    final_time = data.get("final_time", 10)
    init_conditions = data.get("init_conditions", {})
    minlp_enabled = data.get("minlp_enabled", False)
    solver_name = data.get("solver", "ipopt")
    discrete_parameters = data.get("discrete_parameters", [])
    solve_mode = data.get("solve_mode", "monolithic")
    live_plotting = data.get("live_plotting", False)

    return data

def update_parameters():
    # Simple parameter reload with debug output
    new_params = load_parameters()
    print("Updated m =", new_params.get("parameters", {}).get("m"))

def update_parameters_with_json(json_data):
    # Update in-memory parameters with new JSON data
    # Used for real-time parameter updates in timewise mode
    global config_parameters, logic_parameters, live_plotting

    # Update numeric parameters
    config_parameters.update(json_data.get("parameters", {}))

    # Update logic parameters for discrete constraints
    if "logic_parameters" in json_data:
        logic_parameters.update(json_data["logic_parameters"])

    # Update live plotting flag
    live_plotting = json_data.get("live_plotting", live_plotting)

# ============================================================================
# INITIALIZATION
# ============================================================================
# Perform initial load on module import
params_data = load_parameters()
param_mapping = config_parameters  # Convenient alias for parameter mapping
