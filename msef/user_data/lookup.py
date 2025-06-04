# =============================================================================
# Cell 2.5: DataArray Restrictions (Lookup Tables)
# =============================================================================
# Define a dictionary of lookup tables. Each entry is of the form:
#    lookup_tables = { "LOOKUP_NAME": (independent_variable_name, DataArray) }
# For example, to replace damping with a lookup table based on x:

import numpy as np
import xarray as xr

# Example: replicating damping = 1+0.1*x over x ∈ [-2,2]
damping_lookup = xr.DataArray(1 + 0.1 * np.linspace(-2, 2, 100),
                              coords={"x": np.linspace(-2, 2, 100)},
                              dims=["x"])
lookup_tables = {
    "DAMPING": ("x", damping_lookup)
}
# (If you want more lookup-based restrictions, simply add more entries to this dictionary.)
