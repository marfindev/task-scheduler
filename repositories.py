from typing import Iterable, List

from models import Task


class InMemoryTaskRepository:
    """
    Repository task berbasis memory.

    Untuk production:
    - ganti dengan PostgreSQL/MySQL
    - tambahkan index pada scheduled_time
    - tambahkan status task: pending, running, success, failed
    """

    def __init__(self, tasks: Iterable[Task]):
        self._tasks = list(tasks)

    def get_due_tasks(self, current_time: str) -> List[Task]:
        return [
            task for task in self._tasks
            if task.scheduled_time == current_time
        ]

    def add_task(self, task: Task) -> None:
        self._tasks.append(task)

    def list_tasks(self) -> List[Task]:
        return list(self._tasks)