"""
Common mock clients and utilities for DeepExplore examples.

This module provides reusable mock clients and check functions
that can be shared across different example files.
"""

from typing import Any, Optional


class BaseMockClient:
    """Base class for mock clients.

    Provides common functionality for all mock clients.
    """

    @staticmethod
    def _log_action(action_name: str, **kwargs):
        """Log an action execution.

        Args:
            action_name: Name of the action being executed.
            **kwargs: Action parameters.
        """
        params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        print(f"  [Action] {action_name}: {params}")


class ResourceClient(BaseMockClient):
    """Mock client for resource management operations.

    Simulates a resource with states: available -> running -> stopped.
    """

    @staticmethod
    def start_resource(resource_id: str) -> Optional[Any]:
        """Start a resource.

        Args:
            resource_id: The ID of the resource to start.

        Returns:
            None
        """
        ResourceClient._log_action("Starting resource", resource_id=resource_id)
        return None

    @staticmethod
    def stop_resource(resource_id: str) -> Optional[Any]:
        """Stop a resource.

        Args:
            resource_id: The ID of the resource to stop.

        Returns:
            None
        """
        ResourceClient._log_action("Stopping resource", resource_id=resource_id)
        return None

    @staticmethod
    def restart_resource(resource_id: str) -> Optional[Any]:
        """Restart a resource.

        Args:
            resource_id: The ID of the resource to restart.

        Returns:
            None
        """
        ResourceClient._log_action("Restarting resource", resource_id=resource_id)
        return None


class VMClient(BaseMockClient):
    """Mock client for VM management operations.

    Simulates a VM with lifecycle states:
    available -> creating -> running -> stopping -> stopped -> deleting.
    """

    @staticmethod
    def create_vm(vm_name: str, flavor: str, image: str) -> str:
        """Create a new VM.

        Args:
            vm_name: Name of the VM.
            flavor: VM flavor/size.
            image: OS image to use.

        Returns:
            str: Created VM ID.
        """
        vm_id = f"vm-{vm_name}"
        VMClient._log_action("Creating VM", vm_name=vm_name, flavor=flavor, image=image)
        return vm_id

    @staticmethod
    def start_vm(vm_id: str) -> Optional[Any]:
        """Start a VM.

        Args:
            vm_id: The VM ID to start.

        Returns:
            None
        """
        VMClient._log_action("Starting VM", vm_id=vm_id)
        return None

    @staticmethod
    def stop_vm(vm_id: str) -> Optional[Any]:
        """Stop a VM.

        Args:
            vm_id: The VM ID to stop.

        Returns:
            None
        """
        VMClient._log_action("Stopping VM", vm_id=vm_id)
        return None

    @staticmethod
    def delete_vm(vm_id: str) -> Optional[Any]:
        """Delete a VM.

        Args:
            vm_id: The VM ID to delete.

        Returns:
            None
        """
        VMClient._log_action("Deleting VM", vm_id=vm_id)
        return None


class TaskClient(BaseMockClient):
    """Mock client for task management operations.

    Simulates a task queue with states: pending -> processing -> completed -> failed.
    """

    @staticmethod
    def process_task(task_id: str) -> Optional[Any]:
        """Process a task.

        Args:
            task_id: The task ID to process.

        Returns:
            None
        """
        TaskClient._log_action("Processing task", task_id=task_id)
        return None

    @staticmethod
    def retry_task(task_id: str) -> Optional[Any]:
        """Retry a failed task.

        Args:
            task_id: The task ID to retry.

        Returns:
            None
        """
        TaskClient._log_action("Retrying task", task_id=task_id)
        return None

    @staticmethod
    def complete_task(task_id: str) -> Optional[Any]:
        """Mark a task as completed.

        Args:
            task_id: The task ID to complete.

        Returns:
            None
        """
        TaskClient._log_action("Completing task", task_id=task_id)
        return None


class DatabaseClient(BaseMockClient):
    """Mock client for database management operations.

    Simulates a database instance with detailed state information.
    """

    @staticmethod
    def create_database(db_name: str, engine: str, version: str, size: int) -> str:
        """Create a new database.

        Args:
            db_name: Name of the database.
            engine: Database engine (mysql, postgresql, etc.).
            version: Database version.
            size: Database size in GB.

        Returns:
            str: Created database ID.
        """
        db_id = f"db-{db_name}"
        DatabaseClient._log_action(
            "Creating database",
            db_name=db_name,
            engine=engine,
            version=version,
            size=f"{size}GB"
        )
        return db_id

    @staticmethod
    def scale_database(db_id: str, new_size: int) -> Optional[Any]:
        """Scale a database.

        Args:
            db_id: The database ID to scale.
            new_size: New size in GB.

        Returns:
            None
        """
        DatabaseClient._log_action("Scaling database", db_id=db_id, new_size=f"{new_size}GB")
        return None

    @staticmethod
    def add_replica(db_id: str) -> Optional[Any]:
        """Add a replica to the database.

        Args:
            db_id: The database ID.

        Returns:
            None
        """
        DatabaseClient._log_action("Adding replica", db_id=db_id)
        return None

    @staticmethod
    def delete_database(db_id: str) -> Optional[Any]:
        """Delete a database.

        Args:
            db_id: The database ID to delete.

        Returns:
            None
        """
        DatabaseClient._log_action("Deleting database", db_id=db_id)
        return None


# Common check functions
def check_resource_started(resource_id: str) -> bool:
    """Check if resource is started.

    Args:
        resource_id: The resource ID to check.

    Returns:
        bool: True if resource is started.
    """
    print(f"  [Check] Verifying resource {resource_id} is started")
    return True


def check_resource_stopped(resource_id: str) -> bool:
    """Check if resource is stopped.

    Args:
        resource_id: The resource ID to check.

    Returns:
        bool: True if resource is stopped.
    """
    print(f"  [Check] Verifying resource {resource_id} is stopped")
    return True


def check_vm_created(vm_id: str) -> bool:
    """Check if VM is created.

    Args:
        vm_id: The VM ID to check.

    Returns:
        bool: True if VM is created.
    """
    print(f"  [Check] Verifying VM {vm_id} is created")
    return True


def check_vm_running(vm_id: str) -> bool:
    """Check if VM is running.

    Args:
        vm_id: The VM ID to check.

    Returns:
        bool: True if VM is running.
    """
    print(f"  [Check] Verifying VM {vm_id} is running")
    return True


def check_vm_stopped(vm_id: str) -> bool:
    """Check if VM is stopped.

    Args:
        vm_id: The VM ID to check.

    Returns:
        bool: True if VM is stopped.
    """
    print(f"  [Check] Verifying VM {vm_id} is stopped")
    return True


def check_database_created(db_id: str) -> bool:
    """Check if database is created.

    Args:
        db_id: The database ID to check.

    Returns:
        bool: True if database is created.
    """
    print(f"  [Check] Verifying database {db_id} is created")
    return True


def check_database_scaled(db_id: str, expected_size: int) -> bool:
    """Check if database is scaled to expected size.

    Args:
        db_id: The database ID to check.
        expected_size: Expected size in GB.

    Returns:
        bool: True if database is scaled to expected size.
    """
    print(f"  [Check] Verifying database {db_id} is scaled to {expected_size}GB")
    return True


def check_high_priority(task_id: str) -> bool:
    """Check if task has high priority.

    Args:
        task_id: The task ID to check.

    Returns:
        bool: True if task has high priority.
    """
    print(f"  [Check] Verifying task {task_id} has high priority")
    return True
