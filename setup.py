from setuptools import setup, find_packages

setup(
    name="msef_solver_interface",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "sympy",
        "pyomo",
        "numpy",
        "matplotlib",
        "xarray",
        "pymongo",
    ],
)
