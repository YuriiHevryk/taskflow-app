import sqlite3

import pytest

from taskflow.models import Priority, Task, TaskStatus
from taskflow.repository import TaskRepository


def test_list_tasks_returns_empty_list_for_new_database(tmp_path):
    repository = TaskRepository(tmp_path / "tasks.sqlite3")

    assert repository.list_tasks() == []


def test_repository_persists_all_fields_in_id_order(tmp_path):
    database = tmp_path / "nested" / "tasks.sqlite3"
    repository = TaskRepository(database)

    first = repository.add_task(
        Task(
            title="First",
            priority=Priority.LOW,
            status=TaskStatus.PLANNED,
            description="First description",
            due_date="2026-11-12",
        )
    )
    second = repository.add_task(
        Task(
            title="Second",
            priority=Priority.HIGH,
            status=TaskStatus.COMPLETED,
            description="",
        )
    )

    reopened_repository = TaskRepository(database)
    tasks = reopened_repository.list_tasks()

    assert first.id == 1
    assert second.id == 2
    assert [task.id for task in tasks] == [1, 2]
    assert tasks[0] == Task(
        id=1,
        title="First",
        priority=Priority.LOW,
        status=TaskStatus.PLANNED,
        description="First description",
        due_date="2026-11-12",
    )
    assert tasks[1] == Task(
        id=2,
        title="Second",
        priority=Priority.HIGH,
        status=TaskStatus.COMPLETED,
        description="",
    )


def test_repository_surfaces_database_errors(tmp_path):
    database_directory = tmp_path / "not-a-database-file"
    database_directory.mkdir()

    with pytest.raises(sqlite3.OperationalError):
        TaskRepository(database_directory)
