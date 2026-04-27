# Copyright 2025 Leo John

import logging

from .hooks import DeepExploreHookManager, HookPoint

logger = logging.getLogger(__name__)


class DeepExploreScenario:
    """Test exploration scenario executor."""

    def __init__(self, scenario_name, preconditions, actions):
        """Initialize scenario.

        Args:
            scenario_name: Scenario name.
            preconditions: List of preconditions.
            actions: List of actions.
        """
        self.scenario_name = scenario_name
        self.actions = actions
        self.preconditions = preconditions

    def check_preconditions(self, deep_explore_object):
        """Verify all preconditions are satisfied.

        Args:
            deep_explore_object: Test exploration object to check preconditions on.

        Returns:
            bool: True if all conditions are satisfied, False if any condition fails.
        """
        for precondition in self.preconditions:
            if not precondition.check_precondition(deep_explore_object):
                return False
        return True

    def exec_scenario(self, deep_explore_object):
        """Execute all actions in the scenario.

        Args:
            deep_explore_object: Test exploration object to execute scenario on.

        Returns:
            list: List of action names executed in the scenario.
        """
        action_names = []
        logger.info(f"Executing scenario: {self.scenario_name}")

        for action in self.actions:
            action_name = action.action_executor.action_name
            # Invoke BEFORE_ACTION hook
            DeepExploreHookManager.invoke(
                HookPoint.BEFORE_ACTION,
                action_name=action_name,
                deep_explore_object=deep_explore_object,
                action=action)
            try:
                result = action.exec_action(deep_explore_object)
                action_names.append(action_name)
                # Invoke AFTER_ACTION hook
                DeepExploreHookManager.invoke(
                    HookPoint.AFTER_ACTION,
                    action_name=action_name,
                    deep_explore_object=deep_explore_object,
                    action=action,
                    result=result,
                    success=True)
            except Exception as e:
                # Invoke ON_ACTION_ERROR hook
                DeepExploreHookManager.invoke(
                    HookPoint.ON_ACTION_ERROR,
                    action_name=action_name,
                    deep_explore_object=deep_explore_object,
                    action=action,
                    error=e)
                # Invoke AFTER_ACTION hook with failure
                DeepExploreHookManager.invoke(
                    HookPoint.AFTER_ACTION,
                    action_name=action_name,
                    deep_explore_object=deep_explore_object,
                    action=action,
                    result=None,
                    success=False)
                raise

        logger.info(f"Completed scenario: {self.scenario_name} "
                    f"with {len(action_names)} actions")
        return action_names
