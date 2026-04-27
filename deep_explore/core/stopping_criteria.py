# Copyright 2025 Leo John

import logging
import time

from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class DeepExploreStoppingCriteria(ABC):
    """Abstract base class for stopping criteria."""

    @abstractmethod
    def is_matched(self) -> bool:
        """Check if stopping criteria is satisfied.

        Returns:
            bool: True if condition is satisfied, False otherwise
        """
        pass


class DeepExploreStepStoppingCriteria(DeepExploreStoppingCriteria):
    """Step-based stopping criteria."""

    def __init__(self, max_steps):
        """Initialize step stopping criteria.

        Args:
            max_steps: Maximum allowed number of steps
        """
        self.max_steps = max_steps
        self.current_step = -1  # Increment to 0 on first check

    def is_matched(self):
        """Check if current step count exceeds maximum."""
        self.current_step += 1
        satisfied = self.current_step >= self.max_steps
        return satisfied


class DeepExploreTimeStoppingCriteria(DeepExploreStoppingCriteria):
    """Time-based stopping criteria."""

    def __init__(self, duration):
        """Initialize time stopping criteria.

        Args:
            duration: Maximum allowed duration in seconds
        """
        self.start_time = time.time()
        self.duration = duration

    def is_matched(self):
        """Check if maximum duration is exceeded."""
        elapsed = time.time() - self.start_time
        satisfied = elapsed >= self.duration
        return satisfied


class DeepExploreEndTimeStoppingCriteria(DeepExploreStoppingCriteria):
    """Specific datetime-based stopping criteria."""

    def __init__(self, end_time_str):
        """Initialize end time stopping criteria.

        Args:
            end_time_str: Specific datetime string for stopping,
                          format required: "YYYY-MM-DD HH:MM:SS"
                          example: "2026-01-21 16:00:00"
        """
        # Define time format
        time_format = "%Y-%m-%d %H:%M:%S"

        # Parse string to datetime object
        end_datetime = datetime.strptime(end_time_str, time_format)

        # Convert datetime object to Unix timestamp (seconds) for direct numerical comparison
        self.end_timestamp = end_datetime.timestamp()

    def is_matched(self):
        """Check if current system time has reached or exceeded the set deadline."""
        # Get current time timestamp
        current_time = time.time()

        # Stop if current time is greater than or equal to target deadline
        satisfied = current_time >= self.end_timestamp
        return satisfied


class DeepExploreStoppingCriteriaFactory:
    """Stopping criteria factory class.

    Supports runtime registration of custom criteria types via the
    :meth:`register` class method.
    """

    _custom_criteria: dict = {}

    @classmethod
    def register(cls, criteria_type: str, criteria_class: type) -> None:
        """Register a custom stopping criteria type.

        Args:
            criteria_type: Unique string identifier for the criteria type.
            criteria_class: Criteria class (must be a subclass of
                DeepExploreStoppingCriteria).

        Raises:
            TypeError: If criteria_class is not a subclass of
                DeepExploreStoppingCriteria.
            ValueError: If criteria_type is already registered.
        """
        if not (isinstance(criteria_class, type)
                and issubclass(criteria_class, DeepExploreStoppingCriteria)):
            raise TypeError(
                f"criteria_class must be a subclass of "
                f"DeepExploreStoppingCriteria, got {criteria_class}")
        if criteria_type in cls._custom_criteria:
            raise ValueError(
                f"Criteria type '{criteria_type}' is already registered. "
                f"Use a different name or unregister first.")
        cls._custom_criteria[criteria_type] = criteria_class
        logger.info(f"Registered custom criteria type: {criteria_type}")

    @classmethod
    def unregister(cls, criteria_type: str) -> bool:
        """Unregister a previously registered custom criteria type.

        Args:
            criteria_type: The criteria type identifier to unregister.

        Returns:
            bool: True if the type was found and removed, False otherwise.
        """
        if criteria_type in cls._custom_criteria:
            del cls._custom_criteria[criteria_type]
            logger.info(f"Unregistered criteria type: {criteria_type}")
            return True
        return False

    @staticmethod
    def create(criteria_type: str, **kwargs):
        """Create stopping criteria instance.

        Args:
            criteria_type: Criteria type ('step', 'time', 'end_time',
                or any custom registered type).
            **kwargs: Type-specific parameters
                - 'step': max_steps
                - 'time': duration
                - 'end_time': end_time

        Returns:
            DeepExploreStoppingCriteria: Stopping criteria instance

        Raises:
            ValueError: Unsupported type
        """
        logger.info(f"Creating stopping criteria of type: {criteria_type}")

        if criteria_type == "step":
            return DeepExploreStepStoppingCriteria(kwargs["max_steps"])

        elif criteria_type == "time":
            return DeepExploreTimeStoppingCriteria(kwargs["duration"])

        elif criteria_type == "end_time":
            return DeepExploreEndTimeStoppingCriteria(kwargs["end_time"])

        # Check custom registered types
        custom_class = DeepExploreStoppingCriteriaFactory._custom_criteria.get(
            criteria_type)
        if custom_class is not None:
            return custom_class(**kwargs)

        raise ValueError(f"Unsupported criteria type: {criteria_type}")
