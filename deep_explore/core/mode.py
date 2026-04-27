# Copyright 2025 Leo John

import logging
import random
from abc import ABC, abstractmethod

from .hooks import DeepExploreHookManager, HookPoint

logger = logging.getLogger(__name__)


class DeepExploreMode(ABC):
    """Base class for test exploration modes.

    Provides scenario/action execution statistics.

    Attributes:
        already_exec_scenarios: List of executed scenario records.
        already_exec_actions: List of executed action records.
    """

    def __init__(self):
        """Initialize DeepExploreMode."""
        self.already_exec_scenarios: list = []
        self.already_exec_actions: list = []

    @abstractmethod
    def exec_test(self):
        """Main entry method for test execution.

        To be implemented by subclasses.
        """
        pass

    def scenario_statistics(self):
        """Record and output scenario execution statistics.

        Steps:
        1. Record all executed scenarios.
        2. Count execution frequency for each scenario.
        3. Clear execution records.
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
        1. Record all executed actions.
        2. Count execution frequency for each action.
        3. Clear execution records.
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

    Attributes:
        deep_explore_object: Test exploration target object.
        stop_criteria_list: List of stopping criteria.
        scenarios: List of executable scenarios.
        already_exec_scenarios: List of executed scenario records.
    """

    def __init__(self, deep_explore_object, stop_criteria_list, scenarios):
        """Initialize random scenario mode.

        Args:
            deep_explore_object: Test exploration target object.
            stop_criteria_list: List of stopping criteria.
            scenarios: List of executable scenarios.
        """
        super().__init__()
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.scenarios = scenarios

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
                # Invoke BEFORE_SCENARIO hook
                DeepExploreHookManager.invoke(
                    HookPoint.BEFORE_SCENARIO,
                    scenario_name=scenario_name,
                    deep_explore_object=self.deep_explore_object,
                    scenario=selected_scenario)
                # Record executed scenario
                scenario_record = {scenario_name: []}
                self.already_exec_scenarios.append(scenario_record)
                action_list = selected_scenario.exec_scenario(
                    self.deep_explore_object)
                # Update actions executed in scenario
                scenario_record[scenario_name] = action_list
                # Invoke AFTER_SCENARIO hook
                DeepExploreHookManager.invoke(
                    HookPoint.AFTER_SCENARIO,
                    scenario_name=scenario_name,
                    deep_explore_object=self.deep_explore_object,
                    scenario=selected_scenario,
                    success=True)

            except Exception as e:
                # Invoke AFTER_SCENARIO hook with failure
                DeepExploreHookManager.invoke(
                    HookPoint.AFTER_SCENARIO,
                    scenario_name=selected_scenario.scenario_name,
                    deep_explore_object=self.deep_explore_object,
                    scenario=selected_scenario,
                    success=False)
                self.scenario_statistics()
                raise Exception(f"Scenario execution failed: {e}") from e


class DeepExploreSequenceScenarioMode(DeepExploreMode):
    """Sequential scenario test mode.

    Attributes:
        deep_explore_object: Test exploration target object.
        stop_criteria_list: List of stopping criteria.
        scenarios: List of executable scenarios.
        already_exec_scenarios: List of executed scenario records.
    """

    def __init__(self, deep_explore_object, stop_criteria_list, scenarios,
                 reverse=False):
        """Initialize sequential scenario mode.

        Args:
            deep_explore_object: Test exploration target object.
            stop_criteria_list: List of stopping criteria.
            scenarios: List of executable scenarios.
            reverse: Whether to execute sequence in reverse (default False).
        """
        super().__init__()
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.scenarios = scenarios[::-1] if reverse else scenarios

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
                # Invoke BEFORE_SCENARIO hook
                DeepExploreHookManager.invoke(
                    HookPoint.BEFORE_SCENARIO,
                    scenario_name=scenario_name,
                    deep_explore_object=self.deep_explore_object,
                    scenario=current_scenario)
                # Record executed scenario
                scenario_record = {scenario_name: []}
                self.already_exec_scenarios.append(scenario_record)
                action_list = current_scenario.exec_scenario(
                    self.deep_explore_object)
                # Update actions executed in scenario
                scenario_record[scenario_name] = action_list
                # Invoke AFTER_SCENARIO hook
                DeepExploreHookManager.invoke(
                    HookPoint.AFTER_SCENARIO,
                    scenario_name=scenario_name,
                    deep_explore_object=self.deep_explore_object,
                    scenario=current_scenario,
                    success=True)

            except Exception as e:
                # Invoke AFTER_SCENARIO hook with failure
                DeepExploreHookManager.invoke(
                    HookPoint.AFTER_SCENARIO,
                    scenario_name=current_scenario.scenario_name,
                    deep_explore_object=self.deep_explore_object,
                    scenario=current_scenario,
                    success=False)
                self.scenario_statistics()
                raise Exception(f"Scenario execution failed: {e}") from e


