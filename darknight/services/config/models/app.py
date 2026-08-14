from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .auth import AuthConfig
from .database import DatabaseConfig
from .discord import DiscordConfig
from .features import FeaturesConfig
from .jobs import JobsConfig
from .jwt import JwtConfig
from .notifications import NotificationsConfig
from .project import ProjectConfig
from .server import ServerConfig
from .status_text import StatusTextConfig
from .subscription import SubscriptionConfig
from .telegram import TelegramConfig
from .templates import TemplatesConfig
from .users import UsersConfig
from .web import WebConfig
from .webhook import WebhookConfig
from .xray import XrayConfig
from ._helpers import section


@dataclass(frozen=True)
class AppConfig:
    project: ProjectConfig = field(default_factory=ProjectConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    web: WebConfig = field(default_factory=WebConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    xray: XrayConfig = field(default_factory=XrayConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    jwt: JwtConfig = field(default_factory=JwtConfig)
    templates: TemplatesConfig = field(default_factory=TemplatesConfig)
    notifications: NotificationsConfig = field(default_factory=NotificationsConfig)
    status_text: StatusTextConfig = field(default_factory=StatusTextConfig)
    users: UsersConfig = field(default_factory=UsersConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    webhook: WebhookConfig = field(default_factory=WebhookConfig)
    subscription: SubscriptionConfig = field(default_factory=SubscriptionConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    jobs: JobsConfig = field(default_factory=JobsConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> AppConfig:
        data = raw or {}
        server = ServerConfig.from_dict(section(data, "server"))
        return cls(
            project=ProjectConfig.from_dict(section(data, "project")),
            server=server,
            web=WebConfig.from_dict(section(data, "web"), server_port=server.port),
            database=DatabaseConfig.from_dict(section(data, "database")),
            xray=XrayConfig.from_dict(section(data, "xray")),
            telegram=TelegramConfig.from_dict(section(data, "telegram")),
            jwt=JwtConfig.from_dict(section(data, "jwt")),
            templates=TemplatesConfig.from_dict(section(data, "templates")),
            notifications=NotificationsConfig.from_dict(section(data, "notifications")),
            status_text=StatusTextConfig.from_dict(section(data, "status_text")),
            users=UsersConfig.from_dict(section(data, "users")),
            auth=AuthConfig.from_dict(section(data, "auth")),
            webhook=WebhookConfig.from_dict(section(data, "webhook")),
            subscription=SubscriptionConfig.from_dict(section(data, "subscription")),
            discord=DiscordConfig.from_dict(section(data, "discord")),
            jobs=JobsConfig.from_dict(section(data, "jobs")),
            features=FeaturesConfig.from_dict(section(data, "features")),
        )


__all__ = ["AppConfig"]
