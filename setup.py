from setuptools import setup, find_packages

setup(
    name="pyomo_interface_tool",
    version="1.0.0",
    author="Victor Veloso",
    description="A Python library for Mixed-Integer Nonlinear Programming (MINLP) simulation framework",
    packages=find_packages(),
    install_requires=[
        "sympy",
        "pyomo",
        "numpy",
        "matplotlib",
        "xarray",
        "pymongo",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) import setup, find_packages

setup(
    name="pyomo_interface_tool",
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
