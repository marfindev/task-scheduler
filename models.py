import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class Task:
    id: str
    user: str
    scheduled_time: str
    action: str
    target: str
    params: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        required_fields = ["user", "time", "action", "target"]

        for field_name in required_fields:
            if field_name not in data:
                raise ValueError(f"Missing required field: {field_name}")

        scheduled_time = data["time"]
        cls._validate_time_format(scheduled_time)

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            user=data["user"],
            scheduled_time=scheduled_time,
            action=data["action"],
            target=data["target"],
            params=data.get("params", {}),
        )

    @staticmethod
    def _validate_time_format(value: str) -> None:
        try:
            datetime.datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError(
                f"Invalid time format: {value}. Expected format is HH:MM"
            ) from exc


@dataclass
class ActionResult:
    success: bool
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)