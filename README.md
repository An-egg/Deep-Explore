# DeepExplore

[![PyPI version](https://badge.fury.io/py/deep-explore.svg)](https://badge.fury.io/py/deep-explore)
[![Python Versions](https://img.shields.io/pypi/pyversions/deep-explore.svg)](https://pypi.org/project/deep-explore/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**DeepExplore** is an automated functional exploration testing framework that combines Finite State Machine (FSM) and Model-Based Testing (MBT) principles. It provides a flexible, configuration-driven approach for testing complex state transitions in cloud platforms and distributed systems.

## Features

- **State Machine Support**: Track instance states with automatic cache and retry mechanisms
- **Model-Based Testing**: Multiple execution strategies (random/sequential scenarios and actions)
- **Flexible Stopping Conditions**: Time-based, step-based, or custom ending criteria
- **Precondition Validation**: Status matching, data matching, and custom function-based checks
- **Scenario Composition**: Combine multiple actions into complex test scenarios
- **Configuration-Driven**: Define tests via YAML/JSON without code modification
- **Extensible Architecture**: Factory patterns for easy extension of modes, conditions, and checks

## Installation

```bash
pip install deep-explore
```

For development with YAML support:

```bash
pip install deep-explore[yaml,dev]
```

## Quick Start

### 1. Define Your Test Object

```
from deep_explore import DeepExploreObject

class MyTestObject(DeepExploreObject):
    def _do_update_state(self):
        # Fetch current state from your system
        self.data = self.client.get_instance_info()
    
    def get_status(self):
        # Return the current status
        return self.data.get('status')
    
    def instance_id(self):
        # Resolver for dynamic parameters
        return self.data['id']
```

### 2. Create a Configuration

```yaml
mode_type: random_scenario

stopping_criteria_list:
  - criteria_type: step
    max_steps: 100

scenario_list:
  - scenario_name: "Create and Delete Test"
    scenario_precondition_list:
      - precondition_type: status
        precondition_data: ["available"]
        compare_result: true
    action_list:
      - action_name: "create_resource"
        action_public_client: "my_client.ResourceClient"
        action_args:
          - name: "test-resource"
          - "_resolver_instance_id"
        action_post_check_list:
          - check_info: ["my_checks.check_created"]
            check_result: true

      - action_name: "delete_resource"
        action_public_client: "my_client.ResourceClient"
        action_args:
          - "_resolver_instance_id"
        action_precondition_list:
          - precondition_type: status
            precondition_data: ["running"]
            compare_result: true
```

### 3. Load and Execute

```
import yaml
from deep_explore import DeepExploreLoader

# Create your test object
test_obj = MyTestObject()

# Load configuration
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Create test mode
mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)

# Run the test
mode.exec_test()
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   DeepExplore Framework                  │
├─────────────────────────────────────────────────────────┤
│  DeepExploreMode (MBT Strategies)                       │
│   • RandomScenario   • SequenceScenario                 │
│   • RandomAction     • SequenceAction                   │
├─────────────────────────────────────────────────────────┤
│  DeepExploreObject (FSM State Management)               │
│   • State Tracking   • ERIS Integration                 │
│   • Parameter Resolvers                                 │
├─────────────────────────────────────────────────────────┤
│  Scenarios & Actions                                     │
│   • Preconditions    • Pre/Post Checks                  │
│   • Action Execution                                   │
├─────────────────────────────────────────────────────────┤
│  Stopping Criteria & Validation                         │
│   • Step/Time Based  • Custom Conditions                │
└─────────────────────────────────────────────────────────┘
```

For detailed architecture documentation, see [docs/deep_explore架构设计文档.md](docs/deep_explore架构设计文档.md).

## Supported Test Modes

| Mode | Description |
|------|-------------|
| `random_scenario` | Randomly select and execute scenarios |
| `sequence_scenario` | Execute scenarios in order (supports reverse) |
| `random_action` | Randomly select and execute individual actions |
| `sequence_action` | Execute actions in order (supports reverse) |

## Stopping Criteria

| Type | Description |
|------|-------------|
| `step` | Stop after N steps |
| `time` | Stop after T seconds |
| `end_time` | Stop at specific timestamp |

## Precondition Types

| Type | Description |
|------|-------------|
| `status` | Match object status against list |
| `data` | Match object data structure |
| `function` | Execute custom check function |

## Examples

See the [examples/](examples/) directory for complete usage examples:

- [Basic Setup](examples/basic_setup.py)
- [Scenario Testing](examples/scenario_test.py)
- [Custom Mode](examples/custom_mode.py)
- [Cloud VM Testing](examples/vm_testing.py)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for testing complex cloud platform state transitions
- Inspired by model-based testing and state machine design patterns

## Contact

- **GitHub**: [https://github.com/leojohn/deep-explore](https://github.com/leojohn/deep-explore)
- **Issues**: [https://github.com/leojohn/deep-explore/issues](https://github.com/leojohn/deep-explore/issues)
- **Email**: liaozynb@gmail.com