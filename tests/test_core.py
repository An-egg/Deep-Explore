"""Tests for DeepExplore core module."""

import time

import pytest

from deep_explore import (
    DeepExploreObject,
    DeepExploreAction,
    DeepExploreActionCheck,
    DeepExploreActionExecutor,
    DeepExploreScenario,
    DeepExploreMode,
    DeepExploreRandomScenarioMode,
    DeepExploreSequenceScenarioMode,
    DeepExploreModeFactory,
    DeepExplorePrecondition,
    DeepExploreStatusPrecondition,
    DeepExplorePreconditionFactory,
    DeepExploreStoppingCriteria,
    DeepExploreStepStoppingCriteria,
    DeepExploreTimeStoppingCriteria,
    DeepExploreStoppingCriteriaFactory,
    DeepExploreLoader,
    DeepExploreHookManager,
    HookPoint,
)


class MockTestObject(DeepExploreObject):
    """Mock test object for testing."""

    def __init__(self):
        super().__init__()
        self.data = {"status": "idle", "name": "test"}
        self._status = "idle"

    def _do_update_state(self):
        pass

    def get_status(self) -> str:
        return self._status

    def set_status(self, status: str):
        self._status = status
        self.data["status"] = status

    def _resolver_test_id(self):
        return "id-123"


class TestDeepExploreModeABC:
    """Test that DeepExploreMode is abstract and cannot be instantiated directly."""

    def test_cannot_instantiate_base_class(self):
        with pytest.raises(TypeError):
            DeepExploreMode()

    def test_subclass_must_implement_exec_test(self):
        class IncompleteMode(DeepExploreMode):
            pass

        with pytest.raises(TypeError):
            IncompleteMode()


class TestDeepExploreModeFactory:
    """Test DeepExploreModeFactory."""

    def test_create_random_scenario_mode(self):
        obj = MockTestObject()
        stop_criteria = [DeepExploreStepStoppingCriteria(5)]
        scenarios = [DeepExploreScenario("test", [], [])]

        mode = DeepExploreModeFactory.create_mode(
            "random_scenario", obj, stop_criteria, scenarios)
        assert isinstance(mode, DeepExploreRandomScenarioMode)

    def test_create_sequence_scenario_mode(self):
        obj = MockTestObject()
        stop_criteria = [DeepExploreStepStoppingCriteria(5)]
        scenarios = [DeepExploreScenario("test", [], [])]

        mode = DeepExploreModeFactory.create_mode(
            "sequence_scenario", obj, stop_criteria, scenarios)
        assert isinstance(mode, DeepExploreSequenceScenarioMode)

    def test_create_sequence_scenario_mode_reverse(self):
        obj = MockTestObject()
        stop_criteria = [DeepExploreStepStoppingCriteria(5)]
        scenarios = [
            DeepExploreScenario("first", [], []),
            DeepExploreScenario("second", [], []),
        ]

        mode = DeepExploreModeFactory.create_mode(
            "sequence_scenario", obj, stop_criteria, scenarios, reverse=True)
        assert isinstance(mode, DeepExploreSequenceScenarioMode)
        assert mode.scenarios[0].scenario_name == "second"
        assert mode.scenarios[1].scenario_name == "first"

    def test_unsupported_mode_type_raises(self):
        obj = MockTestObject()
        stop_criteria = [DeepExploreStepStoppingCriteria(5)]
        scenarios = [DeepExploreScenario("test", [], [])]

        with pytest.raises(ValueError, match="Unsupported mode type"):
            DeepExploreModeFactory.create_mode(
                "random_action", obj, stop_criteria, scenarios)

    def test_action_mode_types_not_supported(self):
        """Verify that action modes are no longer supported."""
        obj = MockTestObject()
        stop_criteria = [DeepExploreStepStoppingCriteria(5)]
        actions = []

        with pytest.raises(ValueError, match="Unsupported mode type"):
            DeepExploreModeFactory.create_mode(
                "random_action", obj, stop_criteria, actions)

        with pytest.raises(ValueError, match="Unsupported mode type"):
            DeepExploreModeFactory.create_mode(
                "sequence_action", obj, stop_criteria, actions)


