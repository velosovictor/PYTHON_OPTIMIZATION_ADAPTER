"""
MSEF - Mixed-Integer Nonlinear Programming Framework

A powerful Python library for solving mixed-integer nonlinear programming (MINLP) 
problems using Pyomo and Generalized Disjunctive Programming (GDP).
"""

# ============================================================================
# PYOMO INTERFACE TOOL
# ============================================================================
# Mixed-Integer Nonlinear Programming (MINLP) simulation framework
# Provides tools for optimization with discrete logic constraints

# ============================================================================
# PYOMO INTERFACE TOOL
# ============================================================================
# Mixed-Integer Nonlinear Programming (MINLP) simulation framework
# Provides optimization capabilities with SCIP solver integration

# ============================================================================
# PYOMO INTERFACE TOOL PACKAGE
# ============================================================================
__version__ = "1.0.0"
__author__ = "Victor Veloso"
__description__ = "A Python library for Mixed-Integer Nonlinear Programming (MINLP) simulation framework"

from .main import run

__all__ = ["run"]

from .main import run
from .solver_config import set_scip_path

__all__ = ["run", "set_scip_path", "__version__"]

# Import main functions for easy access
from .main import run
from .solver_config import set_scip_path

__all__ = ["run", "set_scip_path"]
__author__ = "Victor Veloso"
__email__ = "velosovictor@example.com"

# Import main functions for easy access
from .main import run
from .parameters import load_parameters, update_parameters
from .build_global_model import build_global_model
from .solver import solve_model, extract_solution
from .postprocessing import package_solution

__all__ = [
    "run",
    "load_parameters", 
    "update_parameters",
    "build_global_model",
    "solve_model",
    "extract_solution", 
    "package_solution",
    "__version__",
]
