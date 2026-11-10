"""Task data model and input validation."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional, Type, TypeVar, Union


class TaskValidationError(ValueError):
    """Raised when a task contains invalid data."""


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


EnumValue = TypeVar("EnumValue", bound=Enum)


def _enum_value(
    value: Union[str, EnumValue],
    enum_type: Type[EnumValue],
    field_name: str,
) -> EnumValue:
    if isinstance(value, enum_type):
        return value

    if isinstance(value, str):
        try:
            return enum_type(value.strip().lower())
        except ValueError:
            pass

    allowed = ", ".join(member.value for member in enum_type)
    raise TaskValidationError(
        f"{field_name} must be one of: {allowed}."
    )


@dataclass(frozen=True)
class Task:
    title: str
    priority: Priority
    status: TaskStatus
    description: str = ""
    due_date: Optional[str] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not isinstance(self.title, str):
            raise TaskValidationError("Title must be a string.")

        title = self.title.strip()
        if not title:
            raise TaskValidationError("Title must not be empty.")
        object.__setattr__(self, "title", title)

        if not isinstance(self.description, str):
            raise TaskValidationError("Description must be a string.")

        object.__setattr__(
            self,
            "priority",
            _enum_value(self.priority, Priority, "Priority"),
        )
        object.__setattr__(
            self,
            "status",
            _enum_value(self.status, TaskStatus, "Status"),
        )

        if self.due_date is not None:
            if not isinstance(self.due_date, str):
                raise TaskValidationError(
                    "Due date must use YYYY-MM-DD format."
                )
            try:
                parsed_date = date.fromisoformat(self.due_date)
            except ValueError as error:
                raise TaskValidationError(
                    "Due date must use YYYY-MM-DD format."
                ) from error
            if parsed_date.isoformat() != self.due_date:
                raise TaskValidationError(
                    "Due date must use YYYY-MM-DD format."
                )

        if self.id is not None and (
            isinstance(self.id, bool)
            or not isinstance(self.id, int)
            or self.id <= 0
        ):
            raise TaskValidationError("Task id must be a positive integer.")
