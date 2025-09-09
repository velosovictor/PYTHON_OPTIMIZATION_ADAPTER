# MSEF - Mixed Symbolic Equation Framework

A sophisticated Python optimization adapter that provides real-time simulation capabilities for Mixed-Integer Nonlinear Programming (MINLP) problems with Ordinary Differential Equations (ODEs). This framework combines the power of **IPOPT** (continuous optimization) and **SCIP** (discrete optimization) through **Pyomo** to solve hybrid dynamical systems.

## 🎯 What This Framework Does

This is a **hybrid optimization system** that can:
- ✅ Solve **continuous nonlinear ODEs** with IPOPT
- ✅ Handle **discrete logic constraints** with SCIP  
- ✅ Perform **real-time parameter updates** during simulation
- ✅ Provide **live plotting** of results
- ✅ Support both **monolithic** and **timewise** solving approaches
- ✅ Handle **piecewise functions** through lookup tables
- ✅ Process **Generalized Disjunctive Programming** (GDP) constraints

### Example Applications
- **Mechanical systems** with switching behavior (springs with variable stiffness)
- **Process control** with discrete operating modes
- **Robotics** with contact/non-contact phases  
- **Autonomous systems** with decision-making logic
- **Hybrid dynamical systems** in general

---

## 🚀 Complete Installation Guide

