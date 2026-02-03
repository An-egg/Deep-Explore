"""
Custom mode example for DeepExplore.

This example demonstrates how to:
1. Create custom test modes by extending DeepExploreMode
2. Implement custom execution logic
3. Use custom stopping criteria
4. Integrate with the factory pattern
"""

import logging
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deep_explore import DeepExploreObject, DeepExploreMode
from deep_explore import DeepExploreLoader
from examples.common.mock_clients import TaskClient

logger = logging.getLogger(__name__)


class CustomTestObject(DeepExploreObject):
    """Custom test object for demonstrating custom modes.

    Simulates a task queue with states: pending -> processing -> completed -> failed.
    """

    def __init__(self):
        """Initialize the custom test object."""
        super().__init__()
        self.data = {
            'task_id': 'task-001',
            'status': 'pending',
            'priority': 'high',
            'attempts': 0
        }

    def _do_update_state(self):
        """Update the task state.

        Simulates fetching current task state from queue system.
        """
        print(f"  [State Update] Task {self.data['task_id']} status: {self.data['status']}")

    def get_status(self) -> str:
        """Get the current task status.

        Returns:
            str: Current task status.
        """
        return self.data['status']

    def task_id(self) -> str:
        """Resolver for getting the task ID.

        Returns:
            str: The task ID.
        """
        return self.data['task_id']


# Custom mode example
class PriorityBasedMode(DeepExploreMode):
    """Custom mode that executes actions based on priority.

    This mode demonstrates how to create custom execution logic
    by extending the DeepExploreMode base class.
    """

    def __init__(self, deep_explore_object, stop_criteria_list, actions):
        """Initialize priority-based mode.

        Args:
            deep_explore_object: Test exploration target object.
            stop_criteria_list: List of stopping criteria.
            actions: List of executable actions.
        """
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.actions = actions
        self.already_exec_actions = []

    def exec_test(self):
        """Execute actions based on priority.

        This custom implementation executes high-priority actions first.
        """
        print("\n  [Custom Mode] Executing in priority order...")

        while True:
            # Check stopping criteria
            for criteria in self.stop_criteria_list:
                if criteria.is_matched():
                    logger.info(
                        "Stopping criteria satisfied: "
                        f"{criteria.__class__.__name__}. Exiting test.")
                    self.action_statistics()
                    return

            # Filter actions that meet preconditions
            available_actions = [
                a for a in self.actions
                if a.check_preconditions(self.deep_explore_object)
            ]

            if not available_actions:
                logger.info("No available actions. Exiting test.")
                self.action_statistics()
                return

            # Custom logic: Execute high-priority actions first
            # In this example, we just execute the first available action
            selected_action = available_actions[0]
            try:
                action_name = selected_action.action_executor.action_name
                self.already_exec_actions.append(action_name)
                selected_action.exec_action(self.deep_explore_object)

            except Exception as e:
                self.action_statistics()
                raise Exception(f"Action execution failed: {e}")


def example_custom_mode():
    """Example: Using custom mode.

    Demonstrates creating and using a custom test mode.
    """
    print("\n" + "="*60)
    print("Example 1: Custom Mode")
    print("="*60)

    # Create the test object
    test_obj = CustomTestObject()

    # Create custom mode instance directly
    from deep_explore.core.action import DeepExploreAction
    from deep_explore.core.action_executor import DeepExploreActionExecutor
    from deep_explore.core.precondition import DeepExplorePreconditionFactory

    # Create actions
    executor1 = DeepExploreActionExecutor(
        action_id="action-1",
        action_name="process_task",
        action_public_client=TaskClient,
        action_args=["task_id=_resolver_task_id"]
    )

    executor2 = DeepExploreActionExecutor(
        action_id="action-2",
        action_name="complete_task",
        action_public_client=TaskClient,
        action_args=["task_id=_resolver_task_id"]
    )

    # Create preconditions
    precondition1 = DeepExplorePreconditionFactory.create(
        "status",
        ["pending"],
        compare_result=True
    )

    precondition2 = DeepExplorePreconditionFactory.create(
        "status",
        ["processing"],
        compare_result=True
    )

    # Create actions with preconditions
    action1 = DeepExploreAction(
        action_executor=executor1,
        preconditions=[precondition1],
        pre_checks=[],
        post_checks=[]
    )

    action2 = DeepExploreAction(
        action_executor=executor2,
        preconditions=[precondition2],
        pre_checks=[],
        post_checks=[]
    )

    # Create stopping criteria
    from deep_explore.core.stopping_criteria import DeepExploreStoppingCriteriaFactory
    stop_criteria = DeepExploreStoppingCriteriaFactory.create(
        "step",
        max_steps=2
    )

    # Create custom mode
    custom_mode = PriorityBasedMode(
        deep_explore_object=test_obj,
        stop_criteria_list=[stop_criteria],
        actions=[action1, action2]
    )

    # Execute custom mode
    custom_mode.exec_test()

    print("\nCustom mode example completed!")


def example_custom_precondition():
    """Example: Using custom function-based preconditions.

    Demonstrates creating custom preconditions using functions.
    """
    print("\n" + "="*60)
    print("Example 2: Custom Function Preconditions")
    print("="*60)

    # Create the test object
    test_obj = CustomTestObject()

    # Configuration with function precondition
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
                "action_name": "process_task",
                "action_public_client": TaskClient,
                "action_args": [
                    "task_id=_resolver_task_id"
                ],
                "action_precondition_list": [
                    {
                        "precondition_type": "function",
                        "precondition_data": [["examples.common.check_high_priority",
                                             "_resolver_task_id"], True],
                        "compare_result": True
                    }
                ]
            }
        ]
    }

    # Load and execute
    mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)
    mode.exec_test()

    print("\nCustom function precondition example completed!")


if __name__ == "__main__":
    """Run all custom mode examples."""
    print("\n" + "="*60)
    print("DeepExplore Custom Mode Examples")
    print("="*60)

    # Run examples
    example_custom_mode()
    example_custom_precondition()

    print("\n" + "="*60)
    print("All custom mode examples completed successfully!")
    print("="*60)
