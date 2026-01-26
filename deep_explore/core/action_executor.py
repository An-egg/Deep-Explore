# Copyright 2025 Leo John

import logging
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


@dataclass
class DeepExploreActionExecutor:
    """Encapsulates action execution configuration information.
    action_id: Unique action identifier
    action_name: Action method name
    action_public_client: Client object
    action_exec_user: Execution user
    except_meet_exception: Whether exception is expected
    action_args: Action parameters
    """
    action_id: str
    action_name: str
    action_public_client: Any
    except_meet_exception: bool = False
    action_args: list = field(default_factory=list)

    def exec_action(self, deep_explore_object):
        """Execute action."""
        from ..utils.util import DeepExploreUtil

        action_name = self.action_name
        logger.info(f"Executing action: {action_name}")
        method = getattr(self.action_public_client, action_name)

        action_args = DeepExploreUtil.resolve_args(
            deep_explore_object, self.action_args)
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
                raise Exception(f"Unexpected exception during action execution: {e}")
            logger.warning(f"Exception during action execution: {e}, but exception was expected for this action")
        return result
