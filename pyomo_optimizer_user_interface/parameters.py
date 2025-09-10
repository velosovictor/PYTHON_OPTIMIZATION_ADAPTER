# ============================================================================
# PARAMETERS MODULE
# ============================================================================
# Handles loading and updating of simulation parameters from Python system_data
# Full Python approach with native xarray tensor support
# Manages time step, simulation duration, initial conditions, solver settings

import os
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
DEFAULT_SYSTEM_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_data_example", "system_data.py")

# ============================================================================
# PARAMETER LOADING FUNCTIONS
# ============================================================================
def load_parameters_from_folder(data_folder=None):
    # Load parameters from system_data.py in specified folder or use defaults
    # Full Python approach with native xarray tensor support
    
    if data_folder:
        system_data_file = os.path.join(data_folder, "system_data.py")
        if not os.path.exists(system_data_file):
            raise FileNotFoundError(f"system_data.py not found in {data_folder}")
        return load_system_data_from_file(system_data_file)
    else:
        return load_system_data_from_file(DEFAULT_SYSTEM_DATA_FILE)

def load_system_data_from_file(system_data_file):
    # Load system data from Python module file
    # Returns system_data dictionary with full Python tensor support
    
    try:
        spec = importlib.util.spec_from_file_location("system_data", system_data_file)
        system_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(system_module)
        
        if hasattr(system_module, 'system_data'):
            return system_module.system_data
        else:
            raise AttributeError("system_data dictionary not found in module")
    except Exception as e:
        raise RuntimeError(f"Error loading system data from {system_data_file}: {e}")

def load_lookup_tables_from_system_data(system_module):
    # Extract lookup tables from system_data module
    # Returns dictionary of lookup tables for compatibility
    
    if hasattr(system_module, 'lookup_tables'):
        return system_module.lookup_tables
    else:
        return {}

def update_parameters_with_data(system_data):
    # Update in-memory parameters with new system data
    # Used for real-time parameter updates in timewise mode
    global _loaded_parameters
    
    _loaded_parameters.update(system_data)

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
    # Updates all global parameter variables and loads lookup tables from system_data.py
    
    global _loaded_parameters, _lookup_tables
    
    system_data_file = os.path.join(data_folder, "system_data.py")
    
    # Load system data
    _loaded_parameters = load_system_data_from_file(system_data_file)
    
    # Load lookup tables from the same system_data module
    spec = importlib.util.spec_from_file_location("system_data", system_data_file)
    system_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(system_module)
    _lookup_tables = load_lookup_tables_from_system_data(system_module)

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

def detect_unknown_parameters():
    """Auto-detect unknown parameters from sparse tensor analysis - FRAMEWORK LOGIC"""
    import numpy as np
    import xarray as xr
    
    unknown_params = []
    for name, value in _loaded_parameters.items():
        if isinstance(value, xr.DataArray):
            # Check if xarray tensor has NaN values (indicating unknowns)
            if np.any(np.isnan(value.values)):
                unknown_params.append(name)
    
    return unknown_params

# ============================================================================
# INITIALIZATION
# ============================================================================
# Initialize with default system data and lookup tables on module import
_loaded_parameters = load_system_data_from_file(DEFAULT_SYSTEM_DATA_FILE)

# Load lookup tables from default system_data module
spec = importlib.util.spec_from_file_location("system_data", DEFAULT_SYSTEM_DATA_FILE)
system_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(system_module)
_lookup_tables = load_lookup_tables_from_system_data(system_module)

# All parameters are now accessed through get_parameter() function calls
