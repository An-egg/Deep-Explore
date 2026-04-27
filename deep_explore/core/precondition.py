# Copyright 2025 Leo John

import logging
from abc import ABC, abstractmethod

from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


class DeepExplorePrecondition(ABC):
    """Abstract base class for test exploration behavior preconditions."""

    @abstractmethod
    def check_precondition(self, deep_explore_object) -> bool:
        """Verify if the target object satisfies the precondition.

        Args:
            deep_explore_object: Target object to verify.

        Returns:
            bool: True if condition is satisfied, False otherwise.
        """
        pass


class DeepExploreStatusPrecondition(DeepExplorePrecondition):
    """Status precondition, verifies if object status is in the allowed list.

    Attributes:
        status_list: List of allowed statuses.
        compare_result: Expected precondition result.
    """

    def __init__(self, status_list, compare_result):
        """Initialize status precondition.

        Args:
            status_list: List of allowed statuses.
            compare_result: Expected precondition result.
        """
        self.status_list = status_list
        self.compare_result = compare_result

    def check_precondition(self, deep_explore_object):
        """Check if object status is in the allowed list.

        Args:
            deep_explore_object: Target object to check.

        Returns:
            bool: True if status is in allowed list, False otherwise.
        """

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
    """Function result matching precondition, verifies if result matches expectation.

    Attributes:
        deep_explore_check: Check method object.
        compare_result: Expected precondition result.
    """

    def __init__(
            self, deep_explore_check, compare_result):
        """Initialize function precondition.

        Args:
            deep_explore_check: Check method object.
            compare_result: Expected precondition result.
        """
        self.deep_explore_check = deep_explore_check
        self.compare_result = compare_result

    def check_precondition(self, deep_explore_object):
        """Check if function result matches expectation.

        Args:
            deep_explore_object: Target object to check.

        Returns:
            bool: True if result matches expectation, False otherwise.
        """
        return self.deep_explore_check.check() == self.compare_result


class DeepExplorePreconditionFactory:
    """Precondition factory class, provides standardized object creation.

    Supports runtime registration of custom precondition types via the
    :meth:`register` class method.
    """

    _custom_preconditions: dict = {}

    @classmethod
    def register(cls, precondition_type: str, precondition_class: type) -> None:
        """Register a custom precondition type.

        Args:
            precondition_type: Unique string identifier for the precondition type.
            precondition_class: Precondition class (must be a subclass of
                DeepExplorePrecondition).

        Raises:
            TypeError: If precondition_class is not a subclass of
                DeepExplorePrecondition.
            ValueError: If precondition_type is already registered.
        """
        if not (isinstance(precondition_class, type)
                and issubclass(precondition_class, DeepExplorePrecondition)):
            raise TypeError(
                f"precondition_class must be a subclass of "
                f"DeepExplorePrecondition, got {precondition_class}")
        if precondition_type in cls._custom_preconditions:
            raise ValueError(
                f"Precondition type '{precondition_type}' is already "
                f"registered. Use a different name or unregister first.")
        cls._custom_preconditions[precondition_type] = precondition_class
        logger.info(f"Registered custom precondition type: {precondition_type}")

    @classmethod
    def unregister(cls, precondition_type: str) -> bool:
        """Unregister a previously registered custom precondition type.

        Args:
            precondition_type: The precondition type identifier to unregister.

        Returns:
            bool: True if the type was found and removed, False otherwise.
        """
        if precondition_type in cls._custom_preconditions:
            del cls._custom_preconditions[precondition_type]
            logger.info(f"Unregistered precondition type: {precondition_type}")
            return True
        return False

    @staticmethod
    def create(precondition_type, precondition_data, compare_result=True):
        """Factory method to create precondition instance.

        Args:
            precondition_type: Precondition type (supports 'status', 'data',
                'function', or any custom registered type).
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

        # Check custom registered types
        custom_class = DeepExplorePreconditionFactory._custom_preconditions.get(
            precondition_type)
        if custom_class is not None:
            return custom_class(precondition_data, compare_result)

        raise ValueError(f"Unsupported precondition type: {precondition_type}")
