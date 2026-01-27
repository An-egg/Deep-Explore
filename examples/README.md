# DeepExplore Examples

This directory contains comprehensive examples demonstrating how to use the DeepExplore framework for automated functional exploration testing.

## Overview

DeepExplore is a model-based testing framework that combines Finite State Machine (FSM) principles with flexible execution strategies. These examples show you how to:

- Create custom test objects
- Define parameter resolvers
- Configure test scenarios and actions
- Use different execution modes
- Implement preconditions and stopping criteria
- Handle errors and retries

## Directory Structure

```
examples/
├── common/                 # Shared mock clients and utilities
│   ├── __init__.py
│   └── mock_clients.py    # Reusable mock clients and check functions
├── basic_setup.py          # Beginner examples
├── scenario_test.py        # Scenario-based testing examples
├── custom_mode.py          # Custom mode examples
├── advanced_usage.py       # Advanced features examples
├── scenario_config.yaml    # YAML configuration example
└── README.md              # This file
```

## Common Mock Module

The `examples/common/` directory contains reusable mock clients and check functions that are shared across all examples:

### Available Mock Clients

- **ResourceClient**: Mock client for resource management (start, stop, restart)
- **VMClient**: Mock client for VM operations (create, start, stop, delete)
- **TaskClient**: Mock client for task management (process, retry, complete)
- **DatabaseClient**: Mock client for database operations (create, scale, add replica, delete)

### Available Check Functions

- `check_resource_started(resource_id)`
- `check_resource_stopped(resource_id)`
- `check_vm_created(vm_id)`
- `check_vm_running(vm_id)`
- `check_vm_stopped(vm_id)`
- `check_database_created(db_id)`
- `check_database_scaled(db_id, expected_size)`
- `check_high_priority(task_id)`

### Using Common Mocks

```python
from examples.common import ResourceClient, check_resource_started

# Use in your configuration
config = {
    "action_name": "start_resource",
    "action_public_client": ResourceClient,
    "action_args": ["resource_id=_resolver_resource_id"],
    "action_post_check_list": [
        {
            "check_info": ["examples.common.check_resource_started", "_resolver_resource_id"],
            "check_result": True
        }
    ]
}
```

## Example Files

### 1. basic_setup.py

**Level:** Beginner  
**Demonstrates:** Core concepts and basic usage

This example covers:
- Creating a test object inheriting from `DeepExploreObject`
- Implementing required abstract methods (`_do_update_state`, `get_status`)
- Defining parameter resolvers with `_resolver_*` methods
- Using random and sequential action modes
- Configuring preconditions and stopping criteria
- Running basic tests

**Run it:**
```bash
python examples/basic_setup.py
```

**Key concepts:**
- Test object lifecycle
- State management
- Action execution
- Precondition validation

### 2. scenario_test.py

**Level:** Intermediate  
**Demonstrates:** Scenario-based testing

This example covers:
- Creating complex test scenarios with multiple actions
- Using scenario-level preconditions
- Executing scenarios in random or sequential order
- Tracking scenario execution statistics
- Reverse scenario execution

**Run it:**
```bash
python examples/scenario_test.py
```

**Key concepts:**
- Scenario composition
- Multi-action workflows
- Scenario preconditions
- Execution statistics

### 3. custom_mode.py

**Level:** Advanced  
**Demonstrates:** Custom modes and extensions

This example covers:
- Creating custom test modes by extending `DeepExploreMode`
- Implementing custom execution logic
- Using custom stopping criteria
- Function-based preconditions
- Direct mode instantiation

**Run it:**
```bash
python examples/custom_mode.py
```

**Key concepts:**
- Custom mode implementation
- Factory pattern usage
- Extensibility
- Custom stopping criteria

### 4. advanced_usage.py

**Level:** Advanced  
**Demonstrates:** Advanced features and patterns

This example covers:
- Data matching preconditions
- Multiple stopping criteria
- Update position control
- Error handling with expected exceptions
- Complex real-world scenarios

**Run it:**
```bash
python examples/advanced_usage.py
```

**Key concepts:**
- Data structure validation
- Complex configurations
- Error handling strategies
- Performance optimization

## Common Patterns

### Creating a Test Object

