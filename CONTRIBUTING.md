# Contributing to MSEF

Thank you for your interest in contributing to the MSEF (Mixed-Integer Nonlinear Programming Framework)! We welcome contributions from the community.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Add tests for your changes
6. Run the test suite to ensure everything works
7. Commit your changes with a clear commit message
8. Push your changes to your fork
9. Create a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/PYTHON_OPTIMIZATION_ADAPTER.git
cd PYTHON_OPTIMIZATION_ADAPTER

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

## Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **pytest** for testing

Run these before submitting:

```bash
black msef/
isort msef/
flake8 msef/
pytest
```

## Testing

Write tests for any new functionality. Place tests in the `tests/` directory.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=msef
```

## Documentation

- Update docstrings for any new or modified functions
- Update the README.md if you add new features
- Add examples for complex new functionality

## Pull Request Process

1. Ensure your code follows the project's coding standards
2. Update documentation as needed
3. Add tests for new functionality
4. Ensure all tests pass
5. Update the CHANGELOG.md with your changes
6. Submit your pull request with a clear description

## Questions?

Feel free to open an issue for any questions about contributing!
