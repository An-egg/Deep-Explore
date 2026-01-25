# Copyright 2025 Leo John

import logging
import time

from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class DeepExploreStoppingCriteria(ABC):
    """停止条件的抽象基类"""

    @abstractmethod
    def is_matched(self) -> bool:
        """
        检查停止条件是否满足

        Returns:
            bool: 满足条件返回True，否则False
        """
        pass


class DeepExploreStepStoppingCriteria(DeepExploreStoppingCriteria):
    """基于步骤数的停止条件"""

    def __init__(self, max_steps):
        """
        Args:
            max_steps: 允许的最大步骤数
        """
        self.max_steps = max_steps
        self.current_step = -1  # 首次检查时递增为0

    def is_matched(self):
        """检查当前步骤数是否超过最大值"""
        self.current_step += 1
        satisfied = self.current_step >= self.max_steps
        return satisfied


class DeepExploreTimeStoppingCriteria(DeepExploreStoppingCriteria):
    """基于时间的停止条件"""

    def __init__(self, duration):
        """
        Args:
            duration: 允许的最大持续时间(秒)
        """
        self.start_time = time.time()
        self.duration = duration

    def is_matched(self):
        """检查是否超过最大持续时间"""
        elapsed = time.time() - self.start_time
        satisfied = elapsed >= self.duration
        return satisfied


class DeepExploreEndTimeStoppingCriteria(DeepExploreStoppingCriteria):
    """基于指定日期时间的停止条件"""

    def __init__(self, end_time_str):
        """
        Args:
            end_time_str: 停止的具体日期时间字符串，
                          格式要求: "YYYY-MM-DD HH:MM:SS"
                          例如: "2026-01-21 16:00:00"
        """
        # 定义时间格式
        time_format = "%Y-%m-%d %H:%M:%S"

        # 将字符串解析为 datetime 对象
        end_datetime = datetime.strptime(end_time_str, time_format)

        # 将 datetime 对象转换为 Unix 时间戳（秒），便于后续直接进行数值比较
        self.end_timestamp = end_datetime.timestamp()

    def is_matched(self):
        """检查当前系统时间是否已达到或超过设定的截止时间"""
        # 获取当前时间的时间戳
        current_time = time.time()

        # 如果当前时间大于等于目标截止时间，则停止
        satisfied = current_time >= self.end_timestamp
        return satisfied


class DeepExploreStoppingCriteriaFactory:
    """停止条件工厂类"""

    @staticmethod
    def create(criteria_type: str, **kwargs):
        """
        创建停止条件实例

        Args:
            criteria_type: 条件类型 ('step' 或 'time')
            **kwargs: 类型所需参数
                - 'step': max_steps
                - 'time': duration
                - 'end_time': end_time

        Returns:
            DeepExploreStoppingCriteria: 停止条件实例

        Raises:
            ValueError: 不支持的类型
        """
        logger.info(f"Creating stopping criteria of type: {criteria_type}")

        if criteria_type == "step":
            return DeepExploreStepStoppingCriteria(kwargs["max_steps"])

        elif criteria_type == "time":
            return DeepExploreTimeStoppingCriteria(kwargs["duration"])

        elif criteria_type == "end_time":
            return DeepExploreEndTimeStoppingCriteria(kwargs["end_time"])

        raise ValueError(f"Unsupported criteria type: {criteria_type}")
