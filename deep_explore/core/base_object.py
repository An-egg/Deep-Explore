# Copyright 2025 Leo John
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DeepExploreObject(ABC):
    """测试探索对象基类，提供状态管理和ERIS实例管理功能"""

    def __init__(self):
        self.eris_instance_dict: Dict[str, Any] = {}
        self.last_eris_instance: Optional[Any] = None
        self.data: Optional[Any] = None
        self.update_times: int = 3

    def arg_resolver(self, resolver: str) -> Any:
        """
        参数解析器实现

        支持两种格式:
        1. 无参数: {resolver}()
        2. 带参数: {resolver}_args_{arg1}_{arg2}...()

        Args:
            resolver: 解析器标识符

        Returns:
            object: 解析后的值

        Raises:
            AttributeError: 解析器方法不存在
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
        """执行实际状态更新的抽象方法（由子类实现）"""
        pass

    @abstractmethod
    def get_status(self) -> Any:
        """
        获取当前状态抽象方法

        Returns:
            object: 当前状态值
        """
        pass

    def add_eris_instance(self, action_id: str, eris_instance: Any):
        """
        添加ERIS实例到对象列表

        Args:
            action_id: action的唯一ID
            eris_instance: 要添加的ERIS实例
        """
        action_id = str(action_id)
        self.eris_instance_dict[action_id] = eris_instance
        self.last_eris_instance = eris_instance

    def get_last_eris_instance(self) -> Optional[Any]:
        """
        获取最后操作的ERIS实例

        Returns:
            object: 最后操作的ERIS实例
        """
        return self.last_eris_instance

    def get_eris_instance_list(self):
        """
        获取所有ERIS实例列表

        Returns:
            list: ERIS实例列表
        """
        return self.eris_instance_dict.values()

    def get_eris_instance_by_action_id(self, action_id: str) -> Any:
        """
        通过索引获取ERIS实例

        Args:
            action_id: action唯一ID

        Returns:
            object: 对应的ERIS实例

        Raises:
            KeyError: 索引超出范围
        """
        try:
            eris_instance = self.eris_instance_dict[action_id]
            return eris_instance
        except KeyError:
            logger.error(f"Action_id {action_id} not found")
            raise

    def get_data(self) -> Optional[Any]:
        """
        获取当前数据（自动更新缓存）

        Returns:
            object: 当前数据
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
        """
        更新对象状态（带重试机制）

        Raises:
            RuntimeError: 更新失败超过最大重试次数
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
        """
        设置对象状态更新次数

        Args:
            update_times: 更新次数
        """
        self.update_times = update_times

