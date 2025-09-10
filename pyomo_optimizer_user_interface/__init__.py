"""
Pyomo Optimizer User Interface

A powerful Python library for solving mixed-integer nonlinear programming (MINLP) 
problems using Pyomo and Generalized Disjunctive Programming (GDP).
"""

# ============================================================================
# PACKAGE METADATA
# ============================================================================
__version__ = "1.0.0"
__author__ = "Victor Veloso"
__email__ = "velosovictor@example.com"
__description__ = "A Python library for Mixed-Integer Nonlinear Programming (MINLP) simulation framework"

# ============================================================================
# IMPORTS
# ============================================================================
from .main import run
from .parameters import load_parameters_from_folder, update_parameters, initialize_with_data_folder

# ============================================================================
# USER HELPER FUNCTIONS
# ============================================================================
def create_sample_config(target_folder=None):
    """
    Create a sample object_data.json configuration file in the specified folder
    
    Args:
        target_folder (str, optional): Folder where to create the config file.
                                     If None, uses current working directory.
    """
    import os
    import json
    import shutil
    
    if target_folder is None:
        target_folder = os.getcwd()
    
    # Source file from the package
    source_file = os.path.join(os.path.dirname(__file__), "user_data", "object_data.json")
    target_file = os.path.join(target_folder, "object_data.json")
    
    if os.path.exists(target_file):
        print(f"⚠️  Configuration file already exists at {target_file}")
        return False
    
    try:
        shutil.copy2(source_file, target_file)
        print(f"✅ Sample configuration created at: {target_file}")
        print("📝 Edit this file to customize your optimization problem")
        return True
    except Exception as e:
        print(f"❌ Error creating config file: {e}")
        return False

# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    "run",
    "create_sample_config",
    "load_parameters_from_folder", 
    "update_parameters",
    "initialize_with_data_folder",
    "__version__",
]
