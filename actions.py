import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

from models import ActionResult, Task


logger = logging.getLogger(__name__)


class ActionStrategy(ABC):
    @abstractmethod
    def execute(self, task: Task) -> ActionResult:
        pass


class SyncAction(ActionStrategy):
    def execute(self, task: Task) -> ActionResult:
        logger.info(
            "Syncing data | user=%s | target=%s | params=%s",
            task.user,
            task.target,
            task.params,
        )

        return ActionResult(
            success=True,
            message=f"Sync completed for {task.target}",
        )


class BackupAction(ActionStrategy):
    def execute(self, task: Task) -> ActionResult:
        compression = task.params.get("compression", "none")

        logger.info(
            "Running backup | user=%s | target=%s | compression=%s",
            task.user,
            task.target,
            compression,
        )

        return ActionResult(
            success=True,
            message=f"Backup completed for {task.target}",
            metadata={
                "compression": compression,
            },
        )


class DeleteAction(ActionStrategy):
    def execute(self, task: Task) -> ActionResult:
        dry_run = task.params.get("dry_run", True)

        logger.warning(
            "Delete requested | user=%s | target=%s | dry_run=%s",
            task.user,
            task.target,
            dry_run,
        )

        if dry_run:
            return ActionResult(
                success=True,
                message=f"Delete skipped because dry_run=True for {task.target}",
            )

        return ActionResult(
            success=True,
            message=f"Delete completed for {task.target}",
        )


class ActionRegistry:
    def __init__(self):
        self._actions: Dict[str, ActionStrategy] = {}

    def register(self, name: str, strategy: ActionStrategy) -> None:
        self._actions[name] = strategy

    def get(self, name: str) -> Optional[ActionStrategy]:
        return self._actions.get(name)

    def list_actions(self) -> list[str]:
        return list(self._actions.keys())