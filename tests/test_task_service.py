from unittest.mock import Mock

import pytest

from taskflow.models import Priority, Task, TaskStatus, TaskValidationError
from taskflow.service import TaskService


def test_service_creates_task_and_delegates_to_repository():
    repository = Mock()
    repository.add_task.side_effect = lambda task: Task(
        id=3,
        title=task.title,
        priority=task.priority,
        status=task.status,
        description=task.description,
        due_date=task.due_date,
    )
    service = TaskService(repository)

    task = service.create_task(
        "  Prepare demo ",
        "Slides and examples",
        priority="high",
        status="in_progress",
        due_date="2026-11-15",
    )

    assert task.id == 3
    assert task.title == "Prepare demo"
    assert task.priority is Priority.HIGH
    assert task.status is TaskStatus.IN_PROGRESS
    repository.add_task.assert_called_once()


def test_service_rejects_invalid_input_before_repository_call():
    repository = Mock()
    service = TaskService(repository)

    with pytest.raises(TaskValidationError):
        service.create_task("  ", priority="low", status="planned")

    repository.add_task.assert_not_called()


def test_service_lists_tasks_from_repository():
    expected_tasks = [
        Task(
            id=1,
            title="Saved",
            priority=Priority.MEDIUM,
            status=TaskStatus.PLANNED,
        )
    ]
    repository = Mock()
    repository.list_tasks.return_value = expected_tasks

    assert TaskService(repository).list_tasks() is expected_tasks
    repository.list_tasks.assert_called_once_with()


def test_service_does_not_hide_repository_errors():
    repository = Mock()
    repository.add_task.side_effect = RuntimeError("repository unavailable")

    with pytest.raises(RuntimeError, match="repository unavailable"):
        TaskService(repository).create_task(
            "Task",
            priority=Priority.MEDIUM,
            status=TaskStatus.PLANNED,
        )


@pytest.mark.parametrize(
    "fields",
    [
        {"title": "Task", "status": "planned"},
        {"title": "Task", "priority": "low"},
    ],
)
def test_service_requires_priority_and_status(fields):
    with pytest.raises(TypeError):
        TaskService(Mock()).create_task(**fields)
