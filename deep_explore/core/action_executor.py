# Copyright 2025 Leo John

import logging
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


@dataclass
class DeepExploreActionExecutor:
    """
    封装动作执行的配置信息
    action_id: 动作唯一标识
    action_name: 动作方法名称
    action_public_client: 客户端对象
    action_exec_user: 执行用户
    except_meet_exception: 是否预期异常
    action_args: 动作参数
    """
    action_id: str
    action_name: str
    action_public_client: Any
    action_exec_user: str = "admin_login"
    except_meet_exception: bool = False
    action_args: list = field(default_factory=list)

    def __post_init__(self):
        # Optional: Support session manager if available
        try:
            from hours.common.common import SessionManager
            getattr(SessionManager, self.action_exec_user)()
        except ImportError:
            pass

        # Use public manager if client is a string path
        if isinstance(self.action_public_client, str):
            from ..utils.public_manager import DeepExplorePublicManager
            self.action_public_client = (
                DeepExplorePublicManager.create_public_client(
                    self.action_public_client))

    def exec_action(self, deep_explore_object):
        """执行动作"""
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
                raise Exception(f"执行动作出现非预期的异常:{e}")
            logger.warning(f"执行动作出现异常:{e}, 但预期该动作就会出现异常")
        # 如果返回的是ERIS对象注册到测试上下文中
        if hasattr(result, '__class__') and 'ERIS' in result.__class__.__name__:
            logger.info(
                "Register eris instance in DeepExploreObject by action_id")
            deep_explore_object.add_eris_instance(self.action_id, result)
        return result
