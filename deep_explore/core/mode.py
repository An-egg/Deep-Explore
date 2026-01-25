# Copyright 2025 Leo John

import logging
import random

logger = logging.getLogger(__name__)


class DeepExploreMode:
    """
    测试探索模式基类，提供场景/动作执行统计功能

    属性:
        already_exec_scenarios: 已执行场景记录列表
        already_exec_actions: 已执行动作记录列表
    """
    already_exec_scenarios = []
    already_exec_actions = []

    def exec_test(self):
        """执行测试的主入口方法（需子类实现）"""
        pass

    def scenario_statistics(self):
        """
        记录并输出场景执行统计信息

        步骤:
        1. 记录所有已执行场景
        2. 统计各场景执行频次
        3. 清空执行记录
        """
        logger.info("Already exec scenario total count: "
                    f"{len(self.already_exec_scenarios)}")
        logger.info("Already exec scenario order records: "
                    f"{self.already_exec_scenarios}")

        # 统计各场景执行次数
        scenario_counter = {}
        for scenario_record in self.already_exec_scenarios:
            for scenario_name in scenario_record.keys():
                scenario_counter[scenario_name] = scenario_counter.get(
                    scenario_name, 0) + 1

        logger.info(f"Already exec scenario statistics: {scenario_counter}")
        self.already_exec_scenarios = []  # 清空记录

    def action_statistics(self):
        """
        记录并输出动作执行统计信息

        步骤:
        1. 记录所有已执行动作
        2. 统计各动作执行频次
        3. 清空执行记录
        """
        logger.info("Already exec action total count: "
                    f"{len(self.already_exec_actions)}")
        logger.info("Already exec action order records: "
                    f"{self.already_exec_actions}")

        # 统计各动作执行次数
        action_counter = {}
        for action_name in self.already_exec_actions:
            action_counter[action_name] = action_counter.get(
                action_name, 0) + 1

        logger.info(f"Already exec action statistics: {action_counter}")
        self.already_exec_actions = []  # 清空记录


class DeepExploreRandomScenarioMode(DeepExploreMode):
    """
    随机场景测试模式

    Args:
        deep_explore_object: 测试探索目标对象
        stop_criteria_list: 停止条件列表
        scenarios: 可执行场景列表
    """

    def __init__(self, deep_explore_object, stop_criteria_list, scenarios):
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.scenarios = scenarios
        self.already_exec_scenarios = []  # 覆盖父类变量为实例变量

    def exec_test(self):
        """随机执行场景直到满足停止条件"""
        while True:
            # 检查停止条件
            for criteria in self.stop_criteria_list:
                if criteria.is_matched():
                    logger.info(
                        "Stopping criteria satisfied: "
                        f"{criteria.__class__.__name__}. Exiting test.")
                    self.scenario_statistics()
                    return

            # 筛选满足前置条件的场景
            available_scenarios = [
                s for s in self.scenarios
                if s.check_preconditions(self.deep_explore_object)
            ]

            if not available_scenarios:
                logger.info("No available scenarios. Exiting test.")
                self.scenario_statistics()
                return

            # 随机选择并执行场景
            selected_scenario = random.choice(available_scenarios)
            try:
                scenario_name = selected_scenario.scenario_name
                # 记录执行场景
                scenario_record = {scenario_name: []}
                self.already_exec_scenarios.append(scenario_record)
                action_list = selected_scenario.exec_scenario(
                    self.deep_explore_object)
                # 更新场景里所执行的动作
                scenario_record[scenario_name] = action_list

            except Exception as e:
                self.scenario_statistics()
                raise Exception(f"Scenario execution failed: {e}")


class DeepExploreRandomActionMode(DeepExploreMode):
    """
    随机动作测试模式

    Args:
        deep_explore_object: 测试探索目标对象
        stop_criteria_list: 停止条件列表
        actions: 可执行动作列表
    """

    def __init__(self, deep_explore_object, stop_criteria_list, actions):
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.actions = actions
        self.already_exec_actions = []  # 覆盖父类变量为实例变量

    def exec_test(self):
        """随机执行动作直到满足停止条件"""
        while True:
            # 检查停止条件
            for criteria in self.stop_criteria_list:
                if criteria.is_matched():
                    logger.info(
                        "Stopping criteria satisfied: "
                        f"{criteria.__class__.__name__}. Exiting test.")
                    self.action_statistics()
                    return

            # 筛选满足前置条件的动作
            available_actions = [
                a for a in self.actions
                if a.check_preconditions(self.deep_explore_object)
            ]

            if not available_actions:
                logger.info("No available actions. Exiting test.")
                self.action_statistics()
                return

            # 随机选择并执行动作
            selected_action = random.choice(available_actions)
            try:
                action_name = selected_action.action_executor.action_name
                # 记录执行动作
                self.already_exec_actions.append(action_name)
                selected_action.exec_action(self.deep_explore_object)

            except Exception as e:
                self.action_statistics()
                raise Exception(f"Action execution failed: {e}")