```python
from deep_explore import DeepExploreObject

class MyTestObject(DeepExploreObject):
    def __init__(self):
        super().__init__()
        self.data = {'status': 'available', 'id': '123'}

    def _do_update_state(self):
        # Fetch current state from your system
        pass

    def get_status(self) -> str:
        return self.data['status']

    def id(self) -> str:
        return self.data['id']
```

### Defining Actions

```python
from examples.common import ResourceClient, check_resource_started

action_config = {
    "action_name": "start_resource",
    "action_public_client": ResourceClient,
    "action_args": ["resource_id=_resolver_id"],
    "action_precondition_list": [
        {
            "precondition_type": "status",
            "precondition_data": ["available"],
            "compare_result": True
        }
    ],
    "action_post_check_list": [
        {
            "check_info": ["examples.common.check_resource_started", "_resolver_id"],
            "check_result": True
        }
    ]
}
```

### Execution Modes

**Random Action Mode:**
```python
config = {
    "mode_type": "random_action",
    "stopping_criteria_list": [...],
    "action_list": [...]
}
```

**Sequential Scenario Mode:**
```python
config = {
    "mode_type": "sequence_scenario",
    "kwargs": {"reverse": False},
    "stopping_criteria_list": [...],
    "scenario_list": [...]
}
```

## Stopping Criteria

### Step-based
```python
{
    "criteria_type": "step",
    "max_steps": 100
}
```

### Time-based
```python
{
    "criteria_type": "time",
    "duration": 60  # seconds
}
```

### End Time-based
```python
{
    "criteria_type": "end_time",
    "end_time": "2026-01-26 16:00:00"
}
```

## Preconditions

### Status Precondition
```python
{
    "precondition_type": "status",
    "precondition_data": ["available", "running"],
    "compare_result": True
}
```

### Data Matching Precondition
```python
{
    "precondition_type": "data",
    "precondition_data": {
        "engine": "mysql",
        "version": "8.0"
    },
    "compare_result": True
}
```

### Function Precondition
```python
{
    "precondition_type": "function",
    "precondition_data": ["examples.common.check_high_priority", "_resolver_task_id"],
    "compare_result": True
}
```

## Best Practices

1. **Start Simple:** Begin with `basic_setup.py` to understand core concepts
2. **Use Common Mocks:** Leverage the `examples.common` module to avoid code duplication
3. **Use Resolvers:** Leverage `_resolver_*` methods for dynamic parameter values
4. **Validate State:** Always implement proper preconditions to ensure valid test states
5. **Handle Errors:** Use `except_meet_exception` for expected error scenarios
6. **Control Updates:** Use `update_positions` to optimize state refresh frequency
7. **Track Statistics:** Review execution statistics to understand test coverage

## Running Examples

All examples can be run directly:

```bash
# Run all examples
python examples/basic_setup.py
python examples/scenario_test.py
python examples/custom_mode.py
python examples/advanced_usage.py

# Or run individual examples
cd examples
python basic_setup.py
```

## Integration with Real Systems

To integrate with your actual system:

1. Replace mock clients with your actual API clients
2. Implement `_do_update_state()` to fetch real state
3. Use real check functions for validation
4. Configure appropriate stopping criteria for your test duration
5. Add logging and monitoring as needed

## Troubleshooting

### Common Issues

**Issue:** Actions not executing
- **Solution:** Check preconditions are satisfied for current state

**Issue:** Tests running too long
- **Solution:** Adjust stopping criteria (reduce max_steps or duration)

**Issue:** State not updating
- **Solution:** Verify `_do_update_state()` implementation and `update_times` setting

**Issue:** Resolver not found
- **Solution:** Ensure resolver method starts with `_resolver_` prefix

**Issue:** Import errors when running examples
- **Solution:** Ensure you're running from the project root directory

## Additional Resources

- [Main README](../README.md)
- [Architecture Documentation](../docs/deep_explore架构设计文档.md)
- [API Documentation](../docs/api.md)

## Contributing

To add new examples:

1. Create a new Python file in this directory
2. Follow the existing naming convention (e.g., `my_example.py`)
3. Include comprehensive docstrings
4. Use common mock clients from `examples.common` when applicable
5. Demonstrate a specific feature or use case
6. Update this README with your example

## License

These examples are part of the DeepExplore project and follow the same Apache 2.0 license.
