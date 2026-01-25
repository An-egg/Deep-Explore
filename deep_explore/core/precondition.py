# Copyright 2025 Leo John

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .action_check import DeepExploreActionCheck
    from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


class DeepExplorePrecondition(ABC):
    """测试探索行为预检条件的抽象基类"""

    @abstractmethod
    def check_precondition(self, deep_explore_object) -> bool:
        """
        验证目标对象是否满足预检条件

        Args:
            deep_explore_object: 要验证的目标对象

        Returns:
            bool: 满足条件返回True，否则False
        """
        pass


class DeepExploreStatusPrecondition(DeepExplorePrecondition):
    """状态预检条件，验证对象状态是否在允许列表中"""

    def __init__(self, status_list, compare_result):
        """
        Args:
            status_list: 允许的状态列表
            compare_result: 预期的前置条件结果
        """
        self.status_list = status_list
        self.compare_result = compare_result

    def check_precondition(self, deep_explore_object):
        """检查对象状态是否在允许列表中"""
        from ..utils.util import DeepExploreUtil

        current_status = deep_explore_object.get_status()
        result = current_status in DeepExploreUtil.resolve_args(
            deep_explore_object, self.status_list)
        return result == self.compare_result


class DeepExploreMatchDataPrecondition(DeepExplorePrecondition):
    """数据结构匹配预检条件，验证对象数据是否包含指定结构"""

    def __init__(self, data, compare_result):
        """
        Args:
            data: 需要匹配的数据模板（字典结构）
            compare_result: 预期的前置条件结果
        """
        self.data = data
        self.compare_result = compare_result

    def check_precondition(self, deep_explore_object):
        """递归检查数据是否包含指定结构"""
        from ..utils.util import DeepExploreUtil

        def is_subset_recursive(sub, super_obj):
            """递归检查子集关系"""
            # 基本类型直接比较
            if not isinstance(sub, (dict, list)):
                return sub == super_obj

            # 字典类型检查
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

            # 列表类型检查（要求顺序一致）
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
    """函数结果匹配预检条件，验证结果是否符合预期"""

    def __init__(
            self, deep_explore_check: DeepExploreActionCheck, compare_result):
        """
        Args:
            deep_explore_check: check方法对象
            compare_result: 预期的前置条件结果
        """
        self.deep_explore_check = deep_explore_check
        self.compare_result = compare_result

    def check_precondition(self, deep_explore_object):
        return self.deep_explore_check.check() == self.compare_result


class DeepExplorePreconditionFactory:
    """预检条件工厂类，提供标准化的对象创建方式"""

    @staticmethod
    def create(precondition_type, precondition_data, compare_result=True):
        """
        创建预检条件实例的工厂方法

        Args:
            precondition_type: 预检类型 (支持 'status', 'data')
            precondition_data: 对应类型需要的参数
            compare_result: 比较预期结果
        Returns:
            DeepExplorePrecondition: 预检条件实例

        Raises:
            ValueError: 不支持的类型
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
        raise ValueError(f"Unsupported precondition type: {precondition_type}")
