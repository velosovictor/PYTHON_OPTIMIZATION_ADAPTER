# ============================================================================
# SOLVER CONFIGURATION MODULE
# ============================================================================
# Handles solver path configuration and initialization
# Allows users to specify custom SCIP installation paths

import os
import sys

# ============================================================================
# SCIP CONFIGURATION
# ============================================================================
_scip_path = None

def set_scip_path(path):
    # Sets the SCIP installation path for the solver
    # User must call this before using SCIP solver
    global _scip_path
    if not os.path.exists(path):
        raise ValueError(f"SCIP path does not exist: {path}")
    
    _scip_path = path
    
    # Add SCIP to PATH if not already there
    scip_bin = os.path.join(path, "bin")
    if scip_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = scip_bin + os.pathsep + os.environ.get("PATH", "")
    
    # Add to Python path for pyscipopt if available
    if scip_bin not in sys.path:
        sys.path.insert(0, scip_bin)
    
    print(f"SCIP path set to: {path}")

def get_scip_path():
    # Returns the currently configured SCIP path
    return _scip_path

def is_scip_configured():
    # Checks if SCIP path has been configured
    return _scip_path is not None
