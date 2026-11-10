"""SQLite persistence for tasks."""

import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Iterator, List, Union

from taskflow.models import Priority, Task, TaskStatus


class TaskRepository:
    """Persist tasks in a local SQLite database."""

    def __init__(self, database_path: Union[str, Path]) -> None:
        self.database_path = Path(database_path).expanduser()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        with closing(sqlite3.connect(str(self.database_path))) as connection:
            connection.row_factory = sqlite3.Row
            with connection:
                yield connection

    def _initialize_schema(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL
                        CHECK (priority IN ('low', 'medium', 'high')),
                    status TEXT NOT NULL
                        CHECK (status IN (
                            'planned', 'in_progress', 'completed'
                        )),
                    due_date TEXT
                )
                """
            )

    def add_task(self, task: Task) -> Task:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    title, description, priority, status, due_date
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    task.priority.value,
                    task.status.value,
                    task.due_date,
                ),
            )
            task_id = cursor.lastrowid

        if task_id is None:
            raise RuntimeError("SQLite did not return the new task id.")
        return Task(
            id=task_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            status=task.status,
            due_date=task.due_date,
        )

    def list_tasks(self) -> List[Task]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT id, title, description, priority, status, due_date
                FROM tasks
                ORDER BY id ASC
                """
            ).fetchall()

        return [
            Task(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                priority=Priority(row["priority"]),
                status=TaskStatus(row["status"]),
                due_date=row["due_date"],
            )
            for row in rows
        ]