class DeepExploreSequenceScenarioMode(DeepExploreMode):
    """
    顺序场景测试模式

    Args:
        deep_explore_object: 测试探索目标对象
        stop_criteria_list: 停止条件列表
        scenarios: 可执行场景列表
        reverse: 是否反向执行序列 (默认False)
    """

    def __init__(self, deep_explore_object, stop_criteria_list, scenarios,
                 reverse=False):
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.scenarios = scenarios[::-1] if reverse else scenarios
        self.already_exec_scenarios = []  # 覆盖父类变量为实例变量

    def exec_test(self):
        """按顺序执行场景直到满足停止条件"""
        index = 0
        while True:
            # 检查停止条件
            for criteria in self.stop_criteria_list:
                if criteria.is_matched():
                    logger.info(
                        "Stopping criteria satisfied: "
                        f"{criteria.__class__.__name__}. Exiting test.")
                    self.scenario_statistics()
                    return

            # 检查是否完成所有场景
            if index >= len(self.scenarios):
                logger.info("All scenarios executed. Exiting test.")
                self.scenario_statistics()
                return

            # 执行当前场景
            current_scenario = self.scenarios[index]
            index += 1
            try:
                scenario_name = current_scenario.scenario_name
                # 记录执行场景
                scenario_record = {scenario_name: []}
                self.already_exec_scenarios.append(scenario_record)
                action_list = current_scenario.exec_scenario(
                    self.deep_explore_object)
                # 更新场景里所执行的动作
                scenario_record[scenario_name] = action_list

            except Exception as e:
                self.scenario_statistics()
                raise Exception(f"Scenario execution failed: {e}")


class DeepExploreSequenceActionMode(DeepExploreMode):
    """
    按序执行动作测试模式

    Args:
        deep_explore_object: 测试探索目标对象
        stop_criteria_list: 停止条件列表
        actions: 可执行动作列表
        reverse: 是否逆序执行动作
    """

    def __init__(self, deep_explore_object, stop_criteria_list, actions,
                 reverse=False):
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.actions = actions[::-1] if reverse else actions
        self.already_exec_actions = []  # 覆盖父类变量为实例变量

    def exec_test(self):
        """顺序执行动作直到满足停止条件或执行完成所有动作"""
        index = 0
        while True:
            # 检查停止条件
            for criteria in self.stop_criteria_list:
                if criteria.is_matched():
                    logger.info(
                        "Stopping criteria satisfied: "
                        f"{criteria.__class__.__name__}. Exiting test.")
                    self.action_statistics()
                    return

            # 检查是否完成所有动作
            if index >= len(self.actions):
                logger.info("All scenarios executed. Exiting test.")
                self.action_statistics()
                return

            # 执行当前场景
            current_action = self.actions[index]
            index += 1
            try:
                action_name = current_action.action_executor.action_name
                # 记录执行动作
                self.already_exec_actions.append(action_name)
                current_action.exec_action(self.deep_explore_object)

            except Exception as e:
                self.action_statistics()
                raise Exception(f"Action execution failed: {e}")


class DeepExploreModeFactory:
    """测试探索模式工厂类"""

    @staticmethod
    def create_mode(mode_type, deep_explore_object, stop_criteria_list,
                    test_objects, **kwargs):
        """
        创建指定类型的测试探索模式实例

        Args:
            mode_type: 模式类型 ('random_scenario', 'sequence_scenario',
                               'random_action')
            deep_explore_object: 测试探索目标对象
            stop_criteria_list: 停止条件列表
            test_objects: 测试对象集合（场景或动作）
            **kwargs: 模式特定参数（如reverse）

        Returns:
            DeepExploreMode: 创建的测试模式实例

        Raises:
            ValueError: 当传入不支持的模式类型时
        """
        if mode_type == "random_scenario":
            return DeepExploreRandomScenarioMode(
                deep_explore_object, stop_criteria_list, test_objects)

        elif mode_type == "sequence_scenario":
            reverse = kwargs.get('reverse', False)
            return DeepExploreSequenceScenarioMode(
                deep_explore_object, stop_criteria_list, test_objects, reverse)

        elif mode_type == "random_action":
            return DeepExploreRandomActionMode(
                deep_explore_object, stop_criteria_list, test_objects)

        elif mode_type == "sequence_action":
            reverse = kwargs.get('reverse', False)
            return DeepExploreSequenceActionMode(
                deep_explore_object, stop_criteria_list, test_objects, reverse)
        else:
            raise ValueError(f"Unsupported mode type: {mode_type}")