class DeepExploreModeFactory:
    """Test exploration mode factory class.

    Supports runtime registration of custom mode types via the
    :meth:`register` class method.

    Example::

        class MyCustomMode(DeepExploreMode):
            def __init__(self, obj, criteria, tests, **kwargs):
                super().__init__()
                ...
            def exec_test(self):
                ...

        DeepExploreModeFactory.register("custom", MyCustomMode)
        mode = DeepExploreModeFactory.create_mode("custom", obj, criteria, tests)
    """

    _custom_modes: dict = {}

    @classmethod
    def register(cls, mode_type: str, mode_class: type) -> None:
        """Register a custom mode type.

        Args:
            mode_type: Unique string identifier for the mode type.
            mode_class: Mode class (must be a subclass of DeepExploreMode).

        Raises:
            TypeError: If mode_class is not a subclass of DeepExploreMode.
            ValueError: If mode_type is already registered.
        """
        if not (isinstance(mode_class, type) and issubclass(mode_class, DeepExploreMode)):
            raise TypeError(
                f"mode_class must be a subclass of DeepExploreMode, "
                f"got {mode_class}")
        if mode_type in cls._custom_modes:
            raise ValueError(
                f"Mode type '{mode_type}' is already registered. "
                f"Use a different name or unregister first.")
        cls._custom_modes[mode_type] = mode_class
        logger.info(f"Registered custom mode type: {mode_type}")

    @classmethod
    def unregister(cls, mode_type: str) -> bool:
        """Unregister a previously registered custom mode type.

        Args:
            mode_type: The mode type identifier to unregister.

        Returns:
            bool: True if the mode type was found and removed, False otherwise.
        """
        if mode_type in cls._custom_modes:
            del cls._custom_modes[mode_type]
            logger.info(f"Unregistered mode type: {mode_type}")
            return True
        return False

    @classmethod
    def create_mode(cls, mode_type, deep_explore_object, stop_criteria_list,
                    test_objects, **kwargs):
        """Create a test exploration mode instance of the specified type.

        Args:
            mode_type: Mode type ('random_scenario', 'sequence_scenario',
                or any custom registered type).
            deep_explore_object: Test exploration target object.
            stop_criteria_list: List of stopping criteria.
            test_objects: Test object collection (scenarios).
            **kwargs: Mode-specific parameters (e.g., reverse).

        Returns:
            DeepExploreMode: Created test mode instance.

        Raises:
            ValueError: When an unsupported mode type is provided.
        """
        if mode_type == "random_scenario":
            return DeepExploreRandomScenarioMode(
                deep_explore_object, stop_criteria_list, test_objects)

        elif mode_type == "sequence_scenario":
            reverse = kwargs.get('reverse', False)
            return DeepExploreSequenceScenarioMode(
                deep_explore_object, stop_criteria_list, test_objects, reverse)

        elif mode_type in cls._custom_modes:
            return cls._custom_modes[mode_type](
                deep_explore_object, stop_criteria_list, test_objects, **kwargs)

        else:
            raise ValueError(f"Unsupported mode type: {mode_type}")
