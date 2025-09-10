# MSEF - Mixed-Integer Nonlinear Programming Framework

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/msef-optimization-framework.svg)](https://badge.fury.io/py/msef-optimization-framework)

**MSEF** (Multi-Scale Energy Framework) is a powerful Python library for solving **Mixed-Integer Nonlinear Programming (MINLP)** problems using **Pyomo** and **Generalized Disjunctive Programming (GDP)**. It provides both monolithic and time-wise simulation approaches with real-time parameter updates and live plotting capabilities.

## 🚀 Key Features

- **🎯 MINLP Optimization**: Solve complex mixed-integer nonlinear programming problems
- **⚡ Dual Solution Modes**: Monolithic (full-horizon) and timewise (step-by-step) simulation
- **🔄 Real-time Updates**: Dynamic parameter modification during simulation
- **📊 Live Plotting**: Interactive visualization with matplotlib
- **🧩 Discrete Logic**: Support for logical constraints using Generalized Disjunctive Programming
- **📈 Lookup Tables**: Piecewise linear approximations with xarray DataArrays
- **🔧 Multiple Solvers**: Compatible with SCIP, IPOPT, and other Pyomo-supported solvers
- **📦 Easy Configuration**: JSON-based problem definition

## 📦 Installation

### From PyPI (when published)
```bash
pip install msef-optimization-framework
```

### From Source
```bash
git clone https://github.com/velosovictor/PYTHON_OPTIMIZATION_ADAPTER.git
cd PYTHON_OPTIMIZATION_ADAPTER
pip install -e .
```

### Prerequisites
- **Python 3.11+**
- **SCIP Solver** (recommended): Download from [SCIPOptSuite](https://www.scipopt.org/index.php#download)
- Or other Pyomo-compatible solvers (IPOPT, GLPK, etc.)

## 🎯 Quick Start

### 1. Basic Usage
```python
from msef import run

# Run with default configuration
run()
```

### 2. Command Line Interface
```bash
# Run the simulation
msef-run
```

### 3. Custom Configuration
Create your problem configuration in `msef/user_data/object_data.json`:

```json
{
  "unknown_parameters": ["x", "v"],
  "init_conditions": {
    "x0": 2.0,
    "v0": 0.0
  },
  "parameters": { 
    "m": 500,
    "F": 0
  },
  "equations": [
    "diff(x(t), t) - v(t) = 0",
    "m*diff(v(t), t) + DAMPING(x(t))*v(t) + k_eff*x(t) - F = 0"
  ],
  "dt_value": 0.5,
  "final_time": 10,
  "minlp_enabled": true,
  "solver": "scip",
  "solve_mode": "monolithic"
}
```

## 🏗️ Architecture

### Core Components

1. **🧮 Equation Handler** (`equations.py`): Loads symbolic equations from JSON
2. **🔨 Model Builder** (`build_global_model.py`): Constructs Pyomo optimization models
3. **⚙️ Discretization** (`discretization.py`): Converts ODEs to algebraic constraints
4. **🧠 Solver Interface** (`solver.py`): Manages optimization solver execution  
5. **📊 Visualization** (`plotting/`): Real-time and post-processing plots
6. **🔧 Parameter Management** (`parameters.py`): JSON configuration handling
7. **🧩 Discrete Logic** (`discrete_logic.py`): GDP constraint implementation

### Solution Modes

#### Monolithic Approach
- Builds the entire time horizon at once
- Optimal for problems with strong temporal coupling
- Uses global optimization strategies

#### Timewise Approach  
- Step-by-step simulation with live updates
- Enables real-time parameter modification
- Ideal for dynamic systems and live monitoring

## 📚 Examples

### Spring-Damper System with Discrete Logic
```python
import msef

# The framework automatically handles:
# - Nonlinear damping lookup tables
# - Discrete spring stiffness switching
# - Mixed-integer constraints
# - Real-time visualization

msef.run()
```

### Custom Problem Definition
```python
from msef.build_global_model import build_global_model
from msef.solver import solve_model, extract_solution
from msef.postprocessing import package_solution

# Build custom model
model, tau = build_global_model()

# Solve optimization problem
solve_model(model)

# Extract and package results
sol_dict = extract_solution(model, model.T)
dataset = package_solution(tau, sol_dict, dt=0.1, final_time=10)
```

## 🔧 Configuration Reference

### Problem Definition (`object_data.json`)

| Parameter | Description | Type | Example |
|-----------|-------------|------|---------|
| `unknown_parameters` | State variables to solve for | Array | `["x", "v"]` |
| `parameters` | System parameters | Object | `{"m": 500, "k": 1000}` |
| `equations` | Differential equations | Array | `["diff(x(t), t) - v(t) = 0"]` |
| `init_conditions` | Initial values | Object | `{"x0": 2.0, "v0": 0.0}` |
| `dt_value` | Time step size | Number | `0.1` |
| `final_time` | Simulation duration | Number | `10.0` |
| `solver` | Optimization solver | String | `"scip"`, `"ipopt"` |
| `solve_mode` | Solution approach | String | `"monolithic"`, `"timewise"` |
| `minlp_enabled` | Enable discrete variables | Boolean | `true` |

### Discrete Logic (`discrete_logic.json`)
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

## 🛠️ Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/velosovictor/PYTHON_OPTIMIZATION_ADAPTER.git
cd PYTHON_OPTIMIZATION_ADAPTER

# Create virtual environment
uv venv
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black msef/
isort msef/
```

### Project Structure
```
msef/
├── __init__.py              # Package initialization
├── main.py                  # Main execution entry point
├── parameters.py            # Configuration management
├── equations.py             # Symbolic equation handling
├── build_global_model.py    # Monolithic model construction
├── build_sequential_model.py # Timewise simulation
├── discretization.py        # ODE discretization
├── constraint_rules.py      # Pyomo constraint generation
├── discrete_logic.py        # GDP logic constraints
├── solver.py               # Optimization solver interface
├── postprocessing.py       # Result packaging
├── plotting/               # Visualization modules
└── user_data/             # Configuration files
    ├── object_data.json   # Problem definition
    ├── discrete_logic.json # Logic constraints
    └── lookup.py         # Lookup tables
```

## 📈 Performance

- **⚡ Fast Setup**: Automatic model generation from JSON
- **🔥 Efficient Solving**: Leverages state-of-the-art MINLP solvers
- **📊 Real-time Capable**: Live parameter updates and visualization
- **🎯 Scalable**: Handles problems from small prototypes to large systems

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Pyomo** team for the excellent optimization modeling framework
- **SCIP** developers for the powerful MINLP solver
- **SymPy** community for symbolic mathematics capabilities

## 📞 Support

- 📖 [Documentation](https://github.com/velosovictor/PYTHON_OPTIMIZATION_ADAPTER#readme)
- 🐛 [Issue Tracker](https://github.com/velosovictor/PYTHON_OPTIMIZATION_ADAPTER/issues)
- 💬 [Discussions](https://github.com/velosovictor/PYTHON_OPTIMIZATION_ADAPTER/discussions)

---

**Made with ❤️ for the optimization community**
