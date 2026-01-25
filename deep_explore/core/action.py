# Copyright 2025 Leo John

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List

logger = logging.getLogger(__name__)


@dataclass
class DeepExploreAction:
    """
    测试探索动作执行器，封装动作执行的前置检查、执行和后置验证逻辑

    Args:
        action_executor: 动作的配置信息
        preconditions: 动作执行的前提条件列表
        pre_checks: 动作执行前必须通过的检查项列表
        post_checks: 动作执行后必须通过的验证项列表
        update_positions: 执行object更新动作的位置列表
    """
    action_executor: Any
    preconditions: list
    pre_checks: list
    post_checks: list
    update_positions: List[str] = field(default_factory=lambda: ["end"])

    def exec_action(self, deep_explore_object):
        """
                执行动作的完整生命周期管理:
                1. 执行所有前置检查(pre_checks)
                2. 调用目标动作方法
                3. 注册ERIS返回对象
                4. 执行所有后置验证(post_checks)
                5. 更新测试探索对象状态

                Returns:
                    object: 动作方法的返回结果

                Raises:
                    RuntimeError: 前置检查或后置检查失败时抛出
        """
        deep_explore_object.set_update_times(999)
        if "start" in self.update_positions:
            deep_explore_object.update_state()
        # 执行 pre_checks
        pre_checks = self.pre_checks
        for pre_check in pre_checks:
            if not pre_check.check():
                raise Exception(
                    f"Pre-check {pre_check}\n"
                    f"failed for action: {self.action_executor}")
        if "before_exec_action" in self.update_positions:
            deep_explore_object.update_state()
        # 执行动作
        result = self.action_executor.exec_action(deep_explore_object)
        if "after_exec_action" in self.update_positions:
            deep_explore_object.update_state()
        # 执行 post_checks
        post_checks = self.post_checks
        for post_check in post_checks:
            if not post_check.check():
                raise Exception(
                    f"Post-check {post_check}\n"
                    f"failed for action: {self.action_executor}")
        if "end" in self.update_positions:
            deep_explore_object.update_state()
        deep_explore_object.set_update_times(3)
        return result

    def check_preconditions(self, deep_explore_object):
        """
                验证所有前置条件是否满足

                Returns:
                    bool: 所有条件满足返回True, 任一条件失败返回False
        """
        for precondition in self.preconditions:
            if not precondition.check_precondition(deep_explore_object):
                return False
        return True
