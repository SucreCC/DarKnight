from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._helpers import as_dict


@dataclass(frozen=True)
class SudoConfig:
    username: str = ""
    password: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> SudoConfig:
        data = raw or {}
        return cls(
            username=str(data.get("username", cls.username)),
            password=str(data.get("password", cls.password)),
        )


@dataclass(frozen=True)
class AuthConfig:
    sudo: SudoConfig = field(default_factory=SudoConfig)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> AuthConfig:
        data = raw or {}
        return cls(sudo=SudoConfig.from_dict(as_dict(data.get("sudo"))))


__all__ = ["AuthConfig", "SudoConfig"]
