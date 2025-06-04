"""
Postprocessing Live Module

This module provides functionality for handling live or streaming simulation results,
packaging them into xarray Datasets for analysis and visualization.
"""
import numpy as np
import xarray as xr

def package_solution_live(tau, sol_dict, dt_value, final_time, description="Live results"):
    """
    Packages live solution variables in an xarray Dataset.

    Parameters
    ----------
    tau : array_like
        Time grid for the solution.
    sol_dict : dict
        Dictionary mapping variable names to their solution arrays.
    dt_value : float
        Time discretization step size.
    final_time : float
        The final time of the simulation.
    description : str, optional
        Description for the dataset.

    Returns
    -------
    ds : xarray.Dataset
        Dataset containing the solution variables, coordinates, and attributes.
    """
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