class TestDeepExploreModeInstanceIsolation:
    """Test that mode instances don't share class-level mutable state."""

    def test_instances_have_separate_already_exec_scenarios(self):
        obj = MockTestObject()
        stop_criteria = [DeepExploreStepStoppingCriteria(1)]
        scenarios = [DeepExploreScenario("test", [], [])]

        mode1 = DeepExploreRandomScenarioMode(obj, stop_criteria, scenarios)
        mode2 = DeepExploreRandomScenarioMode(obj, stop_criteria, scenarios)

        mode1.already_exec_scenarios.append({"test": []})
        assert len(mode1.already_exec_scenarios) == 1
        assert len(mode2.already_exec_scenarios) == 0

    def test_instances_have_separate_already_exec_actions(self):
        obj = MockTestObject()
        stop_criteria = [DeepExploreStepStoppingCriteria(1)]
        scenarios = [DeepExploreScenario("test", [], [])]

        mode1 = DeepExploreRandomScenarioMode(obj, stop_criteria, scenarios)
        mode2 = DeepExploreRandomScenarioMode(obj, stop_criteria, scenarios)

        mode1.already_exec_actions.append("action1")
        assert len(mode1.already_exec_actions) == 1
        assert len(mode2.already_exec_actions) == 0


class TestDeepExploreStoppingCriteria:
    """Test stopping criteria classes."""

    def test_step_stopping_criteria(self):
        criteria = DeepExploreStepStoppingCriteria(3)
        assert not criteria.is_matched()  # step 0
        assert not criteria.is_matched()  # step 1
        assert not criteria.is_matched()  # step 2
        assert criteria.is_matched()      # step 3 >= 3

    def test_time_stopping_criteria(self):
        criteria = DeepExploreTimeStoppingCriteria(0.0)
        assert criteria.is_matched()

    def test_end_time_stopping_criteria(self):
        with pytest.raises(Exception):
            DeepExploreEndTimeStoppingCriteria("invalid-format")

    def test_factory_step(self):
        criteria = DeepExploreStoppingCriteriaFactory.create(
            "step", max_steps=10)
        assert isinstance(criteria, DeepExploreStepStoppingCriteria)

    def test_factory_time(self):
        criteria = DeepExploreStoppingCriteriaFactory.create(
            "time", duration=60)
        assert isinstance(criteria, DeepExploreTimeStoppingCriteria)

    def test_factory_unsupported(self):
        with pytest.raises(ValueError, match="Unsupported criteria type"):
            DeepExploreStoppingCriteriaFactory.create("invalid")


class TestDeepExplorePrecondition:
    """Test precondition classes."""

    def test_status_precondition_matched(self):
        obj = MockTestObject()
        obj.set_status("running")
        precondition = DeepExploreStatusPrecondition(["running"], True)
        assert precondition.check_precondition(obj) is True

    def test_status_precondition_not_matched(self):
        obj = MockTestObject()
        obj.set_status("stopped")
        precondition = DeepExploreStatusPrecondition(["running"], True)
        assert precondition.check_precondition(obj) is False

    def test_status_precondition_negated(self):
        obj = MockTestObject()
        obj.set_status("stopped")
        precondition = DeepExploreStatusPrecondition(["running"], False)
        assert precondition.check_precondition(obj) is True

    def test_precondition_factory(self):
        precondition = DeepExplorePreconditionFactory.create(
            "status", ["running"], True)
        assert isinstance(precondition, DeepExploreStatusPrecondition)

    def test_precondition_factory_unsupported(self):
        with pytest.raises(ValueError, match="Unsupported precondition type"):
            DeepExplorePreconditionFactory.create("invalid", [])


