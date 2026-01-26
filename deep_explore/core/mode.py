# Copyright 2025 Leo John

import logging
import random

logger = logging.getLogger(__name__)


class DeepExploreMode:
    """Base class for test exploration modes, providing scenario/action execution statistics.

    Attributes:
        already_exec_scenarios: List of executed scenario records
        already_exec_actions: List of executed action records
    """
    already_exec_scenarios = []
    already_exec_actions = []

    def exec_test(self):
        """Main entry method for test execution (to be implemented by subclasses)."""
        pass

    def scenario_statistics(self):
        """Record and output scenario execution statistics.

        Steps:
        1. Record all executed scenarios
        2. Count execution frequency for each scenario
        3. Clear execution records
        """
        logger.info("Already exec scenario total count: "
                    f"{len(self.already_exec_scenarios)}")
        logger.info("Already exec scenario order records: "
                    f"{self.already_exec_scenarios}")

        # Count execution times for each scenario
        scenario_counter = {}
        for scenario_record in self.already_exec_scenarios:
            for scenario_name in scenario_record.keys():
                scenario_counter[scenario_name] = scenario_counter.get(
                    scenario_name, 0) + 1

        logger.info(f"Already exec scenario statistics: {scenario_counter}")
        self.already_exec_scenarios = []  # Clear records

    def action_statistics(self):
        """Record and output action execution statistics.

        Steps:
        1. Record all executed actions
        2. Count execution frequency for each action
        3. Clear execution records
        """
        logger.info("Already exec action total count: "
                    f"{len(self.already_exec_actions)}")
        logger.info("Already exec action order records: "
                    f"{self.already_exec_actions}")

        # Count execution times for each action
        action_counter = {}
        for action_name in self.already_exec_actions:
            action_counter[action_name] = action_counter.get(
                action_name, 0) + 1

        logger.info(f"Already exec action statistics: {action_counter}")
        self.already_exec_actions = []  # Clear records


class DeepExploreRandomScenarioMode(DeepExploreMode):
    """Random scenario test mode.

    Args:
        deep_explore_object: Test exploration target object
        stop_criteria_list: List of stopping criteria
        scenarios: List of executable scenarios
    """

    def __init__(self, deep_explore_object, stop_criteria_list, scenarios):
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.scenarios = scenarios
        self.already_exec_scenarios = []  # Override parent class variable as instance variable

    def exec_test(self):
        """Randomly execute scenarios until stopping criteria are met."""
        while True:
            # Check stopping criteria
            for criteria in self.stop_criteria_list:
                if criteria.is_matched():
                    logger.info(
                        "Stopping criteria satisfied: "
                        f"{criteria.__class__.__name__}. Exiting test.")
                    self.scenario_statistics()
                    return

            # Filter scenarios that meet preconditions
            available_scenarios = [
                s for s in self.scenarios
                if s.check_preconditions(self.deep_explore_object)
            ]

            if not available_scenarios:
                logger.info("No available scenarios. Exiting test.")
                self.scenario_statistics()
                return

            # Randomly select and execute scenario
            selected_scenario = random.choice(available_scenarios)
            try:
                scenario_name = selected_scenario.scenario_name
                # Record executed scenario
                scenario_record = {scenario_name: []}
                self.already_exec_scenarios.append(scenario_record)
                action_list = selected_scenario.exec_scenario(
                    self.deep_explore_object)
                # Update actions executed in scenario
                scenario_record[scenario_name] = action_list

            except Exception as e:
                self.scenario_statistics()
                raise Exception(f"Scenario execution failed: {e}")


class DeepExploreRandomActionMode(DeepExploreMode):
    """Random action test mode.

    Args:
        deep_explore_object: Test exploration target object
        stop_criteria_list: List of stopping criteria
        actions: List of executable actions
    """

    def __init__(self, deep_explore_object, stop_criteria_list, actions):
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.actions = actions
        self.already_exec_actions = []  # Override parent class variable as instance variable

    def exec_test(self):
        """Randomly execute actions until stopping criteria are met."""
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

            # Randomly select and execute action
            selected_action = random.choice(available_actions)
            try:
                action_name = selected_action.action_executor.action_name
                # Record executed action
                self.already_exec_actions.append(action_name)
                selected_action.exec_action(self.deep_explore_object)

            except Exception as e:
                self.action_statistics()
                raise Exception(f"Action execution failed: {e}")


