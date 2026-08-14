from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UsersConfig:
    autodelete_days: int = -1
    autodelete_include_limited_accounts: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> UsersConfig:
        data = raw or {}
        return cls(
            autodelete_days=int(data.get("autodelete_days", cls.autodelete_days)),
            autodelete_include_limited_accounts=bool(
                data.get("autodelete_include_limited_accounts", cls.autodelete_include_limited_accounts)
            ),
        )


__all__ = ["UsersConfig"]