class TestDeepExploreAction:
    """Test DeepExploreAction class."""

    def test_action_type_hints(self):
        """Verify action has proper type hints."""
        executor = DeepExploreActionExecutor(
            action_id="test-id",
            action_name="test_action",
            action_public_client=None,
            action_args=[]
        )
        action = DeepExploreAction(
            action_executor=executor,
            preconditions=[],
            pre_checks=[],
            post_checks=[],
        )
        assert isinstance(action.preconditions, list)
        assert isinstance(action.update_positions, list)
        assert action.update_positions == ["end"]

    def test_check_preconditions_empty(self):
        """Action with no preconditions should always pass."""
        executor = DeepExploreActionExecutor(
            action_id="test-id",
            action_name="test_action",
            action_public_client=None,
            action_args=[]
        )
        action = DeepExploreAction(
            action_executor=executor,
            preconditions=[],
        )
        obj = MockTestObject()
        assert action.check_preconditions(obj) is True


class TestDeepExploreScenario:
    """Test DeepExploreScenario class."""

    def test_scenario_creation(self):
        scenario = DeepExploreScenario("test_scenario", [], [])
        assert scenario.scenario_name == "test_scenario"
        assert scenario.preconditions == []
        assert scenario.actions == []

    def test_scenario_check_preconditions_empty(self):
        scenario = DeepExploreScenario("test_scenario", [], [])
        obj = MockTestObject()
        assert scenario.check_preconditions(obj) is True


class TestDeepExploreLoader:
    """Test DeepExploreLoader."""

    def test_loader_unsupported_mode(self):
        obj = MockTestObject()
        config = {"mode_type": "invalid_mode"}

        with pytest.raises(ValueError, match="Unsupported mode type"):
            DeepExploreLoader.load_deep_explore_mode(obj, config)

    def test_loader_no_action_mode(self):
        """Verify that action mode is no longer supported in loader."""
        obj = MockTestObject()
        config = {
            "mode_type": "random_action",
            "stopping_criteria_list": [],
            "action_list": []
        }

        with pytest.raises(ValueError, match="Unsupported mode type"):
            DeepExploreLoader.load_deep_explore_mode(obj, config)


class TestDeepExploreImports:
    """Test that all public API is importable."""

    def test_no_action_mode_exports(self):
        """Verify that action mode classes are no longer exported."""
        import deep_explore
        assert not hasattr(deep_explore, 'DeepExploreRandomActionMode')
        assert not hasattr(deep_explore, 'DeepExploreSequenceActionMode')

    def test_scenario_mode_exports(self):
        """Verify that scenario mode classes are exported."""
        import deep_explore
        assert hasattr(deep_explore, 'DeepExploreRandomScenarioMode')
        assert hasattr(deep_explore, 'DeepExploreSequenceScenarioMode')


# ============================================================================
# Tests for new features
# ============================================================================


class MockClient:
    """Mock client for action execution tests."""

    def __init__(self):
        self.call_count = 0

    def fast_action(self):
        self.call_count += 1
        return "ok"

    def slow_action(self):
        self.call_count += 1
        time.sleep(5)
        return "too_slow"

    def failing_action(self):
        self.call_count += 1
        raise RuntimeError("action failed")


class TestDeepExploreActionTimeout:
    """Test action timeout control."""

    def test_action_no_timeout(self):
        """Action without timeout should complete normally."""
        client = MockClient()
        executor = DeepExploreActionExecutor(
            action_id="test-id",
            action_name="fast_action",
            action_public_client=client,
            action_args=[]
        )
        obj = MockTestObject()
        result = executor.exec_action(obj)
        assert result == "ok"

    def test_action_timeout_not_exceeded(self):
        """Action that finishes within timeout should succeed."""
        client = MockClient()
        executor = DeepExploreActionExecutor(
            action_id="test-id",
            action_name="fast_action",
            action_public_client=client,
            action_args=[],
            timeout=10.0
        )
        obj = MockTestObject()
        result = executor.exec_action(obj)
        assert result == "ok"

    def test_action_timeout_exceeded(self):
        """Action that exceeds timeout should raise TimeoutError."""
        client = MockClient()
        executor = DeepExploreActionExecutor(
            action_id="test-id",
            action_name="slow_action",
            action_public_client=client,
            action_args=[],
            timeout=0.5
        )
        obj = MockTestObject()
        with pytest.raises(Exception, match="timed out"):
            executor.exec_action(obj)

    def test_action_timeout_default_none(self):
        """Default timeout should be None (no timeout)."""
        executor = DeepExploreActionExecutor(
            action_id="test-id",
            action_name="test",
            action_public_client=MockClient(),
            action_args=[]
        )
        assert executor.timeout is None


