# Copyright 2025 Leo John

import logging
from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


class DeepExploreActionCheck:
    """Test exploration action check executor, responsible for dynamically loading and executing check logic.

    Args:
        deep_explore_object: Associated test exploration object
        check_info: Check function information tuple (function path or reference, *parameters)
        check_result: Expected check result
    """

    def __init__(self, deep_explore_object, check_info, check_result):
        self.deep_explore_object = deep_explore_object
        self.check_func = check_info[0]
        self.check_func_args = list(check_info[1:])
        self.check_result = check_result

    def __repr__(self):
        # Use !r to automatically add quotes to strings, or call child object's __repr__
        return (f"DeepExploreActionCheck("
                f"deep_explore_object={self.deep_explore_object!r}, "
                f"check_func={self.check_func!r}, "
                f"check_func_args={self.check_func_args!r}, "
                f"check_result={self.check_result!r})")

    def check(self):
        """Execute check logic and verify result.

        Returns:
            bool: Whether check result matches expectation

        Raises:
            RuntimeError: Error occurred during check execution
        """

        try:
            # Dynamically import and return executable method
            method = DeepExploreUtil.dynamic_import(self.check_func)

            # Resolve parameters and execute check
            all_args = DeepExploreUtil.resolve_args(
                self.deep_explore_object, self.check_func_args)
            logger.info(f"Executing check: {method.__name__} with args: "
                        f"{all_args}, expect result: {self.check_result}")
            if len(all_args) != 0 and isinstance(all_args[0], tuple):
                kwargs = {}
                for arg in all_args:
                    kwargs[arg[0]] = arg[1]

                actual_result = method(**kwargs)
            else:
                actual_result = method(*all_args)
            return actual_result == self.check_result

        except Exception as e:
            raise Exception(
                f"Check execution failed for {self.check_func}: {e}") from e
