"""
Basic setup example for DeepExplore.

This example demonstrates how to:
1. Create a custom test object
2. Define parameter resolvers
3. Load and execute tests
"""

from deep_explore import DeepExploreObject
from deep_explore.utils.loader import DeepExploreLoader


class SimpleTestObject(DeepExploreObject):
    """
    A simple test object for demonstration.
    In real usage, this would connect to your actual system.
    """

    def __init__(self):
        super().__init__()
        self.data = {
            'id': 'test-123',
            'status': 'available',
            'name': 'test-resource'
        }

    def _do_update_state(self):
        """
        Update the object state.
        In real usage, fetch from your system API.
        """
        print(f"Updating state... Current: {self.data['status']}")

    def get_status(self) -> str:
        """
        Get the current status.

        Returns:
            str: Current status value
        """
        return self.data['status']

    def _resolver_resource_id(self) -> str:
        """
        Resolver for getting the resource ID.

        Returns:
            str: The resource ID from data
        """
        return self.data['id']

    def _resolver_resource_name(self) -> str:
        """
        Resolver for getting the resource name.

        Returns:
            str: The resource name from data
        """
        return self.data['name']


# Mock client for demonstration purposes
class ActionClient:
    """Mock client for action execution"""

    @staticmethod
    def start_resource(resource_id: str):
        print(f"Starting resource: {resource_id}")
        return None


if __name__ == "__main__":
    # Create the test object
    test_obj = SimpleTestObject()

    # Example configuration (could be loaded from YAML)
    config = {
        "mode_type": "random_action",
        "stopping_criteria_list": [
            {
                "criteria_type": "step",
                "max_steps": 5
            }
        ],
        "action_list": [
            {
                "action_name": "start_resource",
                "action_public_client": ActionClient,
                "action_args": [
                    "resource_id=test-123"
                ],
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

    print("Basic setup example completed!")