class TestDeepExploreHooks:
    """Test hook/lifecycle callback mechanism."""

    def setup_method(self):
        """Clear all hooks before each test."""
        DeepExploreHookManager.clear()

    def teardown_method(self):
        """Clear all hooks after each test."""
        DeepExploreHookManager.clear()

    def test_register_and_invoke(self):
        """Registered callback should be invoked."""
        results = []

        def callback(**kwargs):
            results.append(kwargs.get("scenario_name"))

        DeepExploreHookManager.register(
            HookPoint.BEFORE_SCENARIO, callback)
        DeepExploreHookManager.invoke(
            HookPoint.BEFORE_SCENARIO, scenario_name="test_scenario")

        assert results == ["test_scenario"]

    def test_multiple_callbacks_invoked_in_order(self):
        """Multiple callbacks should be invoked in registration order."""
        results = []

        DeepExploreHookManager.register(
            HookPoint.AFTER_ACTION,
            lambda **kw: results.append("first"))
        DeepExploreHookManager.register(
            HookPoint.AFTER_ACTION,
            lambda **kw: results.append("second"))

        DeepExploreHookManager.invoke(HookPoint.AFTER_ACTION)
        assert results == ["first", "second"]

    def test_unregister_callback(self):
        """Unregistered callback should not be invoked."""
        results = []

        def callback(**kwargs):
            results.append("called")

        DeepExploreHookManager.register(
            HookPoint.BEFORE_ACTION, callback)
        DeepExploreHookManager.unregister(
            HookPoint.BEFORE_ACTION, callback)
        DeepExploreHookManager.invoke(HookPoint.BEFORE_ACTION)

        assert results == []

    def test_unregister_nonexistent_returns_false(self):
        """Unregistering a non-existent callback returns False."""
        result = DeepExploreHookManager.unregister(
            HookPoint.BEFORE_SCENARIO, lambda: None)
        assert result is False

    def test_hook_exception_does_not_stop_others(self):
        """A failing callback should not prevent other callbacks."""
        results = []

        def bad_callback(**kwargs):
            raise RuntimeError("boom")

        def good_callback(**kwargs):
            results.append("good")

        DeepExploreHookManager.register(
            HookPoint.ON_ACTION_ERROR, bad_callback)
        DeepExploreHookManager.register(
            HookPoint.ON_ACTION_ERROR, good_callback)

        DeepExploreHookManager.invoke(HookPoint.ON_ACTION_ERROR)
        assert results == ["good"]

    def test_clear_specific_hook_point(self):
        """Clear with a specific hook point should only clear that point."""
        before_calls = []
        after_calls = []

        DeepExploreHookManager.register(
            HookPoint.BEFORE_SCENARIO,
            lambda **kw: before_calls.append(1))
        DeepExploreHookManager.register(
            HookPoint.AFTER_SCENARIO,
            lambda **kw: after_calls.append(1))

        DeepExploreHookManager.clear(HookPoint.BEFORE_SCENARIO)
        DeepExploreHookManager.invoke(HookPoint.BEFORE_SCENARIO)
        DeepExploreHookManager.invoke(HookPoint.AFTER_SCENARIO)

        assert before_calls == []
        assert after_calls == [1]

    def test_clear_all_hooks(self):
        """Clear without argument should clear all hooks."""
        DeepExploreHookManager.register(
            HookPoint.BEFORE_SCENARIO, lambda **kw: None)
        DeepExploreHookManager.register(
            HookPoint.AFTER_SCENARIO, lambda **kw: None)

        DeepExploreHookManager.clear()
        assert DeepExploreHookManager.get_registered(
            HookPoint.BEFORE_SCENARIO) == []
        assert DeepExploreHookManager.get_registered(
            HookPoint.AFTER_SCENARIO) == []

    def test_register_invalid_hook_point(self):
        """Registering with invalid hook point should raise TypeError."""
        with pytest.raises(TypeError):
            DeepExploreHookManager.register("not_a_hook", lambda: None)

    def test_register_non_callable(self):
        """Registering a non-callable should raise ValueError."""
        with pytest.raises(ValueError):
            DeepExploreHookManager.register(HookPoint.BEFORE_ACTION, "not_callable")

    def test_get_registered(self):
        """get_registered should return copy of callbacks list."""
        cb = lambda **kw: None
        DeepExploreHookManager.register(HookPoint.BEFORE_ACTION, cb)

        registered = DeepExploreHookManager.get_registered(
            HookPoint.BEFORE_ACTION)
        assert cb in registered
        # Verify it's a copy
        registered.clear()
        assert len(DeepExploreHookManager.get_registered(
            HookPoint.BEFORE_ACTION)) == 1

    def test_hooks_integrated_with_scenario_execution(self):
        """Hooks should be invoked during actual scenario execution."""
        events = []

        DeepExploreHookManager.register(
            HookPoint.BEFORE_SCENARIO,
            lambda **kw: events.append(
                f"before:{kw['scenario_name']}"))
        DeepExploreHookManager.register(
            HookPoint.AFTER_SCENARIO,
            lambda **kw: events.append(
                f"after:{kw['scenario_name']}:{kw['success']}"))

        obj = MockTestObject()
        obj.set_status("running")
        client = MockClient()
        executor = DeepExploreActionExecutor(
            action_id="test-id",
            action_name="fast_action",
            action_public_client=client,
            action_args=[]
        )
        action = DeepExploreAction(action_executor=executor)
        scenario = DeepExploreScenario("hook_test", [], [action])

        mode = DeepExploreRandomScenarioMode(
            obj, [DeepExploreStepStoppingCriteria(1)], [scenario])
        mode.exec_test()

        assert "before:hook_test" in events
        assert "after:hook_test:True" in events


