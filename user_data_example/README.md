# 📁 Example User Data Configuration

This folder contains example configuration files for the **Pyomo Optimizer User Interface** library.

## 📋 Files Description

### `object_data.json`
Main configuration file containing:
- **Parameters**: Problem variables and their settings
- **Simulation Settings**: Time steps, solver options, etc.
- **Logic Parameters**: Discrete constraints and GDP rules
- **Initial Conditions**: Starting values for variables

### `lookup.py`
Contains lookup tables and piecewise functions used in the optimization model.

## 🚀 How to Use

1. **Copy this folder** to your project directory
2. **Modify the files** to match your optimization problem
3. **Run the library** pointing to your data folder:

```python
from pyomo_optimizer_user_interface import run

# Use your custom configuration
result = run(data_folder="path/to/your/data/folder")
```

## 📝 Quick Start

```python
# Example usage
from pyomo_optimizer_user_interface import run

# Use the example data (copy this folder first!)
result = run(data_folder="./user_data_example")
```

## 🔧 Configuration Tips

- **Edit `object_data.json`** to define your optimization problem
- **Modify `lookup.py`** if you need custom piecewise functions
- **Keep the same file structure** for the library to work properly

## 📖 Documentation

For detailed configuration options, see the library documentation or examine the example files in this folder.

---
*Happy Optimizing! 🎯*
