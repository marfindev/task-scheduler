import logging

from actions import ActionRegistry, BackupAction, DeleteAction, SyncAction
from executor import TaskExecutor
from models import Task
from quota import InMemoryQuotaStore
from repositories import InMemoryTaskRepository
from scheduler import SimpleScheduler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def build_scheduler() -> SimpleScheduler:
    users_config = {
        "alice": {
            "quota": 3,
            "executed": 0,
        },
        "bob": {
            "quota": 5,
            "executed": 0,
        },
    }

    task_inputs = [
        {
            "user": "alice",
            "time": "12:00",
            "action": "sync",
            "target": "/data/x",
            "params": {
                "priority": "high",
            },
        },
        {
            "user": "bob",
            "time": "12:00",
            "action": "backup",
            "target": "/srv/y",
            "params": {
                "compression": "gzip",
            },
        },
        {
            "user": "alice",
            "time": "12:00",
            "action": "delete",
            "target": "/tmp/z",
            "params": {
                "dry_run": True,
            },
        },
        {
            "user": "alice",
            "time": "13:30",
            "action": "backup",
            "target": "/data/report",
            "params": {
                "compression": "zip",
            },
        },
    ]

    tasks = [Task.from_dict(task_data) for task_data in task_inputs]

    quota_store = InMemoryQuotaStore(users_config)
    task_repository = InMemoryTaskRepository(tasks)

    action_registry = ActionRegistry()
    action_registry.register("sync", SyncAction())
    action_registry.register("backup", BackupAction())
    action_registry.register("delete", DeleteAction())

    executor = TaskExecutor(
        quota_store=quota_store,
        action_registry=action_registry,
    )

    return SimpleScheduler(
        task_repository=task_repository,
        executor=executor,
    )


if __name__ == "__main__":
    scheduler = build_scheduler()

    # Untuk simulasi/testing.
    scheduler.run_pending(current_time="12:00")

    # Untuk real scheduler sederhana, bisa pakai:
    # scheduler.run_pending()