"""Task application and business logic."""

from typing import List, Optional, Protocol

from taskflow.models import Priority, Task, TaskStatus


class TaskRepositoryProtocol(Protocol):
    def add_task(self, task: Task) -> Task:
        ...

    def list_tasks(self) -> List[Task]:
        ...


class TaskService:
    """Validate task input and delegate persistence to a repository."""

    def __init__(self, repository: TaskRepositoryProtocol) -> None:
        self._repository = repository

    def create_task(
        self,
        title: str,
        description: str = "",
        *,
        priority: Priority,
        status: TaskStatus,
        due_date: Optional[str] = None,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=due_date,
        )
        return self._repository.add_task(task)

    def list_tasks(self) -> List[Task]:
        return self._repository.list_tasks()
