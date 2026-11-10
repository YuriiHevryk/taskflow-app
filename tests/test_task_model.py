import pytest

from taskflow.models import Priority, Task, TaskStatus, TaskValidationError


def test_task_normalizes_title_and_accepts_optional_fields():
    task = Task(
        title="  Finish report  ",
        priority=Priority.MEDIUM,
        status=TaskStatus.PLANNED,
    )

    assert task.title == "Finish report"
    assert task.description == ""
    assert task.priority is Priority.MEDIUM
    assert task.status is TaskStatus.PLANNED
    assert task.due_date is None
    assert task.id is None


@pytest.mark.parametrize(
    "fields",
    [
        {"title": "Task", "status": "planned"},
        {"title": "Task", "priority": "low"},
    ],
)
def test_task_requires_priority_and_status(fields):
    with pytest.raises(TypeError):
        Task(**fields)


@pytest.mark.parametrize("title", ["", "   "])
def test_task_rejects_empty_title(title):
    with pytest.raises(TaskValidationError, match="Title must not be empty"):
        Task(title=title, priority="low", status="planned")


def test_task_rejects_non_string_description():
    with pytest.raises(TaskValidationError, match="Description must be a string"):
        Task(title="Task", priority="low", status="planned", description=None)


@pytest.mark.parametrize("priority", ["urgent", "", None])
def test_task_rejects_unknown_priority(priority):
    with pytest.raises(TaskValidationError, match="Priority must be one of"):
        Task(title="Task", priority=priority, status="planned")


@pytest.mark.parametrize("status", ["started", "", None])
def test_task_rejects_unknown_status(status):
    with pytest.raises(TaskValidationError, match="Status must be one of"):
        Task(title="Task", priority="low", status=status)


@pytest.mark.parametrize(
    "due_date",
    ["2026-2-03", "2026-02-30", "2026-11-30T12:00:00", "tomorrow"],
)
def test_task_rejects_invalid_due_date(due_date):
    with pytest.raises(TaskValidationError, match="YYYY-MM-DD"):
        Task(
            title="Task",
            priority="low",
            status="planned",
            due_date=due_date,
        )


def test_task_accepts_all_task_fields():
    task = Task(
        id=7,
        title="Release",
        priority="high",
        status="in_progress",
        description="Prepare release notes",
        due_date="2026-11-30",
    )

    assert task.id == 7
    assert task.priority is Priority.HIGH
    assert task.status is TaskStatus.IN_PROGRESS
