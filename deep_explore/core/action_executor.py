# Copyright 2025 Leo John

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass, field
from typing import Any, Optional

from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


@dataclass
class DeepExploreActionExecutor:
    """Encapsulates action execution configuration information.

    Attributes:
        action_id: Unique action identifier.
        action_name: Action method name.
        action_public_client: Client object.
        action_exec_user: Execution user.
        except_meet_exception: Whether exception is expected.
        action_args: Action parameters.
        timeout: Maximum execution time in seconds (None means no timeout).
    """
    action_id: str
    action_name: str
    action_public_client: Any
    except_meet_exception: bool = False
    action_args: list = field(default_factory=list)
    timeout: Optional[float] = None

    def exec_action(self, deep_explore_object):
        """Execute action with optional timeout control.

        If ``timeout`` is set, the action will be executed in a separate
        thread and a :class:`TimeoutError` will be raised if the execution
        exceeds the specified duration.

        Args:
            deep_explore_object: Test exploration object.

        Returns:
            Any: Return result of the action method.

        Raises:
            TimeoutError: When action execution exceeds the timeout.
            Exception: When unexpected exception occurs during execution.
        """
        action_name = self.action_name
        logger.info(f"Executing action: {action_name}")

        method = getattr(self.action_public_client, action_name)
        action_args = DeepExploreUtil.resolve_args(
            deep_explore_object, self.action_args)

        if self.timeout is not None:
            return self._exec_with_timeout(method, action_args)
        return self._exec_without_timeout(method, action_args)

    def _exec_without_timeout(self, method, action_args):
        """Execute action without timeout.

        Args:
            method: Callable method to execute.
            action_args: Resolved arguments.

        Returns:
            Any: Return result of the action method.

        Raises:
            Exception: When unexpected exception occurs during execution.
        """
        result = None
        try:
            if len(action_args) != 0 and isinstance(action_args[0], tuple):
                kwargs = {}
                for arg in action_args:
                    kwargs[arg[0]] = arg[1]
                result = method(**kwargs) if callable(method) else None
            else:
                result = method(*action_args) if callable(method) else None
        except Exception as e:
            if not self.except_meet_exception:
                raise Exception(
                    f"Unexpected exception during action execution: {e}")
            logger.warning(f"Exception during action execution: {e}, "
                           f"but exception was expected for this action")
        return result

    def _exec_with_timeout(self, method, action_args):
        """Execute action with timeout control using ThreadPoolExecutor.

        Args:
            method: Callable method to execute.
            action_args: Resolved arguments.

        Returns:
            Any: Return result of the action method.

        Raises:
            TimeoutError: When action execution exceeds the timeout.
            Exception: When unexpected exception occurs during execution.
        """
        def _run():
            if len(action_args) != 0 and isinstance(action_args[0], tuple):
                kwargs = {}
                for arg in action_args:
                    kwargs[arg[0]] = arg[1]
                return method(**kwargs) if callable(method) else None
            return method(*action_args) if callable(method) else None

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run)
            try:
                result = future.result(timeout=self.timeout)
                return result
            except TimeoutError:
                future.cancel()
                logger.error(
                    f"Action '{self.action_name}' timed out after "
                    f"{self.timeout}s")
                raise TimeoutError(
                    f"Action '{self.action_name}' execution timed out "
                    f"after {self.timeout} seconds")
            except Exception as e:
                if not self.except_meet_exception:
                    raise Exception(
                        f"Unexpected exception during action execution: {e}")
                logger.warning(f"Exception during action execution: {e}, "
                               f"but exception was expected for this action")
                return None