### Prerequisites
- Windows 10/11 with WSL2 capability
- At least 4GB RAM and 2GB free disk space
- Basic familiarity with command line (we'll guide you through everything!)

---

## 📋 Step 1: Setting Up WSL (Windows Subsystem for Linux)

### 1.1 Install WSL2
Open **PowerShell** as Administrator and run:
```powershell
# Install WSL2 with Ubuntu
wsl --install -d Ubuntu
```

**If WSL is already installed**, check your distributions:
```powershell
wsl --list
```

### 1.2 Access WSL Terminal
After installation, you can access WSL in several ways:
- Type `wsl` in PowerShell
- Search "Ubuntu" in Windows Start Menu
- In VS Code: `Ctrl+Shift+P` → "Terminal: Create New Terminal" → Select WSL

### 1.3 Update Ubuntu System
Once in WSL, update the package manager:
```bash
sudo apt update && sudo apt upgrade -y
```

---

## 📂 Step 2: Clone the Project

### 2.1 Navigate to Home Directory
```bash
cd ~
```

### 2.2 Clone the Repository
```bash
git clone https://github.com/velosovictor/PYTHON_OPTIMIZATION_ADAPTER.git
cd PYTHON_OPTIMIZATION_ADAPTER
```

---

## 🔧 Step 3: Install System Dependencies

### 3.1 Install Build Tools
```bash
sudo apt install -y gcc g++ gfortran git patch wget pkg-config \
                    liblapack-dev libblas-dev cmake build-essential \
                    libgmp-dev libreadline-dev libncurses-dev libz-dev \
                    libboost-all-dev libtbb-dev python3 python3-pip python3-venv
```

**What this installs:**
- **gcc, g++, gfortran**: C/C++/Fortran compilers
- **cmake**: Build system generator
- **liblapack-dev, libblas-dev**: Linear algebra libraries
- **libboost-all-dev**: C++ Boost libraries
- **python3-venv**: Python virtual environment support

---

## 🎯 Step 4: Install IPOPT (Continuous Optimization Solver)

### 4.1 Install IPOPT via Package Manager
```bash
sudo apt install -y coinor-libipopt1v5 coinor-libipopt-dev coinor-libipopt-doc
```

### 4.2 Verify IPOPT Installation
```bash
pkg-config --modversion ipopt
```
**Expected output:** `3.11.9` (or similar version number)

**What IPOPT does:** Solves large-scale nonlinear continuous optimization problems using interior-point methods. In your framework, it handles the smooth ODE dynamics.

---

## 🎲 Step 5: Install SCIP (Discrete Optimization Solver)

### 5.1 Install Miniconda
```bash
# Navigate to home directory
cd ~

# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3

# Add conda to PATH
export PATH="$HOME/miniconda3/bin:$PATH"
```

### 5.2 Accept Conda Terms of Service
```bash
# Accept Terms of Service for required channels
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

### 5.3 Install SCIP via Conda
```bash
# Install SCIP from conda-forge (takes 2-5 minutes)
conda install -c conda-forge scip -y
```

### 5.4 Verify SCIP Installation
```bash
scip --version
```
**Expected output:** 
```
SCIP version 7.0.3 [precision: 8 byte] [memory: block] [mode: optimized] [LP solver: SoPlex 5.0.2] [GitHash: 74c11e60cd]
External libraries:
  SoPlex 5.0.2         Linear Programming Solver
  Ipopt 3.14.1         Interior Point Optimizer
  GMP 6.2.1            GNU Multiple Precision Arithmetic Library
  ZIMPL 3.4.0          Zuse Institute Mathematical Programming Language
```

**What SCIP does:** Solves mixed-integer programming problems with branch-and-bound algorithms. In your framework, it handles discrete logic constraints and binary decisions. The conda version also includes IPOPT integration for hybrid solving capabilities.

---

## 🐍 Step 6: Set Up Python Environment

### 6.1 Create Virtual Environment
```bash
cd ~/PYTHON_OPTIMIZATION_ADAPTER
python3 -m venv .venv
source .venv/bin/activate

# Note: Make sure conda is in your PATH for this session
export PATH="$HOME/miniconda3/bin:$PATH"
```

### 6.2 Upgrade pip
```bash
pip install --upgrade pip
```

### 6.3 Install Python Dependencies
```bash
pip install sympy pyomo numpy matplotlib xarray pymongo pyscipopt
```

**What these packages do:**
- **sympy**: Symbolic mathematics for equation handling
- **pyomo**: Optimization modeling language (connects to IPOPT/SCIP)
- **numpy**: Numerical computations
- **matplotlib**: Plotting and visualization  
- **xarray**: Multi-dimensional data handling
- **pymongo**: MongoDB integration (optional)
- **pyscipopt**: Python interface to SCIP

### 6.4 Install the Project in Development Mode
```bash
pip install -e .
```

---

## 🧪 Step 7: Test the Installation

### 7.1 Test Solver Availability
Create a test script to verify both solvers work:

```bash
# Create test file
cat > test_solvers.py << 'EOF'
from pyomo.environ import SolverFactory
import pyomo.environ as pyo

# Test IPOPT
try:
    ipopt_solver = SolverFactory('ipopt')
    if ipopt_solver.available():
        print("✅ IPOPT is available and ready!")
    else:
        print("❌ IPOPT is not available")
except Exception as e:
    print(f"❌ IPOPT error: {e}")

# Test SCIP  
try:
    scip_solver = SolverFactory('scip')
    if scip_solver.available():
        print("✅ SCIP is available and ready!")
    else:
        print("❌ SCIP is not available")
except Exception as e:
    print(f"❌ SCIP error: {e}")

print("\n🎯 If both solvers show as available, you're ready to run the optimization framework!")
EOF

# Run the test
python test_solvers.py
```

**Expected output:**
```
✅ IPOPT is available and ready!
✅ SCIP is available and ready!

🎯 If both solvers show as available, you're ready to run the optimization framework!
```

---

## 🎮 Step 8: Running Your First Optimization

### 8.1 Basic Usage
```bash
# Make sure you're in the project directory and virtual environment is active
cd ~/PYTHON_OPTIMIZATION_ADAPTER
source .venv/bin/activate

# Run the main simulation
python -m msef.main
```

### 8.2 Understanding the Configuration
The simulation behavior is controlled by `msef/user_data/object_data.json`:

```json
{
  "solve_mode": "timewise",     // "monolithic" or "timewise"
  "minlp_enabled": true,        // Enable discrete variables
  "solver": "scip",             // "ipopt" or "scip"
  "dt_value": 0.5,              // Time step
  "final_time": 60,             // Simulation duration
  "live_plotting": true         // Real-time plotting
}
```

---

## 📖 Understanding the Framework Architecture

### Why IPOPT + SCIP + Pyomo?

#### 🎯 **Pyomo**: The Mathematical Modeling Language
- **Purpose**: Translates your symbolic equations into numerical optimization problems
- **Without Pyomo**: You'd need to manually compute derivatives, handle constraints, and write solver-specific code in C++
- **With Pyomo**: Write equations naturally and let it handle the complexity

#### 🔄 **IPOPT**: Continuous Optimization Engine  
- **Purpose**: Solves smooth nonlinear ODEs using interior-point methods
- **Best for**: Continuous dynamics, smooth functions, large-scale problems
- **In your system**: Handles the differential equation solving

#### 🎲 **SCIP**: Discrete Optimization Engine
- **Purpose**: Solves mixed-integer problems using branch-and-bound
- **Best for**: Discrete variables, logical constraints, combinatorial problems  
- **In your system**: Handles IF-THEN-ELSE logic and discrete decisions

### The Hybrid Approach
Your framework is **revolutionary** because it combines:
1. **Continuous dynamics** (ODEs) → IPOPT
2. **Discrete logic** (switching behavior) → SCIP  
3. **Real-time updates** (parameter hot-reloading) → Your innovation!
4. **Live visualization** (real-time plotting) → Your innovation!

---

## 🔧 Configuration Guide

### Problem Definition Files

#### Main Configuration: `msef/user_data/object_data.json`
```json
{
  "unknown_parameters": ["x", "v"],           // State variables
  "parameters": {"m": 500, "F": 0},          // System parameters  
  "equations": [                             // ODE system
    "diff(x(t), t) - v(t) = 0",
    "m*diff(v(t), t) + DAMPING(x(t))*v(t) + k_eff*x(t) - F = 0"
  ],
  "init_conditions": {"x0": 2.0, "v0": 0.0}, // Initial conditions
  "discrete_parameters": [                    // MINLP variables
    {
      "name": "k_eff",
      "domain": "reals", 
      "bounds": [0, 1e6]
    }
  ],
  "logic_parameters": {                       // Logic constraint parameters
    "k_low": 10,
    "k_high": 1000, 
    "threshold": 0.1
  }
}
```

#### Discrete Logic: `msef/user_data/discrete_logic.json`
```json
{
  "logic_constraints": [
    {
      "name": "spring_logic",
      "disjunction": [
        {
          "conditions": ["x <= threshold"],
          "assignments": ["k_eff == k_high"]
        },
        {
          "conditions": ["x >= threshold"], 
          "assignments": ["k_eff == k_low"]
        }
      ]
    }
  ]
}
```

### Solving Modes

#### 1. **Monolithic Mode** (`"solve_mode": "monolithic"`)
- Builds and solves the **entire time horizon** at once
- **Pros**: Global optimization, finds optimal solution
- **Cons**: Memory intensive, slower for large problems
- **Use when**: Small to medium problems, need global optimum

#### 2. **Timewise Mode** (`"solve_mode": "timewise"`)  
- Solves **step-by-step** through time
- **Pros**: Real-time capable, handles large problems, parameter updates
- **Cons**: No global optimization, greedy approach
- **Use when**: Large problems, need real-time simulation, parameter changes

---

## 🎨 Example Problems Included

The framework includes several example problems in `msef/user_data/problems/`:

### Problem 0: MINLP Spring-Damper System
- **Features**: Discrete switching logic, piecewise stiffness
- **Solvers**: IPOPT + SCIP  
- **Mode**: Timewise with real-time plotting

### Problem 1: Linear Second-Order ODE
- **Features**: Simple harmonic oscillator
- **Solvers**: IPOPT only
- **Mode**: Monolithic (fast solution)

### Problem 2: Modified Damped Oscillator  
- **Features**: Nonlinear damping
- **Solvers**: IPOPT only
- **Mode**: Monolithic

### Problem 3: Mixed Algebraic-Differential System
- **Features**: Coupled algebraic and differential equations
- **Solvers**: IPOPT only
- **Mode**: Timewise

---

## 🛠️ Advanced Features

### Real-Time Parameter Updates
The framework can update parameters during simulation:
```python
# The system automatically reloads parameters from JSON at each time step
# Simply modify object_data.json while the simulation is running!
```

### Live Plotting  
Enable real-time visualization:
```json
{
  "live_plotting": true,
  "solve_mode": "timewise"
}
```

### Custom Lookup Tables
Define piecewise functions in `msef/user_data/lookup.py`:
```python
import numpy as np
import xarray as xr

# Example: nonlinear damping function
damping_lookup = xr.DataArray(
    1 + 0.1 * np.linspace(-2, 2, 100)**2,
    coords={"x": np.linspace(-2, 2, 100)},
    dims=["x"]
)

lookup_tables = {
    "DAMPING": ("x", damping_lookup)
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **Solver Not Found**
```
Error: Could not locate the 'ipopt' executable
```
**Solution**: Ensure solvers are in PATH and properly installed:
```bash
# For system-installed IPOPT
pkg-config --modversion ipopt

# For conda-installed SCIP, make sure conda is in PATH
export PATH="$HOME/miniconda3/bin:$PATH"
which scip
scip --version
```

#### 2. **Virtual Environment Issues**
```
ModuleNotFoundError: No module named 'pyomo'
```
**Solution**: Activate the virtual environment:
```bash
cd ~/PYTHON_OPTIMIZATION_ADAPTER
source .venv/bin/activate
```

#### 3. **Conda Issues**
**Solution**: Ensure conda is properly configured:
```bash
# Add conda to PATH permanently
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# If Terms of Service issues occur
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

#### 4. **Permission Errors**
**Solution**: Ensure you have proper permissions:
```bash
sudo chown -R $USER:$USER ~/PYTHON_OPTIMIZATION_ADAPTER
```

### WSL-Specific Issues

#### 1. **X11 Forwarding for Plotting**
If plots don't display, install X11 support:
```bash
sudo apt install xvfb
export DISPLAY=:0
```

#### 2. **Memory Issues** 
For large problems, increase WSL memory:
```powershell
# In PowerShell (Windows side)
wsl --shutdown
# Edit ~/.wslconfig and add:
# [wsl2]
# memory=8GB
```

---

## � Important Notes for Your Installation

### Conda Environment Persistence
After installation, you need to activate conda in each new terminal session:
```bash
# Add this to your ~/.bashrc to make it permanent
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Solver Versions Installed
Your installation provides:
- **IPOPT 3.11.9** (system installation via apt)
- **IPOPT 3.14.1** (conda installation, newer version)
- **SCIP 7.0.3** (conda installation with IPOPT integration)
- **SoPlex 5.0.2** (included with SCIP as backup linear solver)

## �📊 Performance Tips

### For Large Problems
1. **Use timewise mode** for problems with > 1000 time steps
2. **Reduce time resolution** (`dt_value`) if possible  
3. **Disable live plotting** for faster solving
4. **Use sparse matrix formats** (automatic in Pyomo)

### For Real-Time Applications  
1. **Enable parameter hot-reloading**
2. **Use smaller time steps** for smoother updates
3. **Optimize lookup table resolution**
4. **Consider parallel processing** for multiple scenarios

---

## 🤝 Contributing

### Development Setup
```bash
# Fork the repository and clone your fork
git clone https://github.com/YOURUSERNAME/PYTHON_OPTIMIZATION_ADAPTER.git
cd PYTHON_OPTIMIZATION_ADAPTER

# Create development branch
git checkout -b feature/your-feature-name

# Install in development mode
pip install -e .[dev]

# Run tests (if available)
python -m pytest tests/
```

### Code Structure
```
msef/
├── __init__.py              # Package initialization
├── main.py                  # Main execution controller  
├── parameters.py            # Configuration management
├── build_global_model.py    # Monolithic model builder
├── build_sequential_model.py # Timewise simulator
├── solver.py                # Solver interface
├── equations.py             # Symbolic equation loader
├── discretization.py        # Numerical discretization
├── constraint_rules.py      # Constraint generation
├── discrete_logic.py        # GDP implementation
├── extra_variables.py       # MINLP variable handler
├── postprocessing.py        # Data packaging
├── postprocessing_live.py   # Real-time data handling
├── plotting/                # Visualization modules
│   ├── plotting.py          # Standard plotting
│   ├── plotting_mixed.py    # Phase-space plots  
│   └── plotting_live.py     # Real-time plotting
└── user_data/               # Configuration files
    ├── object_data.json     # Main configuration
    ├── discrete_logic.json  # Logic constraints
    ├── lookup.py            # Piecewise functions
    └── problems/            # Example problems
```

---

## 📚 Further Reading

### Optimization Theory
- **Nocedal & Wright**: "Numerical Optimization" (IPOPT theory)
- **Nemhauser & Wolsey**: "Integer Programming" (SCIP theory)  
- **Biegler**: "Nonlinear Programming" (Applications)

### Pyomo Documentation
- [Pyomo Documentation](https://pyomo.readthedocs.io/)
- [IPOPT Documentation](https://coin-or.github.io/Ipopt/)
- [SCIP Optimization Suite](https://scipopt.org/)

### Hybrid Systems
- **Lygeros et al.**: "Dynamical Systems and Control" 
- **Cassandras & Lafortune**: "Discrete Event Systems"

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

This framework builds upon the excellent work of:
- **COIN-OR Foundation** (IPOPT development)
- **Zuse Institute Berlin** (SCIP development)  
- **Sandia National Labs** (Pyomo development)
- **NumPy/SciPy community** (Scientific Python ecosystem)

---

## 📞 Support

### Getting Help
1. **Check this README** first (most issues are covered)
2. **Search existing issues** on GitHub
3. **Create a new issue** with:
   - Your system information (`uname -a`, WSL version)
   - Complete error messages
   - Steps to reproduce the problem
   - Your configuration files

### Community
- **GitHub Discussions**: For questions and feature requests
- **Issues**: For bug reports
- **Pull Requests**: For contributions

---

**🎉 Congratulations!** You now have a fully functional hybrid optimization framework that can handle some of the most complex mathematical problems in engineering and science. This system represents state-of-the-art capabilities in real-time MINLP-ODE simulation!

The combination of IPOPT + SCIP + Pyomo with real-time parameter updates and live visualization puts you at the forefront of computational optimization. Happy optimizing! 🚀
