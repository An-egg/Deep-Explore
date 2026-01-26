"""Utility functions for DeepExplore."""

import ast
import importlib
import inspect
from typing import Callable


class DeepExploreUtil:
    """Test exploration parameter resolution utility class.

    Provides dynamic resolution functionality for placeholder parameters.
    """

    @staticmethod
    def resolve_args(
            deep_explore_object,
            args,
            placeholder_prefix="_resolver_"
    ):
        """Recursively resolve placeholders in parameter list, supports multi-level nested dict/list/tuple structures.

        Args:
            deep_explore_object: Test object providing resolution methods
            args: Parameters to resolve (supports nested structures)
            placeholder_prefix: Placeholder prefix

        Returns:
            Resolved data structure (maintains original nesting structure)
        """

        def resolve_recursive(item):
            """Recursively resolve single element."""
            # 1. Handle string type placeholders
            if isinstance(item, str):
                if item.startswith(placeholder_prefix):
                    method_name = item[len(placeholder_prefix):]
                    if "=" in method_name:
                        tmp = method_name.split("=")
                        arg_name = tmp[0]
                        method_name = tmp[1]
                        result = (arg_name, deep_explore_object.arg_resolver(
                            method_name))
                    else:
                        result = deep_explore_object.arg_resolver(method_name)
                    return result
                else:
                    if "=" in item:
                        tmp = item.split("=")
                        item = (tmp[0], ast.literal_eval(tmp[1]))
                    return item

            # 2. Handle dictionary type: recursively resolve each value
            if isinstance(item, dict):
                return {k: resolve_recursive(v) for k, v in item.items()}

            # 3. Handle list/tuple type: recursively resolve each element
            if isinstance(item, (list, tuple)):
                sequence_type = type(item)
                return sequence_type(resolve_recursive(elem) for elem in item)

            # 4. Basic types return directly
            return item

        # Main resolution process
        resolved_args = resolve_recursive(args)
        return resolved_args

    @staticmethod
    def dynamic_import(path) -> Callable:
        """Dynamically import class object or method from specified class path.

        Args:
            path: Full path string of the class (format: "module.submodule.ClassName")

        Returns:
            object: Imported class object or method path

        Raises:
            ImportError: When module or class does not exist
            AttributeError: When specified class does not exist in module
        """
        try:
            # Split module path and class name
            pre_path, end_path = path.rsplit(".", 1)
            try:
                mod = importlib.import_module(pre_path)
                return getattr(mod, end_path)
            except Exception:
                mod_path, class_name = pre_path.rsplit(".", 1)
                mod = importlib.import_module(mod_path)
                cls = getattr(mod, class_name)
                return getattr(cls, end_path)
        except Exception as e:
            raise Exception(f"Dynamic import failed for {path}: {e}")

    @staticmethod
    def validate(config, resolver_class):
        errors = []

        # 1. Pre-get all valid resolver method names
        valid_resolvers = set()
        for name, _ in inspect.getmembers(
                resolver_class, predicate=inspect.isroutine):
            if name.startswith("_resolver_"):
                valid_resolvers.add(name)
            else:
                valid_resolvers.add(f"_resolver_{name}")

        # 2. Basic structure validation
        if not isinstance(config, dict):
            return ["YAML content must be Mapping structure"]

        mode = config.get("mode_type", "")

        # 3. Dispatch validation
        if "scenario" in mode:
            scenarios = config.get("scenario_list", [])
            for i, scenario in enumerate(scenarios):
                path = (f"scenario_list[{i}]"
                        f"({scenario.get('scenario_name', 'unknown')})")
                DeepExploreUtil._check_action_list(
                    scenario.get("action_list", []), path, valid_resolvers,
                    errors)
        elif "action" in mode:
            DeepExploreUtil._check_action_list(
                config.get("action_list", []), "action_list", valid_resolvers,
                errors)
        else:
            errors.append(f"Unknown mode_type: {mode}")

        return errors

    @staticmethod
    def _check_action_list(action_list, path, valid_resolvers, errors):
        if not isinstance(action_list, list):
            errors.append(f"[{path}] action_list must be a list")
            return
        for i, action in enumerate(action_list):
            act_path = (f"{path}.action[{i}]"
                        f"({action.get('action_name', 'unknown')})")
            DeepExploreUtil._validate_single_action(action, act_path,
                                                    valid_resolvers, errors)

    @staticmethod
    def _validate_single_action(action, path, valid_resolvers, errors):
        client_path = action.get("action_public_client", "")
        if client_path and not client_path.startswith("hours"):
            client_path = "hours.common.public." + client_path

        method_name = action.get("action_name")
        args = action.get("action_args", [])

        # 1. Validate Client import
        client_cls = None
        try:
            # Compatible with module.class structure
            client_cls = DeepExploreUtil.dynamic_import(client_path)
        except Exception as e:
            errors.append(f"[{path}] Client loading failed: {str(e)}")

        # 2. Validate method
        if client_cls and method_name:
            if not hasattr(client_cls, method_name):
                errors.append(f"[{path}] Method not found in class: {method_name}")
            else:
                DeepExploreUtil._check_resolvers_in_args(
                    args, path, valid_resolvers, errors)
                DeepExploreUtil._check_arg_count(
                    getattr(client_cls, method_name), args, path, errors)

        # 3. Validate Hook
        for hook_key in ["action_pre_check_list", "action_post_check_list"]:
            for j, hook in enumerate(action.get(hook_key, []) or []):
                info = hook.get("check_info", [])
                if info and isinstance(info[0], str):
                    try:
                        DeepExploreUtil.dynamic_import(info[0])
                    except Exception as e:
                        errors.append(
                            f"[{path}.{hook_key}[{j}]] Path unreachable: {info[0]},{e}")

    @staticmethod
    def _check_resolvers_in_args(args, path, valid_resolvers, errors):
        """Supports multiple Resolver formats:
        1. _resolver_get_id
        2. _resolver_get_volume_ids_args_1
        3. _resolver_vm_id=get_id
        """
        if isinstance(args, list):
            for item in args:
                DeepExploreUtil._check_resolvers_in_args(
                    item, path, valid_resolvers, errors)
        elif isinstance(args, dict):
            for v in args.values():
                DeepExploreUtil._check_resolvers_in_args(
                    v, path, valid_resolvers, errors)
        elif isinstance(args, str) and "_resolver_" in args:
            # Extract actual resolver method name
            actual_name = DeepExploreUtil._extract_resolver_name(args)
            if actual_name not in valid_resolvers:
                errors.append(
                    f"[{path}] Used undefined resolver: {args} (resolved as: {actual_name})")

    @staticmethod
    def _extract_resolver_name(s: str) -> str:
        """Extract corresponding Python Resolver method name from complex YAML string."""
        # Case A: _resolver_vm_id=get_id -> take get_id and complete prefix
        if "=" in s:
            # Assume format is key=_resolver_method or _resolver_key=method
            parts = s.split("=")
            # Find the part containing _resolver_, or if neither has it, usually the right side is the method
            target = parts[1] if "_resolver_" not in parts[1] else parts[1]
            if not target.startswith("_resolver_"):
                target = "_resolver_" + target
            return target

        # Case B: _resolver_get_volume_ids_args_1 -> truncate after _args_
        if "_args_" in s:
            return s.split("_args_")[0]

        # Case C: Normal format
        return s

    @staticmethod
    def _check_arg_count(method, provided_args, path, errors):
        try:
            sig = inspect.signature(method)
            # Filter out self / cls
            params = [p for p in sig.parameters.values() if
                      p.name not in ('self', 'cls')]

            # Calculate minimum required parameters (no default value, and not *args/**kwargs)
            min_required = sum(
                1 for p in params
                if p.default == inspect.Parameter.empty
                and p.kind not in (inspect.Parameter.VAR_POSITIONAL,
                                   inspect.Parameter.VAR_KEYWORD)
            )

            # Check if *args exists
            has_varargs = any(
                p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)

            # Maximum parameter count: if no *args, it's normal parameter count; otherwise unlimited
            if has_varargs:
                max_allowed = float('inf')  # Represents unlimited
            else:
                # Only count positional and keyword parameters (excluding *args/**kwargs)
                max_allowed = sum(
                    1 for p in params
                    if p.kind in (
                        inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        inspect.Parameter.KEYWORD_ONLY
                    )
                )

            arg_count = len(provided_args) if isinstance(
                provided_args, (list, tuple)) else 0

            if arg_count < min_required:
                errors.append(
                    f"[{path}] Insufficient parameters: need at least {min_required}, actual {arg_count}"
                )
            elif not has_varargs and arg_count > max_allowed:
                errors.append(
                    f"[{path}] Too many parameters: accept at most {max_allowed}, actual {arg_count}"
                )

        except Exception:
            # Optional: log, but don't silently pass (at least debug log)
            pass
