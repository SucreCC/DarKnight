from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._helpers import as_dict, as_tuple_str


@dataclass(frozen=True)
class SslConfig:
    certfile: str | None = None
    keyfile: str | None = None
    ca_type: str = "public"

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> SslConfig:
        ssl = as_dict(raw)
        ca_type = str(ssl.get("ca_type", cls.ca_type)).lower()
        if ca_type not in ("public", "private"):
            ca_type = "public"
        return cls(
            certfile=ssl.get("certfile"),
            keyfile=ssl.get("keyfile"),
            ca_type=ca_type,
        )


@dataclass(frozen=True)
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 33100
    uds: str | None = None
    ssl: SslConfig = field(default_factory=SslConfig)
    doc_url: str = "/docs"
    redoc_url: str = "/redoc"
    docs: bool = False
    allowed_origins: tuple[str, ...] = ("*",)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> ServerConfig:
        data = raw or {}
        return cls(
            host=str(data.get("host", cls.host)),
            port=int(data.get("port", cls.port)),
            uds=data.get("uds"),
            ssl=SslConfig.from_dict(data.get("ssl")),
            doc_url=str(data.get("doc_url", cls.doc_url)),
            redoc_url=str(data.get("redoc_url", cls.redoc_url)),
            docs=bool(data.get("docs", cls.docs)),
            allowed_origins=as_tuple_str(data.get("allowed_origins", list(cls.allowed_origins))),
        )


__all__ = ["ServerConfig", "SslConfig"]
