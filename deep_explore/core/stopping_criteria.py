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
    """Stopping criteria factory class."""

    @staticmethod
    def create(criteria_type: str, **kwargs):
        """Create stopping criteria instance.

        Args:
            criteria_type: Criteria type ('step' or 'time')
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

        raise ValueError(f"Unsupported criteria type: {criteria_type}")
