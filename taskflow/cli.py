"""Command-line interface for basic TaskFlow task operations."""

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Union

from taskflow.models import Priority, Task, TaskStatus, TaskValidationError
from taskflow.repository import TaskRepository
from taskflow.service import TaskRepositoryProtocol, TaskService


def default_database_path() -> Path:
    """Return the platform's conventional per-user application data path."""
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        base_path = Path(local_app_data) if local_app_data else None
        if base_path is None or not base_path.is_absolute():
            base_path = Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        base_path = Path.home() / "Library" / "Application Support"
    else:
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        base_path = Path(xdg_data_home) if xdg_data_home else None
        if base_path is None or not base_path.is_absolute():
            base_path = Path.home() / ".local" / "share"

    return base_path / "TaskFlow" / "tasks.sqlite3"


def build_parser() -> argparse.ArgumentParser:
    database_default = default_database_path()
    parser = argparse.ArgumentParser(
        prog="taskflow",
        description="Create and list TaskFlow tasks.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=database_default,
        help=f"SQLite database file (default: {database_default}).",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="Create a task.")
    add_parser.add_argument("--title", required=True, help="Task title.")
    add_parser.add_argument(
        "--description",
        required=True,
        help="Task description (an empty value is allowed).",
    )
    add_parser.add_argument(
        "--priority",
        choices=[priority.value for priority in Priority],
        required=True,
    )
    add_parser.add_argument(
        "--status",
        choices=[status.value for status in TaskStatus],
        required=True,
    )
    add_parser.add_argument(
        "--due-date",
        help="Optional due date in YYYY-MM-DD format.",
    )

    commands.add_parser("list", help="List saved tasks.")
    return parser


def _format_task(task: Task) -> str:
    due_date = task.due_date or "-"
    return (
        f"{task.id}\t{task.title}\t{task.priority.value}\t"
        f"{task.status.value}\t{due_date}\t{task.description}"
    )


def main(
    argv: Optional[Sequence[str]] = None,
    repository_factory: Callable[[Path], TaskRepositoryProtocol] = TaskRepository,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        service = TaskService(repository_factory(args.database))
        if args.command == "add":
            task = service.create_task(
                title=args.title,
                description=args.description,
                priority=args.priority,
                status=args.status,
                due_date=args.due_date,
            )
            print(f"Created task {task.id}: {task.title}")
            return 0

        tasks = service.list_tasks()
        if not tasks:
            print("No tasks found.")
            return 0

        print("ID\tTITLE\tPRIORITY\tSTATUS\tDUE DATE\tDESCRIPTION")
        for task in tasks:
            print(_format_task(task))
        return 0
    except TaskValidationError as error:
        print(f"Invalid task: {error}", file=sys.stderr)
        return 2
    except (sqlite3.Error, OSError) as error:
        print(f"Unable to access task storage: {error}", file=sys.stderr)
        return 1
