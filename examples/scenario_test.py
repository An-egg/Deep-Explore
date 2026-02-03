"""
Scenario-based testing example for DeepExplore.

This example demonstrates how to:
1. Define complex test scenarios with multiple actions
2. Use scenario-level preconditions
3. Execute scenarios in random or sequential order
4. Track scenario execution statistics
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deep_explore import DeepExploreObject
from deep_explore import DeepExploreLoader
from examples.common.mock_clients import VMClient

class VMTestObject(DeepExploreObject):
    """Virtual Machine test object for cloud platform testing.

    Simulates a VM with lifecycle states:
    available -> creating -> running -> stopping -> stopped -> deleting
    """

    def __init__(self):
        """Initialize the VM test object."""
        super().__init__()
        self.data = {
            'vm_id': 'vm-abc123',
            'status': 'available',
            'name': 'test-vm',
            'flavor': 'medium',
            'image': 'ubuntu-20.04'
        }

    def _do_update_state(self):
        """Update the VM state.

        Simulates fetching current VM state from cloud API.
        """
        print(f"  [State Update] VM {self.data['vm_id']} status: {self.data['status']}")

    def get_status(self) -> str:
        """Get the current VM status.

        Returns:
            str: Current VM status.
        """
        return self.data['status']

    def vm_id(self) -> str:
        """Resolver for getting the VM ID.

        Returns:
            str: The VM ID.
        """
        return self.data['vm_id']

    def vm_name(self) -> str:
        """Resolver for getting the VM name.

        Returns:
            str: The VM name.
        """
        return self.data['name']


def example_random_scenario_mode():
    """Example: Random scenario mode.

    Randomly selects and executes scenarios until stopping criteria are met.
    """
    print("\n" + "="*60)
    print("Example 1: Random Scenario Mode")
    print("="*60)

    # Create the test object
    test_obj = VMTestObject()

    # Configuration with multiple scenarios
    config = {
        "mode_type": "random_scenario",
        "stopping_criteria_list": [
            {
                "criteria_type": "step",
                "max_steps": 4
            }
        ],
        "scenario_list": [
            {
                "scenario_name": "Create and Start VM",
                "scenario_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["available"],
                        "compare_result": True
                    }
                ],
                "action_list": [
                    {
                        "action_name": "create_vm",
                        "action_public_client": VMClient,
                        "action_args": [
                            "vm_name=_resolver_vm_name",
                            "flavor=medium",
                            "image=ubuntu-20.04"
                        ],
                        "action_post_check_list": [
                            {
                                "check_info": ["examples.common.check_vm_created",
                                             "_resolver_vm_id"],
                                "check_result": True
                            }
                        ]
                    },
                    {
                        "action_name": "start_vm",
                        "action_public_client": VMClient,
                        "action_args": [
                            "vm_id=_resolver_vm_id"
                        ],
                        "action_precondition_list": [
                            {
                                "precondition_type": "status",
                                "precondition_data": ["creating"],
                                "compare_result": True
                            }
                        ],
                        "action_post_check_list": [
                            {
                                "check_info": ["examples.common.check_vm_running",
                                             "_resolver_vm_id"],
                                "check_result": True
                            }
                        ]
                    }
                ]
            },
            {
                "scenario_name": "Stop and Delete VM",
                "scenario_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["running"],
                        "compare_result": True
                    }
                ],
                "action_list": [
                    {
                        "action_name": "stop_vm",
                        "action_public_client": VMClient,
                        "action_args": [
                            "vm_id=_resolver_vm_id"
                        ],
                        "action_post_check_list": [
                            {
                                "check_info": ["examples.common.check_vm_stopped",
                                             "_resolver_vm_id"],
                                "check_result": True
                            }
                        ]
                    },
                    {
                        "action_name": "delete_vm",
                        "action_public_client": VMClient,
                        "action_args": [
                            "vm_id=_resolver_vm_id"
                        ],
                        "action_precondition_list": [
                            {
                                "precondition_type": "status",
                                "precondition_data": ["stopped"],
                                "compare_result": True
                            }
                        ]
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nRandom scenario mode example completed!")


def example_sequence_scenario_mode():
    """Example: Sequential scenario mode.

    Executes scenarios in order.
    """
    print("\n" + "="*60)
    print("Example 2: Sequential Scenario Mode")
    print("="*60)

    # Create the test object
    test_obj = VMTestObject()

    # Configuration for sequential scenario execution
    config = {
        "mode_type": "sequence_scenario",
        "stopping_criteria_list": [
            {
                "criteria_type": "step",
                "max_steps": 2
            }
        ],
        "scenario_list": [
            {
                "scenario_name": "Create VM Scenario",
                "scenario_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["available"],
                        "compare_result": True
                    }
                ],
                "action_list": [
                    {
                        "action_name": "create_vm",
                        "action_public_client": VMClient,
                        "action_args": [
                            "vm_name=_resolver_vm_name",
                            "flavor=medium",
                            "image=ubuntu-20.04"
                        ]
                    }
                ]
            },
            {
                "scenario_name": "Start VM Scenario",
                "scenario_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["creating"],
                        "compare_result": True
                    }
                ],
                "action_list": [
                    {
                        "action_name": "start_vm",
                        "action_public_client": VMClient,
                        "action_args": [
                            "vm_id=_resolver_vm_id"
                        ]
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nSequential scenario mode example completed!")


if __name__ == "__main__":
    """Run all scenario examples."""
    print("\n" + "="*60)
    print("DeepExplore Scenario Testing Examples")
    print("="*60)

    # Run examples
    example_random_scenario_mode()
    example_sequence_scenario_mode()

    print("\n" + "="*60)
    print("All scenario examples completed successfully!")
    print("="*60)
