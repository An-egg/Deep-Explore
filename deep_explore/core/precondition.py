# Copyright 2025 Leo John

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .action_check import DeepExploreActionCheck
    from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


class DeepExplorePrecondition(ABC):
    """Abstract base class for test exploration behavior preconditions."""

    @abstractmethod
    def check_precondition(self, deep_explore_object) -> bool:
        """Verify if the target object satisfies the precondition.

        Args:
            deep_explore_object: Target object to verify

        Returns:
            bool: True if condition is satisfied, False otherwise
        """
        pass


class DeepExploreStatusPrecondition(DeepExplorePrecondition):
    """Status precondition, verifies if object status is in the allowed list."""

    def __init__(self, status_list, compare_result):
        """Initialize status precondition.

        Args:
            status_list: List of allowed statuses
            compare_result: Expected precondition result
        """
        self.status_list = status_list
        self.compare_result = compare_result

    def check_precondition(self, deep_explore_object):
        """Check if object status is in the allowed list."""
        from ..utils.util import DeepExploreUtil

        current_status = deep_explore_object.get_status()
        result = current_status in DeepExploreUtil.resolve_args(
            deep_explore_object, self.status_list)
        return result == self.compare_result


class DeepExploreMatchDataPrecondition(DeepExplorePrecondition):
    """Data structure matching precondition, verifies if object data contains specified structure."""

    def __init__(self, data, compare_result):
        """Initialize data matching precondition.

        Args:
            data: Data template to match (dictionary structure)
            compare_result: Expected precondition result
        """
        self.data = data
        self.compare_result = compare_result

    def check_precondition(self, deep_explore_object):
        """Recursively check if data contains specified structure."""
        from ..utils.util import DeepExploreUtil

        def is_subset_recursive(sub, super_obj):
            """Recursively check subset relationship."""
            # Basic types direct comparison
            if not isinstance(sub, (dict, list)):
                return sub == super_obj

            # Dictionary type check
            if isinstance(sub, dict):
                if sub == {} and len(super_obj) > 0:
                    return False
                if not isinstance(super_obj, dict):
                    return False
                for key, value in sub.items():
                    if key not in super_obj:
                        return False
                    if not is_subset_recursive(value, super_obj[key]):
                        return False
                return True

            # List type check (requires consistent order)
            if isinstance(sub, list):
                if sub == [] and len(super_obj) > 0:
                    return False
                if not isinstance(super_obj, list) or len(super_obj) < len(
                        sub):
                    return False
                for i in range(len(sub)):
                    if not is_subset_recursive(sub[i], super_obj[i]):
                        return False
                return True

            return False

        target_data = deep_explore_object.get_data()
        result = is_subset_recursive(
            DeepExploreUtil.resolve_args(
                deep_explore_object, self.data), target_data)

        return result == self.compare_result


class DeepExploreFunctionPrecondition(DeepExplorePrecondition):
    """Function result matching precondition, verifies if result matches expectation."""

    def __init__(
            self, deep_explore_check: DeepExploreActionCheck, compare_result):
        """Initialize function precondition.

        Args:
            deep_explore_check: Check method object
            compare_result: Expected precondition result
        """
        self.deep_explore_check = deep_explore_check
        self.compare_result = compare_result

    def check_precondition(self, deep_explore_object):
        return self.deep_explore_check.check() == self.compare_result


class DeepExplorePreconditionFactory:
    """Precondition factory class, provides standardized object creation."""

    @staticmethod
    def create(precondition_type, precondition_data, compare_result=True):
        """Factory method to create precondition instance.

        Args:
            precondition_type: Precondition type (supports 'status', 'data')
            precondition_data: Parameters required for the type
            compare_result: Compare expected result
        Returns:
            DeepExplorePrecondition: Precondition instance

        Raises:
            ValueError: Unsupported type
        """
        logger.info(f"Creating precondition of type: {precondition_type}")

        if precondition_type == "status":
            return DeepExploreStatusPrecondition(
                precondition_data, compare_result)

        elif precondition_type == "data":
            return DeepExploreMatchDataPrecondition(
                precondition_data, compare_result)
        elif precondition_type == "function":
            return DeepExploreFunctionPrecondition(
                precondition_data, compare_result)
        raise ValueError(f"Unsupported precondition type: {precondition_type}")
