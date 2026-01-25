"""Utility functions for DeepExplore."""

import ast
import importlib
import inspect
from typing import Callable, Any


class DeepExploreUtil:
    """
    测试探索参数解析工具类

    提供占位符参数的动态解析功能
    """

    @staticmethod
    def resolve_args(
            deep_explore_object,
            args,
            placeholder_prefix="_resolver_"
    ):
        """
        递归解析参数列表中的占位符，支持多层嵌套的字典/列表/元组结构

        Args:
            deep_explore_object: 提供解析方法的测试对象
            args: 待解析的参数(支持嵌套结构)
            placeholder_prefix: 占位符前缀

        Returns:
            解析后的数据结构（保持原始嵌套结构）
        """

        def resolve_recursive(item):
            """递归解析单个元素"""
            # 1. 处理字符串类型的占位符
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

            # 2. 处理字典类型：递归解析每个value
            if isinstance(item, dict):
                return {k: resolve_recursive(v) for k, v in item.items()}

            # 3. 处理列表/元组类型：递归解析每个元素
            if isinstance(item, (list, tuple)):
                sequence_type = type(item)
                return sequence_type(resolve_recursive(elem) for elem in item)

            # 4. 基础类型直接返回
            return item

        # 主解析流程
        resolved_args = resolve_recursive(args)
        return resolved_args

    @staticmethod
    def dynamic_import(path) -> Callable:
        """
        动态导入指定类路径的类对象或方法

        Args:
            path: 类的完整路径字符串 (格式: "module.submodule.ClassName")

        Returns:
            object: 导入的类对象或方法路径

        Raises:
            ImportError: 当模块或类不存在时
            AttributeError: 当模块中不存在指定类时
        """
        try:
            # 分割模块路径和类名
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

        # 1. 预先获取所有合法的 resolver 方法名
        valid_resolvers = set()
        for name, _ in inspect.getmembers(
                resolver_class, predicate=inspect.isroutine):
            if name.startswith("_resolver_"):
                valid_resolvers.add(name)
            else:
                valid_resolvers.add(f"_resolver_{name}")

        # 2. 基本结构校验
        if not isinstance(config, dict):
            return ["YAML 内容必须是 Mapping 结构"]

        mode = config.get("mode_type", "")

        # 3. 分发校验
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
            errors.append(f"未知的 mode_type: {mode}")

        return errors

    @staticmethod
    def _check_action_list(action_list, path, valid_resolvers, errors):
        if not isinstance(action_list, list):
            errors.append(f"[{path}] action_list 必须是列表")
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

        # 1. 校验 Client 导入
        client_cls = None
        try:
            # 兼容模块.类 的结构
            client_cls = DeepExploreUtil.dynamic_import(client_path)
        except Exception as e:
            errors.append(f"[{path}] Client加载失败: {str(e)}")

        # 2. 校验方法
        if client_cls and method_name:
            if not hasattr(client_cls, method_name):
                errors.append(f"[{path}] 类中找不到方法: {method_name}")
            else:
                DeepExploreUtil._check_resolvers_in_args(
                    args, path, valid_resolvers, errors)
                DeepExploreUtil._check_arg_count(
                    getattr(client_cls, method_name), args, path, errors)

        # 3. 校验 Hook
        for hook_key in ["action_pre_check_list", "action_post_check_list"]:
            for j, hook in enumerate(action.get(hook_key, []) or []):
                info = hook.get("check_info", [])
                if info and isinstance(info[0], str):
                    try:
                        DeepExploreUtil.dynamic_import(info[0])
                    except Exception as e:
                        errors.append(
                            f"[{path}.{hook_key}[{j}]] 路径不可达: {info[0]},{e}")

    @staticmethod
    def _check_resolvers_in_args(args, path, valid_resolvers, errors):
        """
        支持多种 Resolver 格式：
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
            # 提取真正的 resolver 方法名
            actual_name = DeepExploreUtil._extract_resolver_name(args)
            if actual_name not in valid_resolvers:
                errors.append(
                    f"[{path}] 使用了未定义的解析器: {args} (解析为: {actual_name})")

    @staticmethod
    def _extract_resolver_name(s: str) -> str:
        """
        从复杂的 YAML 字符串中提取对应的 Python Resolver 方法名
        """
        # 情况 A: _resolver_vm_id=get_id -> 取 get_id 并补全前缀
        if "=" in s:
            # 假设格式是 key=_resolver_method 或 _resolver_key=method
            parts = s.split("=")
            # 找到包含 _resolver_ 的那部分，或者如果都不带，通常右边是方法
            target = parts[1] if "_resolver_" not in parts[1] else parts[1]
            if not target.startswith("_resolver_"):
                target = "_resolver_" + target
            return target

        # 情况 B: _resolver_get_volume_ids_args_1 -> 截断 _args_ 之后的部分
        if "_args_" in s:
            return s.split("_args_")[0]

        # 情况 C: 普通格式
        return s

    @staticmethod
    def _check_arg_count(method, provided_args, path, errors):
        try:
            sig = inspect.signature(method)
            # 过滤掉 self / cls
            params = [p for p in sig.parameters.values() if
                      p.name not in ('self', 'cls')]

            # 计算最小必需参数（无默认值，且不是 *args/**kwargs）
            min_required = sum(
                1 for p in params
                if p.default == inspect.Parameter.empty
                and p.kind not in (inspect.Parameter.VAR_POSITIONAL,
                                   inspect.Parameter.VAR_KEYWORD)
            )

            # 检查是否存在 *args
            has_varargs = any(
                p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)

            # 最大参数数：如果没有 *args，则为普通参数数量；否则不限制
            if has_varargs:
                max_allowed = float('inf')  # 表示无限
            else:
                # 只计算位置参数和关键字参数（不含 *args/**kwargs）
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
                    f"[{path}] 参数不足: 需要至少 {min_required}, 实际 {arg_count}"
                )
            elif not has_varargs and arg_count > max_allowed:
                errors.append(
                    f"[{path}] 参数过多: 最多接受 {max_allowed}, 实际 {arg_count}"
                )

        except Exception:
            # 可选：记录日志，但不要静默 pass（至少 debug log）
            pass
