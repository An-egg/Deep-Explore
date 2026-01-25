# Copyright 2025 Leo John

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


class DeepExploreActionCheck:
    """
    测试探索动作检查执行器，负责动态加载和执行检查逻辑

    Args:
        deep_explore_object: 关联的测试探索对象
        check_info: 检查函数信息元组 (函数路径或函数引用, *参数)
        check_result: 预期的检查结果
    """

    def __init__(self, deep_explore_object, check_info, check_result):
        self.deep_explore_object = deep_explore_object
        self.check_func = check_info[0]
        self.check_func_args = list(check_info[1:])
        self.check_result = check_result

    def __repr__(self):
        # 使用 !r 可以自动给字符串加引号，或者调用子对象的 __repr__
        return (f"DeepExploreActionCheck("
                f"deep_explore_object={self.deep_explore_object!r}, "
                f"check_func={self.check_func!r}, "
                f"check_func_args={self.check_func_args!r}, "
                f"check_result={self.check_result!r})")

    def check(self):
        """
        执行检查逻辑并验证结果

        Returns:
            bool: 检查结果是否符合预期

        Raises:
            RuntimeError: 检查执行过程中发生错误
        """
        from ..utils.util import DeepExploreUtil

        try:
            # 动态导入并返回可执行方法
            method = DeepExploreUtil.dynamic_import(self.check_func)

            # 解析参数并执行检查
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
