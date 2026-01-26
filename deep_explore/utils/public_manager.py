"""Public client manager for DeepExplore."""

import importlib


class DeepExplorePublicManager:
    """Public client manager class, responsible for dynamically creating public client instances."""

    @staticmethod
    def create_public_client(
            public_client_name, public_client_prefix):
        """Dynamically create corresponding client object based on given public client name.

        Args:
            public_client_name: Client name (e.g. "module.ClassName")
            public_client_prefix: Client prefix (default "hours.common.public")

        Returns:
            object: Created public client instance

        Raises:
            ImportError: Module import failed
            AttributeError: Class name not found in module
        """
        try:
            module_name, class_name = public_client_name.rsplit('.', 1)

            # Build complete module path
            full_module_path = f"{public_client_prefix}{module_name}"

            # Dynamically import module
            module = importlib.import_module(full_module_path)

            # Get client class
            client_class = getattr(module, class_name)

            # Create instance and return
            return client_class()

        except ImportError as e:
            raise ImportError(
                f"Failed to import module '{full_module_path}'") from e

        except AttributeError as e:
            raise AttributeError(
                f"Class '{class_name}' not found in module '{full_module_path}'"
            ) from e
