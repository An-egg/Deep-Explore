"""Public client manager for DeepExplore."""

import importlib


class DeepExplorePublicManager:
    """Public client manager class, responsible for dynamically creating public client instances."""

    @staticmethod
    def create_public_client(
            public_client_absolute_path, *args, **kwargs):
        """Dynamically create corresponding client object based on given public client name.

        Args:
            public_client_absolute_path: Client prefix (default "hours.common.public.module.ClassName")

        Returns:
            object: Created public client instance

        Raises:
            ImportError: Module import failed
            AttributeError: Class name not found in module
        """
        full_module_path = ""
        class_name = ""
        try:
            module_name, class_name = public_client_absolute_path.rsplit('.', 1)

            # Dynamically import module
            module = importlib.import_module(module_name)

            # Get client class
            client_class = getattr(module, class_name)

            # Create instance and return
            return client_class(*args, **kwargs)

        except ImportError as e:
            raise ImportError(
                f"Failed to import module '{full_module_path}'") from e

        except AttributeError as e:
            raise AttributeError(
                f"Class '{class_name}' not found in module '{full_module_path}'"
            ) from e
