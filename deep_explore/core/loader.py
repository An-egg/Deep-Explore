#  Copyright 2025 Leo John

import logging
import random
import string
import time

from . import DeepExploreAction
from . import DeepExploreActionCheck
from . import DeepExploreActionExecutor
from . import DeepExploreScenario
from .mode import DeepExploreModeFactory
from .precondition import DeepExplorePreconditionFactory
from .stopping_criteria import DeepExploreStoppingCriteriaFactory
from ..utils.util import DeepExploreUtil

logger = logging.getLogger(__name__)


class DeepExploreLoader:
    """Test exploration loader.

    Loads configuration and creates test exploration mode instances.
    Optionally validates configuration before loading to catch errors early.

    Example::

        from deep_explore import DeepExploreLoader

        # With validation (recommended for YAML-loaded configs)
        mode = DeepExploreLoader.load_deep_explore_mode(
            obj, config, validate=True)

        # Without validation (when using class references directly)
        mode = DeepExploreLoader.load_deep_explore_mode(obj, config)
    """

    @staticmethod
    def load_deep_explore_mode(deep_explore_obj, deep_explore_info,
                               validate=False):
        """Load and create a test exploration mode from configuration.

        Args:
            deep_explore_obj: Test exploration target object.
            deep_explore_info: Configuration dictionary containing mode settings.
            validate: If True, validate configuration before loading.
                Errors are logged as warnings; set strict=True to raise.

        Returns:
            DeepExploreMode: Created test mode instance.

        Raises:
            ValueError: When an unsupported mode type is provided,
                or when strict validation fails.
        """
        mode_type = deep_explore_info["mode_type"]
        logger.info(f"Loading deep explore mode: {mode_type}")

        if validate:
            errors = DeepExploreUtil.validate(
                deep_explore_info, type(deep_explore_obj))
            if errors:
                logger.warning(
                    f"Configuration validation found {len(errors)} "
                    f"issue(s):")
                for error in errors:
                    logger.warning(f"  - {error}")

        if "scenario" in mode_type:
            return DeepExploreLoader._load_scenario_mode(
                deep_explore_obj, deep_explore_info)
        raise ValueError(f"Unsupported mode type: {mode_type}")

    @staticmethod
    def _load_stopping_criteria(stopping_criteria_configs):
        """Load stopping criteria from configuration list.

        Args:
            stopping_criteria_configs: List of stopping criteria configurations.

        Returns:
            list: List of DeepExploreStoppingCriteria instances.
        """
        return [
            DeepExploreStoppingCriteriaFactory.create(**config)
            for config in stopping_criteria_configs
        ]

    @staticmethod
    def _load_preconditions(deep_explore_obj, precondition_configs):
        """Load preconditions from configuration list.

        Args:
            deep_explore_obj: Test exploration target object.
            precondition_configs: List of precondition configurations.

        Returns:
            list: List of DeepExplorePrecondition instances.
        """
        preconditions = []
        for config in precondition_configs:
            precondition_data = config["precondition_data"]

            if config["precondition_type"] == "function":
                precondition_data = DeepExploreActionCheck(
                    deep_explore_obj, *config["precondition_data"])
            args = [config["precondition_type"], precondition_data]
            if "compare_result" in config:
                args.append(config["compare_result"])

            preconditions.append(DeepExplorePreconditionFactory.create(*args))
        return preconditions

    @staticmethod
    def _load_action_checks(deep_explore_obj, check_configs):
        """Load action checks from configuration list.

        Args:
            deep_explore_obj: Test exploration target object.
            check_configs: List of check configurations.

        Returns:
            list: List of DeepExploreActionCheck instances.
        """
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
        """Load a single action from configuration.

        Args:
            deep_explore_obj: Test exploration target object.
            action_conf: Action configuration dictionary.

        Returns:
            DeepExploreAction: Created action instance.
        """
        action_id = action_conf.get("action_id", "")
        if action_id == "":
            random_str = "".join(random.choices(string.ascii_lowercase, k=6))
            timestamp = str(int(time.time() * 1000))
            action_id = random_str + timestamp
        executor = DeepExploreActionExecutor(
            action_id=action_id,
            action_name=action_conf["action_name"],
            action_public_client=action_conf["action_public_client"],
            except_meet_exception=action_conf.get(
                "except_meet_exception", False),
            action_args=action_conf["action_args"],
            timeout=action_conf.get("timeout")
        )

        preconditions = DeepExploreLoader._load_preconditions(
            deep_explore_obj, action_conf.get("action_precondition_list", [])
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
    def _load_scenario_mode(deep_explore_obj, deep_explore_info):
        """Load scenario mode from configuration.

        Args:
            deep_explore_obj: Test exploration target object.
            deep_explore_info: Configuration dictionary for scenario mode.

        Returns:
            DeepExploreMode: Created scenario mode instance.
        """
        logger.info("load scenario mode")
        stop_criteria_list = DeepExploreLoader._load_stopping_criteria(
            deep_explore_info["stopping_criteria_list"]
        )

        logger.info(f"Loading "
                    f"{len(deep_explore_info['scenario_list'])} scenarios")
        scenarios = []
        for scenario_conf in deep_explore_info["scenario_list"]:
            preconditions = DeepExploreLoader._load_preconditions(
                deep_explore_obj, scenario_conf.get(
                    "scenario_precondition_list", [])
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
