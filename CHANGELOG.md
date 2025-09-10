# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-09

### Added
- Initial release of MSEF (Mixed-Integer Nonlinear Programming Framework)
- Monolithic and timewise simulation modes
- Support for discrete logic constraints using GDP
- Real-time parameter updates and live plotting
- JSON-based configuration system
- Piecewise linear lookup tables with xarray
- Multiple solver support (SCIP, IPOPT, etc.)
- Command line interface (`msef-run`)
- Comprehensive documentation and examples
- Spring-damper system demonstration
- Automatic model building from symbolic equations
- Time discretization using backward Euler method

### Features
- **Core Framework**: Complete MINLP optimization framework
- **Dual Modes**: Monolithic (full-horizon) and timewise (step-by-step) solving
- **Live Updates**: Real-time parameter modification during simulation
- **Visualization**: Interactive plotting with matplotlib
- **Discrete Logic**: GDP-based logical constraints
- **Configurability**: JSON-based problem definition
- **Extensibility**: Modular architecture for easy customization

### Technical Details
- Python 3.11+ support
- Built on Pyomo optimization framework
- SymPy for symbolic mathematics
- xarray for data management
- matplotlib for visualization
- Comprehensive test coverage
- Type hints throughout codebase

### Documentation
- Complete README with examples
- API documentation
- Configuration reference
- Contributing guidelines
- MIT license

[1.0.0]: https://github.com/velosovictor/PYTHON_OPTIMIZATION_ADAPTER/releases/tag/v1.0.0
