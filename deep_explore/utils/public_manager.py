"""Public client manager for DeepExplore."""

import importlib


class DeepExplorePublicManager:
    """公共客户端管理类，负责动态创建公共客户端实例"""

    @staticmethod
    def create_public_client(
            public_client_name, public_client_prefix="hours.common.public."):
        """
        根据给定的public客户端名称动态创建对应的客户端对象

        Args:
            public_client_name: 客户端名称 (e.g. "module.ClassName")
            public_client_prefix: 客户端前缀 (默认"hours.common.public")

        Returns:
            object: 创建的公共客户端实例

        Raises:
            ImportError: 模块导入失败
            AttributeError: 类名在模块中不存在
        """
        try:
            module_name, class_name = public_client_name.rsplit('.', 1)

            # 构建完整模块路径
            if public_client_name.startswith("hours"):
                public_client_prefix = ""
            full_module_path = f"{public_client_prefix}{module_name}"

            # 动态导入模块
            module = importlib.import_module(full_module_path)

            # 获取客户端类
            client_class = getattr(module, class_name)

            # 创建实例并返回
            return client_class()

        except ImportError as e:
            raise ImportError(
                f"Failed to import module '{full_module_path}'") from e

        except AttributeError as e:
            raise AttributeError(
                f"Class '{class_name}' not found in module '{full_module_path}'"
            ) from e
