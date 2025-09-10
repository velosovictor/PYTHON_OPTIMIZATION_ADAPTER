# ============================================================================
# PARAMETERS MODULE
# ============================================================================
# Handles loading and updating of simulation parameters from JSON configuration
# Manages time step, simulation duration, initial conditions, solver settings
# Includes dynamic loading of user lookup tables

import os
import json
import importlib.util
from typing import Dict, Any, Optional

# ============================================================================
# GLOBAL VARIABLE DECLARATIONS
# ============================================================================
# Dynamic parameter storage - populated from user data folders
_lookup_tables = None
_loaded_parameters = {}

# ============================================================================
# CONFIGURATION CONSTANTS  
# ============================================================================
DEFAULT_PARAMS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_data_example", "object_data.json")

# ============================================================================
# PARAMETER LOADING FUNCTIONS
# ============================================================================
def load_parameters_from_folder(data_folder=None):
    # Load parameters from specified data folder or use defaults
    # Returns parsed JSON configuration dictionary
    
    if data_folder:
        params_file = os.path.join(data_folder, "object_data.json")
        if not os.path.exists(params_file):
            raise FileNotFoundError(f"object_data.json not found in {data_folder}")
    else:
        params_file = DEFAULT_PARAMS_FILE
    
    with open(params_file, 'r') as f:
        return json.load(f)

def load_lookup_tables_from_folder(data_folder):
    # Load lookup tables from user's lookup.py file
    # Returns dictionary of lookup tables or empty dict if not found
    
    lookup_file = os.path.join(data_folder, "lookup.py")
    if not os.path.exists(lookup_file):
        return {}
    
    try:
        spec = importlib.util.spec_from_file_location("user_lookup", lookup_file)
        user_lookup_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_lookup_module)
        
        if hasattr(user_lookup_module, 'lookup_tables'):
            return user_lookup_module.lookup_tables
        else:
            return {}
    except Exception as e:
        print(f"Warning: Error loading lookup tables from {lookup_file}: {e}")
        return {}

def update_parameters_with_json(json_data):
    # Update in-memory parameters with new JSON data
    # Used for real-time parameter updates in timewise mode
    global _loaded_parameters
    
    _loaded_parameters.update(json_data)

# ============================================================================
# LOOKUP TABLE ACCESS FUNCTIONS
# ============================================================================
def get_lookup_tables():
    # Get all loaded lookup tables
    return _lookup_tables

def get_lookup_value(table_name: str, key: Any) -> Any:
    # Get value from a specific lookup table
    if table_name not in _lookup_tables:
        raise KeyError(f"Lookup table '{table_name}' not found")
    
    indep_var_name, data_array = _lookup_tables[table_name]
    if key not in data_array.coords[indep_var_name]:
        raise KeyError(f"Key '{key}' not found in lookup table '{table_name}'")
    
    return data_array.sel({indep_var_name: key}).values

# ============================================================================
# PARAMETER REINITIALIZATION FUNCTION
# ============================================================================
def initialize_with_data_folder(data_folder):
    # Reinitialize all parameters with a custom data folder
    # Updates all global parameter variables and loads lookup tables
    
    global _loaded_parameters, _lookup_tables
    
    _loaded_parameters = load_parameters_from_folder(data_folder)
    _lookup_tables = load_lookup_tables_from_folder(data_folder)

# ============================================================================
# PARAMETER ACCESS FUNCTIONS
# ============================================================================
def get_parameter(key, default=None):
    # Get parameter value by key from loaded parameters
    return _loaded_parameters.get(key, default)

def get_all_parameters():
    # Get all loaded parameters as dictionary
    return _loaded_parameters.copy()

def set_parameter(key, value):
    # Set parameter value in loaded parameters
    global _loaded_parameters
    _loaded_parameters[key] = value

# ============================================================================
# INITIALIZATION
# ============================================================================
# Initialize with default parameters and lookup tables on module import
_loaded_parameters = load_parameters_from_folder()
_lookup_tables = load_lookup_tables_from_folder(os.path.dirname(DEFAULT_PARAMS_FILE))

# All parameters are now accessed through get_parameter() function calls
