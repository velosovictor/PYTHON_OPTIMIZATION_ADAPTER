# ============================================================================
# POSTPROCESSING MODULE
# ============================================================================
# Packages simulation solutions into xarray Datasets
# Provides data structure for analysis and visualization

import xarray as xr
from pymongo import MongoClient

# ============================================================================
# SOLUTION PACKAGING FUNCTION
# ============================================================================
def package_solution(tau, sol_dict, dt_value, final_time, description="Results from the ODE solved with Pyomo"):
    # Packages solution variables in xarray Dataset
    # Creates structured data with time coordinates and metadata
    
    ds = xr.Dataset(
        data_vars={ var: (("time"), sol_dict[var]) for var in sol_dict },
        coords={"time": tau},
        attrs={
            "dt": dt_value,
            "final_time": final_time,
            "description": description
        }
    )
    return ds
