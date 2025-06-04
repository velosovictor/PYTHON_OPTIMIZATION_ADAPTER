"""
Postprocessing Module

This module provides functionality for packaging simulation solutions into xarray Datasets
and inserting them into MongoDB for persistent storage and retrieval.
"""
import xarray as xr
from pymongo import MongoClient

def package_solution(tau, sol_dict, dt_value, final_time, description="Results from the ODE solved with Pyomo"):
    """
    Packages solution variables in an xarray Dataset.

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
