# ============================================================================
# LIVE POSTPROCESSING MODULE
# ============================================================================
# Handles live/streaming simulation results for real-time visualization
# Creates truncated datasets for ongoing simulations

import numpy as np
import xarray as xr

# ============================================================================
# LIVE SOLUTION PACKAGING FUNCTION
# ============================================================================
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
