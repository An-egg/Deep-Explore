# Copyright 2025 Leo John

"""Hook system for DeepExplore lifecycle events.

Provides a simple but powerful hook mechanism that allows users to inject
custom logic at key points in the test execution lifecycle without
subclassing.

Usage::

    from deep_explore import DeepExploreHookManager, HookPoint

    def my_before_scenario(scenario_name, **kwargs):
        print(f"About to run: {scenario_name}")

    def my_on_action_error(action_name, error, **kwargs):
        print(f"Action {action_name} failed: {error}")

    DeepExploreHookManager.register(HookPoint.BEFORE_SCENARIO, my_before_scenario)
    DeepExploreHookManager.register(HookPoint.ON_ACTION_ERROR, my_on_action_error)

    # Later, if needed:
    DeepExploreHookManager.unregister(HookPoint.BEFORE_SCENARIO, my_before_scenario)
"""

import logging
from enum import Enum
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class HookPoint(Enum):
    """Enumeration of available hook points in the test lifecycle.

    Each hook point corresponds to a specific moment during test execution
    where user-defined callbacks can be invoked.
    """

    # Before a scenario starts executing
    BEFORE_SCENARIO = "before_scenario"

    # After a scenario finishes executing (whether success or failure)
    AFTER_SCENARIO = "after_scenario"

    # Before a single action starts executing
    BEFORE_ACTION = "before_action"

    # After a single action finishes executing (whether success or failure)
    AFTER_ACTION = "after_action"

    # When an action raises an exception
    ON_ACTION_ERROR = "on_action_error"


class DeepExploreHookManager:
    """Centralized hook manager for registering and invoking lifecycle callbacks.

    This class provides a global hook registry that allows users to register
    callbacks for specific hook points. Callbacks are invoked in registration
    order when the corresponding event occurs during test execution.

    All registered callbacks receive keyword arguments appropriate to their
    hook point:

    - BEFORE_SCENARIO: scenario_name, deep_explore_object, scenario
    - AFTER_SCENARIO: scenario_name, deep_explore_object, scenario, success
    - BEFORE_ACTION: action_name, deep_explore_object, action
    - AFTER_ACTION: action_name, deep_explore_object, action, result, success
    - ON_ACTION_ERROR: action_name, deep_explore_object, action, error
    """

    _hooks: Dict[HookPoint, List[Callable]] = {
        point: [] for point in HookPoint
    }

    @classmethod
    def register(cls, hook_point: HookPoint, callback: Callable) -> None:
        """Register a callback for a specific hook point.

        Args:
            hook_point: The lifecycle event to hook into.
            callback: Callable to invoke when the event occurs.
                The callback should accept **kwargs to be forward-compatible.

        Raises:
            TypeError: If hook_point is not a HookPoint enum value.
            ValueError: If callback is not callable.
        """
        if not isinstance(hook_point, HookPoint):
            raise TypeError(
                f"hook_point must be a HookPoint enum, got {type(hook_point)}")
        if not callable(callback):
            raise ValueError("callback must be callable")

        cls._hooks[hook_point].append(callback)
        logger.debug(f"Registered hook for {hook_point.value}: {callback}")

    @classmethod
    def unregister(cls, hook_point: HookPoint, callback: Callable) -> bool:
        """Unregister a previously registered callback.

        Args:
            hook_point: The hook point the callback was registered for.
            callback: The exact callback function to remove.

        Returns:
            bool: True if the callback was found and removed, False otherwise.
        """
        try:
            cls._hooks[hook_point].remove(callback)
            logger.debug(
                f"Unregistered hook for {hook_point.value}: {callback}")
            return True
        except ValueError:
            return False

    @classmethod
    def invoke(cls, hook_point: HookPoint, **kwargs: Any) -> None:
        """Invoke all registered callbacks for a hook point.

        Callbacks are invoked in registration order. If a callback raises
        an exception, it is logged and remaining callbacks still execute.

        Args:
            hook_point: The hook point whose callbacks to invoke.
            **kwargs: Arguments to pass to each callback.
        """
        for callback in cls._hooks.get(hook_point, []):
            try:
                callback(**kwargs)
            except Exception as e:
                logger.error(
                    f"Hook callback {callback} for "
                    f"{hook_point.value} raised exception: {e}")

    @classmethod
    def clear(cls, hook_point: HookPoint = None) -> None:
        """Clear registered callbacks.

        Args:
            hook_point: If provided, clear only callbacks for this point.
                If None, clear all callbacks for all hook points.
        """
        if hook_point is not None:
            cls._hooks[hook_point] = []
        else:
            for point in HookPoint:
                cls._hooks[point] = []

    @classmethod
    def get_registered(cls, hook_point: HookPoint) -> List[Callable]:
        """Get list of callbacks registered for a hook point.

        Args:
            hook_point: The hook point to query.

        Returns:
            list: Copy of the registered callbacks list.
        """
        return list(cls._hooks.get(hook_point, []))
