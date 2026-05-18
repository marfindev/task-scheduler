import logging

from actions import ActionRegistry
from models import Task
from quota import InMemoryQuotaStore


logger = logging.getLogger(__name__)


class TaskExecutor:
    def __init__(
        self,
        quota_store: InMemoryQuotaStore,
        action_registry: ActionRegistry,
    ):
        self.quota_store = quota_store
        self.action_registry = action_registry

    def execute(self, task: Task) -> bool:
        logger.info(
            "Preparing task execution | task_id=%s | user=%s | action=%s",
            task.id,
            task.user,
            task.action,
        )

        strategy = self.action_registry.get(task.action)

        if strategy is None:
            logger.error(
                "Unsupported action | task_id=%s | action=%s",
                task.id,
                task.action,
            )
            return False

        try:
            quota_reserved = self.quota_store.try_reserve(task.user)

            if not quota_reserved:
                logger.warning(
                    "Quota exceeded | task_id=%s | user=%s",
                    task.id,
                    task.user,
                )
                return False

        except KeyError:
            logger.error(
                "Unknown user | task_id=%s | user=%s",
                task.id,
                task.user,
            )
            return False

        try:
            result = strategy.execute(task)

            if not result.success:
                self.quota_store.release(task.user)

                logger.error(
                    "Task failed | task_id=%s | user=%s | message=%s",
                    task.id,
                    task.user,
                    result.message,
                )
                return False

            logger.info(
                "Task completed | task_id=%s | user=%s | message=%s",
                task.id,
                task.user,
                result.message,
            )

            return True

        except Exception as exc:
            self.quota_store.release(task.user)

            logger.exception(
                "Unexpected task error | task_id=%s | user=%s | error=%s",
                task.id,
                task.user,
                str(exc),
            )

            return False