# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-01-24

### Added

- Initial release of DeepExplore framework
- **Core Architecture**
  - Finite State Machine (FSM) support via `DeepExploreObject`
  - Model-Based Testing (MBT) with multiple execution strategies
  - Factory patterns for `DeepExploreMode`, `DeepExplorePrecondition`, and `DeepExploreStoppingCriteria`

- **Test Modes**
  - `DeepExploreRandomScenarioMode`: Random scenario execution
  - `DeepExploreSequenceScenarioMode`: Ordered scenario execution (with reverse option)
  - `DeepExploreRandomActionMode`: Random action execution
  - `DeepExploreSequenceActionMode`: Ordered action execution (with reverse option)

- **Stopping Criteria**
  - `DeepExploreStepStoppingCriteria`: Stop after N steps
  - `DeepExploreTimeStoppingCriteria`: Stop after T seconds
  - `DeepExploreEndTimeStoppingCriteria`: Stop at specific timestamp

- **Preconditions**
  - `DeepExploreStatusPrecondition`: Status matching
  - `DeepExploreMatchDataPrecondition`: Data structure matching
  - `DeepExploreFunctionPrecondition`: Custom function checks

- **Action Management**
  - `DeepExploreAction`: Complete lifecycle management (pre-checks, execution, post-checks)
  - `DeepExploreActionExecutor`: Action execution with dynamic parameter resolution
  - `DeepExploreActionCheck`: Dynamic check loading and execution

- **Scenario Support**
  - `DeepExploreScenario`: Combine multiple actions into test scenarios
  - Precondition validation for scenarios

- **Utilities**
  - `DeepExploreUtil`: Parameter resolution with placeholder support
  - `DeepExploreLoader`: Configuration-driven test loading
  - `DeepExplorePublicManager`: Dynamic client instantiation

- **Type Annotations**
  - Full type hints support for Python 3.8+
  - Conditional imports to avoid circular dependencies

### Documentation

- Comprehensive architecture documentation
- API docstrings for all public classes and methods
- Configuration examples for all supported modes

### Packaging

- `pyproject.toml` with modern Python packaging
- Support for Python 3.8, 3.9, 3.10, 3.11, 3.12
- Optional dependencies for YAML support and development

[Unreleased]: https://github.com/leojohn/deep-explore/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/leojohn/deep-explore/releases/tag/v1.0.0