class TestFactoryRegistration:
    """Test factory register/unregister for custom types."""

    def test_mode_factory_register_custom(self):
        """Custom mode type should be creatable after registration."""

        class CustomMode(DeepExploreMode):
            def __init__(self, obj, criteria, tests, **kwargs):
                super().__init__()
                self.custom_init = True

            def exec_test(self):
                pass

        DeepExploreModeFactory.register("custom_mode", CustomMode)
        try:
            obj = MockTestObject()
            criteria = [DeepExploreStepStoppingCriteria(1)]
            mode = DeepExploreModeFactory.create_mode(
                "custom_mode", obj, criteria, [])
            assert isinstance(mode, CustomMode)
            assert mode.custom_init is True
        finally:
            DeepExploreModeFactory.unregister("custom_mode")

    def test_mode_factory_register_duplicate_raises(self):
        """Registering the same type twice should raise ValueError."""

        class CustomMode(DeepExploreMode):
            def exec_test(self):
                pass

        DeepExploreModeFactory.register("dup_mode", CustomMode)
        try:
            with pytest.raises(ValueError, match="already registered"):
                DeepExploreModeFactory.register("dup_mode", CustomMode)
        finally:
            DeepExploreModeFactory.unregister("dup_mode")

    def test_mode_factory_register_invalid_class_raises(self):
        """Registering a non-DeepExploreMode class should raise TypeError."""
        with pytest.raises(TypeError, match="subclass of DeepExploreMode"):
            DeepExploreModeFactory.register("bad", str)

    def test_mode_factory_unregister(self):
        """Unregistered custom type should no longer be creatable."""

        class CustomMode(DeepExploreMode):
            def exec_test(self):
                pass

        DeepExploreModeFactory.register("temp_mode", CustomMode)
        result = DeepExploreModeFactory.unregister("temp_mode")
        assert result is True

        with pytest.raises(ValueError, match="Unsupported mode type"):
            DeepExploreModeFactory.create_mode(
                "temp_mode", MockTestObject(), [], [])

    def test_mode_factory_unregister_nonexistent(self):
        """Unregistering a non-existent type returns False."""
        result = DeepExploreModeFactory.unregister("nonexistent")
        assert result is False

    def test_stopping_criteria_factory_register_custom(self):
        """Custom stopping criteria should be creatable after registration."""

        class CustomCriteria(DeepExploreStoppingCriteria):
            def __init__(self, threshold=10, **kwargs):
                self.threshold = threshold

            def is_matched(self):
                return True

        DeepExploreStoppingCriteriaFactory.register("custom", CustomCriteria)
        try:
            criteria = DeepExploreStoppingCriteriaFactory.create(
                "custom", threshold=42)
            assert isinstance(criteria, CustomCriteria)
            assert criteria.threshold == 42
        finally:
            DeepExploreStoppingCriteriaFactory.unregister("custom")

    def test_stopping_criteria_register_invalid_raises(self):
        """Registering invalid class should raise TypeError."""
        with pytest.raises(TypeError, match="subclass"):
            DeepExploreStoppingCriteriaFactory.register("bad", dict)

    def test_precondition_factory_register_custom(self):
        """Custom precondition should be creatable after registration."""

        class CustomPrecondition(DeepExplorePrecondition):
            def __init__(self, data, compare_result=True):
                self.data = data
                self.compare_result = compare_result

            def check_precondition(self, obj):
                return self.compare_result

        DeepExplorePreconditionFactory.register("custom", CustomPrecondition)
        try:
            pre = DeepExplorePreconditionFactory.create(
                "custom", "some_data", True)
            assert isinstance(pre, CustomPrecondition)
        finally:
            DeepExplorePreconditionFactory.unregister("custom")

    def test_precondition_register_invalid_raises(self):
        """Registering invalid class should raise TypeError."""
        with pytest.raises(TypeError, match="subclass"):
            DeepExplorePreconditionFactory.register("bad", list)


