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
# Point to the example folder at the root level
DEFAULT_PARAMS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_data_example", "object_data.json")
SPECIAL_KEYS = (
    "init_conditions", "dt_value", "final_time", "minlp_enabled",
    "solver", "discrete_parameters", "logic_constraints",
    "solve_mode", "live_plotting",
    "unknown_parameters", "additional_functions", "equations"
)

def load_parameters_from_folder(data_folder=None):
    """
    Load parameters from specified data folder or use defaults
    
    Args:
        data_folder (str, optional): Path to folder containing object_data.json
    
    Returns:
        dict: Loaded parameters
    """
    if data_folder:
        params_file = os.path.join(data_folder, "object_data.json")
        if not os.path.exists(params_file):
            raise FileNotFoundError(f"object_data.json not found in {data_folder}")
    else:
        params_file = DEFAULT_PARAMS_FILE
    
    with open(params_file, 'r') as f:
        return json.load(f)

# ============================================================================
# GLOBAL PARAMETER STORAGE
# ============================================================================
config_parameters = {}  # Standard numeric parameters
logic_parameters = {}   # Discrete logic parameters

# ============================================================================
# PARAMETER LOADING FUNCTIONS
# ============================================================================
# Removed old load_parameters() function - now using load_parameters_from_folder()

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
# Perform initial load on module import (using defaults)
# Initialize with default internal data folder first
params_data = load_parameters_from_folder()

# Initialize all global variables with default values
config_parameters = params_data.get("parameters", {})
dt_value = params_data.get("dt_value", 0.1)
final_time = params_data.get("final_time", 10.0)
init_conditions = params_data.get("init_conditions", {})
minlp_enabled = params_data.get("minlp_enabled", False)
solver_name = params_data.get("solver", "ipopt")
discrete_parameters = params_data.get("discrete_parameters", [])
solve_mode = params_data.get("solve_mode", "monolithic")
live_plotting = params_data.get("live_plotting", False)
logic_parameters = params_data.get("logic_parameters", {})
param_mapping = config_parameters  # Convenient alias for parameter mapping

# Function to reinitialize with custom data folder
def initialize_with_data_folder(data_folder):
    """Reinitialize all parameters with a custom data folder"""
    global params_data, config_parameters, dt_value, final_time, minlp_enabled
    global logic_parameters, solver_name, discrete_parameters, solve_mode, live_plotting
    
    params_data = load_parameters_from_folder(data_folder)
    
    # Update all global variables
    config_parameters = params_data.get("parameters", {})
    dt_value = params_data.get("dt_value", 0.1)
    final_time = params_data.get("final_time", 10.0)
    minlp_enabled = params_data.get("minlp_enabled", False)
    logic_parameters = params_data.get("logic_parameters", {})
    solver_name = params_data.get("solver", "ipopt")
    discrete_parameters = params_data.get("discrete_parameters", [])
    solve_mode = params_data.get("solve_mode", "monolithic")
    live_plotting = params_data.get("live_plotting", False)
