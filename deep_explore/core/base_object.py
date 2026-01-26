# Copyright 2025 Leo John
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DeepExploreObject(ABC):
    """Base class for test exploration objects.

    Provides state management and ERIS instance management functionality.
    """

    def __init__(self):
        """Initialize DeepExploreObject."""
        self.data: Optional[Any] = None
        self.update_times: int = 3

    def arg_resolver(self, resolver: str) -> Any:
        """Parameter resolver implementation.

        Supports two formats:
        1. No parameters: {resolver}()
        2. With parameters: {resolver}_args_{arg1}_{arg2}...()

        Args:
            resolver: Resolver identifier.

        Returns:
            Any: Resolved value.

        Raises:
            AttributeError: Resolver method does not exist.
        """
        try:
            if "_args_" in resolver:
                parts = resolver.split('_args_')
                method_name = f"{parts[0]}"
                args = parts[1].split("_")
                return getattr(self, method_name)(*args)
            else:
                method_name = f"{resolver}"
                return getattr(self, method_name)()

        except AttributeError as e:
            raise AttributeError(f"Invalid resolver: {resolver}") from e
        except Exception as e:
            raise Exception(f"Resolver execution failed for {resolver}: {e}")

    @abstractmethod
    def _do_update_state(self):
        """Perform actual state update.

        Abstract method to be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_status(self) -> Any:
        """Get current status.

        Abstract method to be implemented by subclasses.

        Returns:
            Any: Current status value.
        """
        pass

    def get_data(self) -> Optional[Any]:
        """Get current data with automatic cache update.

        Returns:
            Optional[Any]: Current data.
        """
        try:
            if self.update_times > 0:
                self.update_times -= 1
                self._do_update_state()
        except Exception as e:
            logger.exception(
                f"Failed to update state, use old data. Exception: {e}")
        return self.data

    def update_state(self):
        """Update object state with retry mechanism.

        Raises:
            Exception: Update failed after maximum retry attempts.
        """
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            try:
                self._do_update_state()
                return

            except Exception as e:
                logger.warning(
                    f"State update attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    logger.info("Retrying in 1 second...")
                    time.sleep(1)
                else:
                    raise Exception(
                        f"State update failed after {max_retries} attempts.")

    def set_update_times(self, update_times: int):
        """Set object state update count.

        Args:
            update_times: Number of updates.
        """
        self.update_times = update_times

