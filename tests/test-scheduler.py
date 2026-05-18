from actions import ActionRegistry, SyncAction
from executor import TaskExecutor
from models import Task
from quota import InMemoryQuotaStore
from repositories import InMemoryTaskRepository
from scheduler import SimpleScheduler


def test_scheduler_runs_due_tasks():
    users_config = {
        "alice": {
            "quota": 2,
            "executed": 0,
        }
    }

    tasks = [
        Task.from_dict({
            "user": "alice",
            "time": "12:00",
            "action": "sync",
            "target": "/data/a",
        }),
        Task.from_dict({
            "user": "alice",
            "time": "12:00",
            "action": "sync",
            "target": "/data/b",
        }),
    ]

    quota_store = InMemoryQuotaStore(users_config)
    task_repository = InMemoryTaskRepository(tasks)

    action_registry = ActionRegistry()
    action_registry.register("sync", SyncAction())

    executor = TaskExecutor(quota_store, action_registry)
    scheduler = SimpleScheduler(task_repository, executor)

    success_count = scheduler.run_pending(current_time="12:00")

    assert success_count == 2
    assert quota_store.get_status("alice").executed == 2


def test_scheduler_blocks_task_when_quota_exceeded():
    users_config = {
        "alice": {
            "quota": 1,
            "executed": 0,
        }
    }

    tasks = [
        Task.from_dict({
            "user": "alice",
            "time": "12:00",
            "action": "sync",
            "target": "/data/a",
        }),
        Task.from_dict({
            "user": "alice",
            "time": "12:00",
            "action": "sync",
            "target": "/data/b",
        }),
    ]

    quota_store = InMemoryQuotaStore(users_config)
    task_repository = InMemoryTaskRepository(tasks)

    action_registry = ActionRegistry()
    action_registry.register("sync", SyncAction())

    executor = TaskExecutor(quota_store, action_registry)
    scheduler = SimpleScheduler(task_repository, executor)

    success_count = scheduler.run_pending(current_time="12:00")

    assert success_count == 1
    assert quota_store.get_status("alice").executed == 1