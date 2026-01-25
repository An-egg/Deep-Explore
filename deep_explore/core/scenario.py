# Copyright 2025 Leo John

import logging

logger = logging.getLogger(__name__)


class DeepExploreScenario:
    """测试探索场景执行器"""

    def __init__(self, scenario_name, preconditions, actions):
        """
        Args:
            scenario_name: 场景名称
            preconditions: 前置条件列表
            actions: 动作列表
        """
        self.scenario_name = scenario_name
        self.actions = actions
        self.preconditions = preconditions

    def check_preconditions(self, deep_explore_object):
        """验证所有前置条件是否满足"""
        for precondition in self.preconditions:
            if not precondition.check_precondition(deep_explore_object):
                return False
        return True

    def exec_scenario(self, deep_explore_object):
        """执行场景中的所有动作"""
        action_names = []
        logger.info(f"Executing scenario: {self.scenario_name}")

        for action in self.actions:
            action.exec_action(deep_explore_object)
            action_names.append(action.action_executor.action_name)

        logger.info(f"Completed scenario: {self.scenario_name} "
                    f"with {len(action_names)} actions")
        return action_names
