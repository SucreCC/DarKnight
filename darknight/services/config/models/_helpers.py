from __future__ import annotations

from typing import Any


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def section(raw: dict[str, Any], key: str) -> dict[str, Any]:
    return as_dict(raw.get(key) or {})


def as_tuple_str(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    return tuple(str(item) for item in value)


def as_tuple_int(value: Any) -> tuple[int, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(int(item.strip()) for item in value.split(",") if item.strip())
    return tuple(int(item) for item in value)


__all__ = [
    "as_dict",
    "as_tuple_int",
    "as_tuple_str",
    "section",
]
