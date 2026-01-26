# Contributing to DeepExplore

Thank you for your interest in contributing to DeepExplore! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Environment details (Python version, OS, etc.)
- Any relevant error messages or logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Use a clear and descriptive title
- Provide a detailed explanation of the feature
- Explain why this feature would be useful
- Provide examples or use cases if possible

### Pull Requests

We welcome pull requests! Here's how to get started:

#### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/deep-explore.git
   cd deep-explore
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install the package in development mode:
   ```bash
   pip install -e ".[dev,yaml]"
   ```

#### Making Changes

1. Create a new branch for your contribution:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Write tests for new functionality
4. Ensure existing tests pass:
   ```bash
   pytest
   ```
5. Format code with black:
   ```bash
   black deep_explore/
   ```
6. Run linting:
   ```bash
   flake8 deep_explore/
   ```
7. Type checking with mypy (optional):
   ```bash
   mypy deep_explore/
   ```

#### Commit Messages

Follow these guidelines for commit messages:

- Use clear, descriptive messages
- Use imperative mood ("Add feature" not "Added feature")
- Limit the first line to 72 characters or less
- Reference relevant issue numbers:

   ```
   Add support for custom stopping criteria (#42)

   - Implement DeepExploreCustomStoppingCriteria
   - Add factory method for custom criteria creation
   - Update documentation
   ```

#### Submitting

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Create a pull request from your branch to the main repository
3. Fill out the pull request template with details about your changes
4. Wait for code review and address any feedback

## Coding Standards

### Python Version

The project supports Python 3.8+. New code should be compatible with Python 3.8.

### Code Style

- Use [Black](https://github.com/psf/black) for formatting (configured in `pyproject.toml`)
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use meaningful variable and function names
- Keep functions focused and small when possible
- Add docstrings for public APIs

### Type Hints

- Use type hints for function signatures and class attributes
- Use `from typing import TYPE_CHECKING` for forward references to avoid circular imports
- Gradually improve type coverage as the codebase evolves

### Documentation

- Add docstrings to all public classes, functions, and methods
- Use Google-style docstrings:
   ```
   def example_function(param1: str, param2: int) -> bool:
       """
       Brief description of the function.

       Args:
           param1: Description of param1
           param2: Description of param2

       Returns:
           Description of return value
       """
       return True
   ```
- Update relevant documentation when making changes

### Testing

- Write tests for new functionality
- Maintain test coverage
- Use descriptive test names
- Test edge cases and error conditions

## Project Structure

```
deep-explore/
├── deep_explore/          # Main package
│   ├── core/              # Core classes (Action, Scenario, Mode, etc.)
│   ├── factories/         # Factory classes
│   └── utils/             # Utilities and loaders
├── examples/              # Usage examples
├── docs/                  # Documentation
├── tests/                 # Test files
└── README.md              # Project documentation
```

## Adding New Features

When adding new features:

1. Discuss the feature in an issue first if it's a significant change
2. Follow the existing architecture patterns
3. Use factory patterns for creating new types (modes, conditions, etc.)
4. Add tests for the new functionality
5. Update documentation (README, architecture docs)
6. Consider adding an example in the `examples/` directory

## Architecture Guidelines

- **Factory Pattern**: Use factory classes for creating new instances of extensible types
- **Inheritance**: Extend abstract base classes for new implementations
- **Decoupling**: Minimize direct dependencies between modules
- **Configuration**: New features should be configurable via YAML/JSON when appropriate

## Questions or Need Help?

If you have questions or need help contributing:

- Check existing [documentation](README.md)
- Look through existing [issues](https://github.com/leojohn/deep-explore/issues)
- Use [Discussions](https://github.com/leojohn/deep-explore/discussions) for questions
- Open a new issue with the "question" label

## License

By contributing to DeepExplore, you agree that your contributions will be licensed under the Apache License 2.0.