class TestDeepExploreLoaderValidation:
    """Test Loader validate integration."""

    def test_loader_with_validate_flag(self):
        """Loader with validate=True should not crash on valid config."""
        obj = MockTestObject()
        config = {
            "mode_type": "random_scenario",
            "stopping_criteria_list": [
                {"criteria_type": "step", "max_steps": 1}
            ],
            "scenario_list": [
                {
                    "scenario_name": "test",
                    "action_list": [
                        {
                            "action_name": "fast_action",
                            "action_public_client": MockClient(),
                            "action_args": []
                        }
                    ]
                }
            ]
        }
        # Should not raise
        mode = DeepExploreLoader.load_deep_explore_mode(
            obj, config, validate=True)
        assert isinstance(mode, DeepExploreRandomScenarioMode)

    def test_loader_without_validate_flag(self):
        """Loader without validate should work as before."""
        obj = MockTestObject()
        config = {
            "mode_type": "random_scenario",
            "stopping_criteria_list": [
                {"criteria_type": "step", "max_steps": 1}
            ],
            "scenario_list": [
                {
                    "scenario_name": "test",
                    "action_list": [
                        {
                            "action_name": "fast_action",
                            "action_public_client": MockClient(),
                            "action_args": []
                        }
                    ]
                }
            ]
        }
        mode = DeepExploreLoader.load_deep_explore_mode(obj, config)
        assert isinstance(mode, DeepExploreRandomScenarioMode)


class TestDeepExplorePublicManager:
    """Test cleaned-up PublicManager."""

    def test_imports_are_available(self):
        """PublicManager should be importable from deep_explore."""
        from deep_explore import DeepExplorePublicManager
        assert DeepExplorePublicManager is not None

    def test_error_messages_use_correct_module_name(self):
        """Error messages should use the actual module name, not empty string."""
        from deep_explore import DeepExplorePublicManager

        with pytest.raises(ImportError, match="nonexistent_module"):
            DeepExplorePublicManager.create_public_client(
                "nonexistent_module.FakeClass")
