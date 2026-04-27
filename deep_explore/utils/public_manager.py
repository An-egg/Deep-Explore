"""Public client manager for DeepExplore."""

import importlib


class DeepExplorePublicManager:
    """Public client manager class, responsible for dynamically creating
    public client instances from fully qualified class paths.

    Example::

        from deep_explore import DeepExplorePublicManager

        client = DeepExplorePublicManager.create_public_client(
            "my_package.my_module.MyClient", arg1, arg2)
    """

    @staticmethod
    def create_public_client(
            public_client_absolute_path, *args, **kwargs):
        """Dynamically create a client object from a fully qualified path.

        Args:
            public_client_absolute_path: Fully qualified class path
                (format: "package.module.ClassName").
            *args: Positional arguments passed to the class constructor.
            **kwargs: Keyword arguments passed to the class constructor.

        Returns:
            object: Created public client instance.

        Raises:
            ImportError: Module import failed.
            AttributeError: Class name not found in module.
        """
        module_name = ""
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
                f"Failed to import module '{module_name}'") from e

        except AttributeError as e:
            raise AttributeError(
                f"Class '{class_name}' not found in module '{module_name}'"
            ) from e