class DeepExploreSequenceScenarioMode(DeepExploreMode):
    """Sequential scenario test mode.

    Args:
        deep_explore_object: Test exploration target object
        stop_criteria_list: List of stopping criteria
        scenarios: List of executable scenarios
        reverse: Whether to execute sequence in reverse (default False)
    """

    def __init__(self, deep_explore_object, stop_criteria_list, scenarios,
                 reverse=False):
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.scenarios = scenarios[::-1] if reverse else scenarios
        self.already_exec_scenarios = []  # Override parent class variable as instance variable

    def exec_test(self):
        """Execute scenarios in order until stopping criteria are met."""
        index = 0
        while True:
            # Check stopping criteria
            for criteria in self.stop_criteria_list:
                if criteria.is_matched():
                    logger.info(
                        "Stopping criteria satisfied: "
                        f"{criteria.__class__.__name__}. Exiting test.")
                    self.scenario_statistics()
                    return

            # Check if all scenarios are completed
            if index >= len(self.scenarios):
                logger.info("All scenarios executed. Exiting test.")
                self.scenario_statistics()
                return

            # Execute current scenario
            current_scenario = self.scenarios[index]
            index += 1
            try:
                scenario_name = current_scenario.scenario_name
                # Record executed scenario
                scenario_record = {scenario_name: []}
                self.already_exec_scenarios.append(scenario_record)
                action_list = current_scenario.exec_scenario(
                    self.deep_explore_object)
                # Update actions executed in scenario
                scenario_record[scenario_name] = action_list

            except Exception as e:
                self.scenario_statistics()
                raise Exception(f"Scenario execution failed: {e}")


class DeepExploreSequenceActionMode(DeepExploreMode):
    """Sequential action test mode.

    Args:
        deep_explore_object: Test exploration target object
        stop_criteria_list: List of stopping criteria
        actions: List of executable actions
        reverse: Whether to execute actions in reverse order
    """

    def __init__(self, deep_explore_object, stop_criteria_list, actions,
                 reverse=False):
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.actions = actions[::-1] if reverse else actions
        self.already_exec_actions = []  # Override parent class variable as instance variable

    def exec_test(self):
        """Execute actions in order until stopping criteria are met or all actions are completed."""
        index = 0
        while True:
            # Check stopping criteria
            for criteria in self.stop_criteria_list:
                if criteria.is_matched():
                    logger.info(
                        "Stopping criteria satisfied: "
                        f"{criteria.__class__.__name__}. Exiting test.")
                    self.action_statistics()
                    return

            # Check if all actions are completed
            if index >= len(self.actions):
                logger.info("All scenarios executed. Exiting test.")
                self.action_statistics()
                return

            # Execute current action
            current_action = self.actions[index]
            index += 1
            try:
                action_name = current_action.action_executor.action_name
                # Record executed action
                self.already_exec_actions.append(action_name)
                current_action.exec_action(self.deep_explore_object)

            except Exception as e:
                self.action_statistics()
                raise Exception(f"Action execution failed: {e}")


class DeepExploreModeFactory:
    """Test exploration mode factory class."""

    @staticmethod
    def create_mode(mode_type, deep_explore_object, stop_criteria_list,
                    test_objects, **kwargs):
        """Create a test exploration mode instance of the specified type.

        Args:
            mode_type: Mode type ('random_scenario', 'sequence_scenario',
                               'random_action')
            deep_explore_object: Test exploration target object
            stop_criteria_list: List of stopping criteria
            test_objects: Test object collection (scenarios or actions)
            **kwargs: Mode-specific parameters (e.g., reverse)

        Returns:
            DeepExploreMode: Created test mode instance

        Raises:
            ValueError: When an unsupported mode type is provided
        """
        if mode_type == "random_scenario":
            return DeepExploreRandomScenarioMode(
                deep_explore_object, stop_criteria_list, test_objects)

        elif mode_type == "sequence_scenario":
            reverse = kwargs.get('reverse', False)
            return DeepExploreSequenceScenarioMode(
                deep_explore_object, stop_criteria_list, test_objects, reverse)

        elif mode_type == "random_action":
            return DeepExploreRandomActionMode(
                deep_explore_object, stop_criteria_list, test_objects)

        elif mode_type == "sequence_action":
            reverse = kwargs.get('reverse', False)
            return DeepExploreSequenceActionMode(
                deep_explore_object, stop_criteria_list, test_objects, reverse)
        else:
            raise ValueError(f"Unsupported mode type: {mode_type}")
