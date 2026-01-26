# Copyright 2025 Leo John

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List

logger = logging.getLogger(__name__)


@dataclass
class DeepExploreAction:
    """Test exploration action executor, encapsulating pre-check, execution, and post-validation logic.

    Args:
        action_executor: Action configuration information
        preconditions: List of preconditions for action execution
        pre_checks: List of checks that must pass before action execution
        post_checks: List of validations that must pass after action execution
        update_positions: List of positions to execute object update actions
    """
    action_executor: Any
    preconditions: list
    pre_checks: list
    post_checks: list
    update_positions: List[str] = field(default_factory=lambda: ["end"])

    def exec_action(self, deep_explore_object):
        """Execute the complete lifecycle of an action:
        1. Execute all pre-checks (pre_checks)
        2. Call target action method
        3. Register ERIS return object
        4. Execute all post-validations (post_checks)
        5. Update test exploration object state

        Returns:
            object: Return result of the action method

        Raises:
            RuntimeError: Raised when pre-check or post-check fails
        """
        deep_explore_object.set_update_times(999)
        if "start" in self.update_positions:
            deep_explore_object.update_state()
        # Execute pre_checks
        pre_checks = self.pre_checks
        for pre_check in pre_checks:
            if not pre_check.check():
                raise Exception(
                    f"Pre-check {pre_check}\n"
                    f"failed for action: {self.action_executor}")
        if "before_exec_action" in self.update_positions:
            deep_explore_object.update_state()
        # Execute action
        result = self.action_executor.exec_action(deep_explore_object)
        if "after_exec_action" in self.update_positions:
            deep_explore_object.update_state()
        # Execute post_checks
        post_checks = self.post_checks
        for post_check in post_checks:
            if not post_check.check():
                raise Exception(
                    f"Post-check {post_check}\n"
                    f"failed for action: {self.action_executor}")
        if "end" in self.update_positions:
            deep_explore_object.update_state()
        deep_explore_object.set_update_times(3)
        return result

    def check_preconditions(self, deep_explore_object):
        """Verify all preconditions are satisfied.

        Returns:
            bool: True if all conditions are satisfied, False if any condition fails
        """
        for precondition in self.preconditions:
            if not precondition.check_precondition(deep_explore_object):
                return False
        return True
