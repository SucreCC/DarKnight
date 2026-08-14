from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProjectConfig:
    project_name: str = "darknight"
    description: str = "darknight"
    version: str = "1.0.0"
    api_version: str = "/api/v1"

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> ProjectConfig:
        data = raw or {}
        return cls(
            project_name=str(data.get("project_name", cls.project_name)),
            description=str(data.get("description", cls.description)),
            version=str(data.get("version", cls.version)),
            api_version=str(data.get("api_version", cls.api_version)),
        )


__all__ = ["ProjectConfig"]
