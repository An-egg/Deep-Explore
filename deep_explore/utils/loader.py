#  Copyright 2025 Leo John

import logging
import random
import string
import time

from ..core.action import DeepExploreAction
from ..core.action_check import DeepExploreActionCheck
from ..core.action_executor import DeepExploreActionExecutor
from ..core.mode import DeepExploreModeFactory
from ..core.precondition import DeepExplorePreconditionFactory
from ..core.scenario import DeepExploreScenario
from ..core.stopping_criteria import DeepExploreStoppingCriteriaFactory

logger = logging.getLogger(__name__)


class DeepExploreLoader:
    """
    测试探索加载器
    """
    MODE_LOADERS = {
        "scenario": "_load_scenario_mode",
        "action": "_load_action_mode"
    }

    @staticmethod
    def load_deep_explore_mode(deep_explore_obj, deep_explore_info):
        mode_type = deep_explore_info["mode_type"]
        logger.info(f"Loading deep explore mode: {mode_type}")
        loader_key = next((key for key in DeepExploreLoader.MODE_LOADERS
                           if key in mode_type), None)

        if loader_key:
            loader_method = getattr(DeepExploreLoader,
                                    DeepExploreLoader.MODE_LOADERS[loader_key])
            return loader_method(deep_explore_obj, deep_explore_info)
        raise ValueError(f"Unsupported mode type: {mode_type}")

    @staticmethod
    def _load_stopping_criteria(stopping_criteria_configs):
        return [
            DeepExploreStoppingCriteriaFactory.create(**config)
            for config in stopping_criteria_configs
        ]

    @staticmethod
    def _load_preconditions(precondition_configs):
        preconditions = []
        for config in precondition_configs:
            args = [config["precondition_type"], config["precondition_data"]]
            if "compare_result" in config:
                args.append(config["compare_result"])
            preconditions.append(DeepExplorePreconditionFactory.create(*args))
        return preconditions

    @staticmethod
    def _load_action_checks(deep_explore_obj, check_configs):
        return [
            DeepExploreActionCheck(
                deep_explore_object=deep_explore_obj,
                check_info=config["check_info"],
                check_result=config["check_result"]
            )
            for config in check_configs
        ]

    @staticmethod
    def _load_action_from_conf(deep_explore_obj, action_conf):
        action_id = action_conf.get("action_id", "")
        if action_id == "":
            random_str = "".join(random.choices(string.ascii_lowercase,k=6))
            timestamp = str(int(time.time() * 1000))
            action_id = random_str + timestamp
        executor = DeepExploreActionExecutor(
            action_id=action_id,
            action_name=action_conf["action_name"],
            action_public_client=action_conf["action_public_client"],
            action_exec_user=action_conf.get("action_exec_user", "admin_login"),
            except_meet_exception=action_conf.get(
                "except_meet_exception", False),
            action_args=action_conf["action_args"]
        )

        preconditions = DeepExploreLoader._load_preconditions(
            action_conf.get("action_precondition_list", [])
        )

        pre_checks = DeepExploreLoader._load_action_checks(
            deep_explore_obj,
            action_conf.get("action_pre_check_list", [])
        )

        post_checks = DeepExploreLoader._load_action_checks(
            deep_explore_obj,
            action_conf.get("action_post_check_list", [])
        )

        return DeepExploreAction(
            action_executor=executor,
            preconditions=preconditions,
            pre_checks=pre_checks,
            post_checks=post_checks,
            update_positions=action_conf.get("update_positions", ["end"])
        )

    @staticmethod
    def _load_action_mode(deep_explore_obj, deep_explore_info):
        logger.info("load action mode")
        stop_criteria_list = DeepExploreLoader._load_stopping_criteria(
            deep_explore_info["stopping_criteria_list"]
        )

        logger.info(f"Loading {len(deep_explore_info['action_list'])} actions")
        actions = [
            DeepExploreLoader._load_action_from_conf(deep_explore_obj, conf)
            for conf in deep_explore_info["action_list"]
        ]
        logger.info(f"Successfully loaded {len(actions)} actions")

        mode = DeepExploreModeFactory.create_mode(
            mode_type=deep_explore_info["mode_type"],
            deep_explore_object=deep_explore_obj,
            stop_criteria_list=stop_criteria_list,
            test_objects=actions
        )
        logger.info("Successfully created action mode")
        return mode

    @staticmethod
    def _load_scenario_mode(deep_explore_obj, deep_explore_info):
        logger.info("load scenario mode")
        stop_criteria_list = DeepExploreLoader._load_stopping_criteria(
            deep_explore_info["stopping_criteria_list"]
        )

        logger.info(f"Loading "
                    f"{len(deep_explore_info['scenario_list'])} scenarios")
        scenarios = []
        for scenario_conf in deep_explore_info["scenario_list"]:
            preconditions = DeepExploreLoader._load_preconditions(
                scenario_conf.get("scenario_precondition_list", [])
            )

            actions = [
                DeepExploreLoader._load_action_from_conf(
                    deep_explore_obj, action_conf)
                for action_conf in scenario_conf["action_list"]
            ]

            scenarios.append(DeepExploreScenario(
                scenario_name=scenario_conf["scenario_name"],
                preconditions=preconditions,
                actions=actions
            ))

        kwargs = deep_explore_info.get("kwargs", {})
        mode = DeepExploreModeFactory.create_mode(
            mode_type=deep_explore_info["mode_type"],
            deep_explore_object=deep_explore_obj,
            stop_criteria_list=stop_criteria_list,
            test_objects=scenarios,
            **kwargs
        )
        logger.info("Successfully created scenario mode")
        return mode
