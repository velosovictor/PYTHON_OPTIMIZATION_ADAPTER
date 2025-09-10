# ============================================================================
# POSTPROCESSING MODULE
# ============================================================================
# Packages simulation solutions into xarray Datasets for analysis and visualization
# Handles both static and live/streaming results

import numpy as np
import xarray as xr

# ============================================================================
# SOLUTION PACKAGING FUNCTIONS
# ============================================================================
def package_solution(tau, sol_dict, dt_value, final_time, description="Results from the ODE solved with Pyomo"):
    # Packages solution variables in xarray Dataset
    # Creates structured data with time coordinates and metadata
    
    ds = xr.Dataset(
        data_vars={var: (("time"), sol_dict[var]) for var in sol_dict},
        coords={"time": tau},
        attrs={
            "dt": dt_value,
            "final_time": final_time,
            "description": description
        }
    )
    return ds

def package_solution_live(tau, sol_dict, dt_value, final_time, description="Live results"):
    # Packages live solution variables in xarray Dataset
    # Handles truncated time series for real-time updates
    
    truncated_tau = np.array(tau)
    data_vars = {
        var: (("time",), sol_dict[var][:len(truncated_tau)])
        for var in sol_dict
    }
    
    ds = xr.Dataset(
        data_vars=data_vars,
        coords={"time": truncated_tau},
        attrs={"dt": dt_value, "final_time": final_time, "description": description}
    )
    return ds
