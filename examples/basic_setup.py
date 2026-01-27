"""
Basic setup example for DeepExplore.

This example demonstrates how to:
1. Create a custom test object inheriting from DeepExploreObject
2. Define parameter resolvers for dynamic values
3. Configure and execute tests using different modes
4. Use preconditions and stopping criteria
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deep_explore import DeepExploreObject
from deep_explore import DeepExploreLoader
from examples.common import ResourceClient


class SimpleTestObject(DeepExploreObject):
    """A simple test object for demonstration.

    In real usage, this would connect to your actual system (e.g., cloud platform API).
    This example simulates a resource with states: available -> running -> stopped.
    """

    def __init__(self):
        """Initialize the test object with initial state."""
        super().__init__()
        self.data = {
            'id': 'resource-123',
            'status': 'available',
            'name': 'test-resource',
            'cpu': 2,
            'memory': 4096
        }

    def _do_update_state(self):
        """Update the object state.

        In real usage, fetch from your system API.
        This simulates state updates.
        """
        print(f"  [State Update] Current status: {self.data['status']}")

    def get_status(self) -> str:
        """Get the current status.

        Returns:
            str: Current status value.
        """
        return self.data['status']

    def resource_id(self) -> str:
        """Resolver for getting the resource ID.

        Returns:
            str: The resource ID from data.
        """
        return self.data['id']

    def resource_name(self) -> str:
        """Resolver for getting the resource name.

        Returns:
            str: The resource name from data.
        """
        return self.data['name']


def example_random_action_mode():
    """Example: Random action mode.

    Randomly executes actions until stopping criteria are met.
    """
    print("\n" + "="*60)
    print("Example 1: Random Action Mode")
    print("="*60)

    # Create the test object
    test_obj = SimpleTestObject()

    # Configuration for random action mode
    config = {
        "mode_type": "random_action",
        "stopping_criteria_list": [
            {
                "criteria_type": "step",
                "max_steps": 3
            }
        ],
        "action_list": [
            {
                "action_name": "start_resource",
                "action_public_client": ResourceClient,
                "action_args": [
                    "resource_id=_resolver_resource_id"
                ],
                "action_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["available"],
                        "compare_result": True
                    }
                ],
                "action_post_check_list": [
                    {
                        "check_info": ["examples.common.check_resource_started",
                                     "_resolver_resource_id"],
                        "check_result": True
                    }
                ]
            },
            {
                "action_name": "stop_resource",
                "action_public_client": ResourceClient,
                "action_args": [
                    "_resolver_resource_id=resource_id"
                ],
                "action_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["running"],
                        "compare_result": True
                    }
                ],
                "action_post_check_list": [
                    {
                        "check_info": ["examples.common.check_resource_stopped",
                                     "_resolver_resource_id"],
                        "check_result": True
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nRandom action mode example completed!")


def example_sequence_action_mode():
    """Example: Sequential action mode.

    Executes actions in order.
    """
    print("\n" + "="*60)
    print("Example 2: Sequential Action Mode")
    print("="*60)

    # Create the test object
    test_obj = SimpleTestObject()

    # Configuration for sequential action mode
    config = {
        "mode_type": "sequence_action",
        "stopping_criteria_list": [
            {
                "criteria_type": "step",
                "max_steps": 2
            }
        ],
        "action_list": [
            {
                "action_name": "start_resource",
                "action_public_client": ResourceClient,
                "action_args": [
                    "resource_id=_resolver_resource_id"
                ],
                "action_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["available"],
                        "compare_result": True
                    }
                ]
            },
            {
                "action_name": "stop_resource",
                "action_public_client": ResourceClient,
                "action_args": [
                    "resource_id=_resolver_resource_id"
                ],
                "action_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["running"],
                        "compare_result": True
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nSequential action mode example completed!")


def example_time_based_stopping():
    """Example: Time-based stopping criteria.

    Stops test execution after a specified duration.
    """
    print("\n" + "="*60)
    print("Example 3: Time-based Stopping Criteria")
    print("="*60)

    # Create the test object
    test_obj = SimpleTestObject()

    # Configuration with time-based stopping
    config = {
        "mode_type": "random_action",
        "stopping_criteria_list": [
            {
                "criteria_type": "time",
                "duration": 2  # Stop after 2 seconds
            }
        ],
        "action_list": [
            {
                "action_name": "restart_resource",
                "action_public_client": ResourceClient,
                "action_args": [
                    "resource_id=_resolver_resource_id"
                ],
                "action_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["available", "running", "stopped"],
                        "compare_result": True
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nTime-based stopping example completed!")


if __name__ == "__main__":
    """Run all examples."""
    print("\n" + "="*60)
    print("DeepExplore Basic Setup Examples")
    print("="*60)

    # Run examples
    example_random_action_mode()
    example_sequence_action_mode()
    example_time_based_stopping()

    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60)
