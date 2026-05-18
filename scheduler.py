import datetime
import logging
from typing import Optional

from executor import TaskExecutor
from repositories import InMemoryTaskRepository


logger = logging.getLogger(__name__)


class SimpleScheduler:
    def __init__(
        self,
        task_repository: InMemoryTaskRepository,
        executor: TaskExecutor,
    ):
        self.task_repository = task_repository
        self.executor = executor

    def run_pending(self, current_time: Optional[str] = None) -> int:
        """
        Menjalankan semua task yang waktunya sama dengan current_time.

        current_time dibuat injectable agar mudah dites.
        """

        if current_time is None:
            current_time = datetime.datetime.now().strftime("%H:%M")

        due_tasks = self.task_repository.get_due_tasks(current_time)

        logger.info(
            "Scheduler checked tasks | current_time=%s | due_tasks=%d",
            current_time,
            len(due_tasks),
        )

        success_count = 0

        for task in due_tasks:
            success = self.executor.execute(task)

            if success:
                success_count += 1

        logger.info(
            "Scheduler finished | current_time=%s | success=%d | total=%d",
            current_time,
            success_count,
            len(due_tasks),
        )

        return success_count