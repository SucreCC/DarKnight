from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._helpers import as_dict


@dataclass(frozen=True)
class TemplatePairConfig:
    subscription: str = ""
    settings: str = ""

    @classmethod
    def from_dict(
        cls,
        raw: dict[str, Any] | None = None,
        *,
        defaults: TemplatePairConfig | None = None,
    ) -> TemplatePairConfig:
        data = raw or {}
        base = defaults or cls()
        return cls(
            subscription=str(data.get("subscription", base.subscription)),
            settings=str(data.get("settings", base.settings)),
        )


@dataclass(frozen=True)
class UserAgentTemplateConfig:
    default: str = "user_agent/default.json"
    grpc: str = "user_agent/grpc.json"

    @classmethod
    def from_dict(
        cls,
        raw: dict[str, Any] | None = None,
        *,
        defaults: UserAgentTemplateConfig | None = None,
    ) -> UserAgentTemplateConfig:
        data = raw or {}
        base = defaults or cls()
        return cls(
            default=str(data.get("default", base.default)),
            grpc=str(data.get("grpc", base.grpc)),
        )


@dataclass(frozen=True)
class TemplatesConfig:
    custom_directory: str | None = None
    subscription_page: str = "subscription/index.html"
    home_page: str = "home/index.html"
    clash: TemplatePairConfig = field(
        default_factory=lambda: TemplatePairConfig(
            subscription="clash/default.yml",
            settings="clash/settings.yml",
        )
    )
    singbox: TemplatePairConfig = field(
        default_factory=lambda: TemplatePairConfig(
            subscription="singbox/default.json",
            settings="singbox/settings.json",
        )
    )
    mux: str = "mux/default.json"
    v2ray: TemplatePairConfig = field(
        default_factory=lambda: TemplatePairConfig(
            subscription="v2ray/default.json",
            settings="v2ray/settings.json",
        )
    )
    user_agent: UserAgentTemplateConfig = field(default_factory=UserAgentTemplateConfig)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> TemplatesConfig:
        data = raw or {}
        defaults = cls()
        return cls(
            custom_directory=data.get("custom_directory"),
            subscription_page=str(data.get("subscription_page", defaults.subscription_page)),
            home_page=str(data.get("home_page", defaults.home_page)),
            clash=TemplatePairConfig.from_dict(as_dict(data.get("clash")), defaults=defaults.clash),
            singbox=TemplatePairConfig.from_dict(
                as_dict(data.get("singbox")), defaults=defaults.singbox
            ),
            mux=str(data.get("mux", defaults.mux)),
            v2ray=TemplatePairConfig.from_dict(as_dict(data.get("v2ray")), defaults=defaults.v2ray),
            user_agent=UserAgentTemplateConfig.from_dict(
                as_dict(data.get("user_agent")), defaults=defaults.user_agent
            ),
        )


__all__ = [
    "TemplatePairConfig",
    "TemplatesConfig",
    "UserAgentTemplateConfig",
]
