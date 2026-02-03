"""
Advanced usage example for DeepExplore.

This example demonstrates advanced features:
1. Data matching preconditions
2. Multiple stopping criteria
3. Complex action configurations
4. Error handling and retries
5. Update position control
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deep_explore import DeepExploreObject
from deep_explore import DeepExploreLoader
from examples.common.mock_clients import DatabaseClient

class AdvancedTestObject(DeepExploreObject):
    """Advanced test object for demonstrating complex features.

    Simulates a database instance with detailed state information.
    """

    def __init__(self):
        """Initialize the advanced test object."""
        super().__init__()
        self.data = {
            'db_id': 'db-001',
            'status': 'available',
            'name': 'test-db',
            'engine': 'mysql',
            'version': '8.0',
            'size': 100,
            'region': 'us-east-1',
            'replicas': 1
        }

    def _do_update_state(self):
        """Update the database state.

        Simulates fetching current database state from cloud API.
        """
        print(f"  [State Update] DB {self.data['db_id']} status: "
              f"{self.data['status']}")
        print(f"  [State Update] DB details: {self.data}")

    def get_status(self) -> str:
        """Get the current database status.

        Returns:
            str: Current database status.
        """
        return self.data['status']

    def db_id(self) -> str:
        """Resolver for getting the database ID.

        Returns:
            str: The database ID.
        """
        return self.data['db_id']

    def db_name(self) -> str:
        """Resolver for getting the database name.

        Returns:
            str: The database name.
        """
        return self.data['name']


def example_data_matching_precondition():
    """Example: Data matching preconditions.

    Demonstrates using data structure matching for preconditions.
    """
    print("\n" + "="*60)
    print("Example 1: Data Matching Precondition")
    print("="*60)

    # Create the test object
    test_obj = AdvancedTestObject()

    # Configuration with data matching precondition
    config = {
        "mode_type": "random_action",
        "stopping_criteria_list": [
            {
                "criteria_type": "step",
                "max_steps": 2
            }
        ],
        "action_list": [
            {
                "action_name": "scale_database",
                "action_public_client": DatabaseClient,
                "action_args": [
                    "db_id=_resolver_db_id",
                    "new_size=200"
                ],
                "action_precondition_list": [
                    {
                        "precondition_type": "data",
                        "precondition_data": {
                            "engine": "mysql",
                            "version": "8.0"
                        },
                        "compare_result": True
                    }
                ],
                "action_post_check_list": [
                    {
                        "check_info": ["examples.common.check_database_scaled",
                                     "_resolver_db_id", 200],
                        "check_result": True
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nData matching precondition example completed!")


def example_multiple_stopping_criteria():
    """Example: Multiple stopping criteria.

    Demonstrates using multiple stopping criteria together.
    """
    print("\n" + "="*60)
    print("Example 2: Multiple Stopping Criteria")
    print("="*60)

    # Create the test object
    test_obj = AdvancedTestObject()

    # Configuration with multiple stopping criteria
    config = {
        "mode_type": "random_action",
        "stopping_criteria_list": [
            {
                "criteria_type": "step",
                "max_steps": 5
            },
            {
                "criteria_type": "time",
                "duration": 3
            }
        ],
        "action_list": [
            {
                "action_name": "add_replica",
                "action_public_client": DatabaseClient,
                "action_args": [
                    "db_id=_resolver_db_id"
                ],
                "action_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["available", "running"],
                        "compare_result": True
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nMultiple stopping criteria example completed!")


def example_update_positions():
    """Example: Controlling update positions.

    Demonstrates when to update object state during action execution.
    """
    print("\n" + "="*60)
    print("Example 3: Update Position Control")
    print("="*60)

    # Create the test object
    test_obj = AdvancedTestObject()

    # Configuration with custom update positions
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
                "action_name": "create_database",
                "action_public_client": DatabaseClient,
                "action_args": [
                    "db_name=_resolver_db_name",
                    "engine=mysql",
                    "version=8.0",
                    "size=100"
                ],
                "update_positions": ["start", "end"],
                "action_post_check_list": [
                    {
                        "check_info": ["examples.common.check_database_created",
                                     "_resolver_db_id"],
                        "check_result": True
                    }
                ]
            },
            {
                "action_name": "add_replica",
                "action_public_client": DatabaseClient,
                "action_args": [
                    "db_id=_resolver_db_id"
                ],
                "update_positions": ["before_exec_action", "after_exec_action"]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nUpdate position control example completed!")


def example_error_handling():
    """Example: Error handling with expected exceptions.

    Demonstrates handling expected exceptions in actions.
    """
    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60)

    # Create the test object
    test_obj = AdvancedTestObject()

    # Configuration with error handling
    config = {
        "mode_type": "random_action",
        "stopping_criteria_list": [
            {
                "criteria_type": "step",
                "max_steps": 2
            }
        ],
        "action_list": [
            {
                "action_name": "delete_database",
                "action_public_client": DatabaseClient,
                "action_args": [
                    "db_id=_resolver_db_id"
                ],
                "except_meet_exception": True,
                "action_precondition_list": [
                    {
                        "precondition_type": "status",
                        "precondition_data": ["available"],
                        "compare_result": True
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nError handling example completed!")


if __name__ == "__main__":
    """Run all advanced usage examples."""
    print("\n" + "="*60)
    print("DeepExplore Advanced Usage Examples")
    print("="*60)

    # Run examples
    example_data_matching_precondition()
    example_multiple_stopping_criteria()
    example_update_positions()
    example_error_handling()

    print("\n" + "="*60)
    print("All advanced usage examples completed successfully!")
    print("="*60)
