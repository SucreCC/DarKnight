import os
from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import select, text

import darknight.xray as xray
from darknight.db.base import Base
from darknight.models.node import NodeStatus
from darknight.models.order import PortalOrderStatus
from darknight.models.proxy import (
    ProxyHostALPN,
    ProxyHostFingerprint,
    ProxyHostSecurity,
    ProxyTypes,
)
from darknight.models.user import ReminderType, UserDataLimitResetStrategy, UserStatus


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    username = Column(String(34), unique=True, index=True)
    hashed_password = Column(String(128))
    users = relationship("User", back_populates="admin")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_sudo = Column(Boolean, default=False)
    password_reset_at = Column(DateTime, nullable=True)
    telegram_id = Column(BigInteger, nullable=True, default=None)
    discord_webhook = Column(String(1024), nullable=True, default=None)
    users_usage = Column(BigInteger, nullable=False, default=0)
    usage_logs = relationship("AdminUsageLogs", back_populates="admin")


class AdminUsageLogs(Base):
    __tablename__ = "admin_usage_logs"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("admins.id"))
    admin = relationship("Admin", back_populates="usage_logs")
    used_traffic_at_reset = Column(BigInteger, nullable=False)
    reset_at = Column(DateTime, default=datetime.utcnow)


class EmailVerificationCode(Base):
    __tablename__ = "email_verification_codes"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), index=True, nullable=False)
    code = Column(String(8), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EmailOutbox(Base):
    __tablename__ = "email_outbox"

    id = Column(Integer, primary_key=True)
    account = Column(String(64), nullable=False)
    template = Column(String(128), nullable=False)
    to_address = Column(String(255), index=True, nullable=False)
    subject = Column(String(512), nullable=False)
    body_text = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)
    status = Column(String(32), index=True, nullable=False, default="pending")
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(34, collation='NOCASE'), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(128), nullable=True)
    email_verified_at = Column(DateTime, nullable=True)
    referrer_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    referrer = relationship("User", remote_side="User.id", foreign_keys=[referrer_user_id])
    wallet_balance = Column(Float, nullable=False, default=0.0)
    auto_renewal = Column(Boolean, nullable=False, default=False)
    notify_expire_email = Column(Boolean, nullable=False, default=True)
    notify_traffic_email = Column(Boolean, nullable=False, default=True)
    proxies = relationship("Proxy", back_populates="user", cascade="all, delete-orphan")
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active)
    used_traffic = Column(BigInteger, default=0)
    node_usages = relationship("NodeUserUsage", back_populates="user", cascade="all, delete-orphan")
    notification_reminders = relationship("NotificationReminder", back_populates="user", cascade="all, delete-orphan")
    data_limit = Column(BigInteger, nullable=True)
    data_limit_reset_strategy = Column(
        Enum(UserDataLimitResetStrategy),
        nullable=False,
        default=UserDataLimitResetStrategy.no_reset,
    )
    usage_logs = relationship("UserUsageResetLogs", back_populates="user")  # maybe rename it to reset_usage_logs?
    expire = Column(Integer, nullable=True)
    admin_id = Column(Integer, ForeignKey("admins.id"))
    admin = relationship("Admin", back_populates="users")
    sub_revoked_at = Column(DateTime, nullable=True, default=None)
    sub_updated_at = Column(DateTime, nullable=True, default=None)
    sub_last_user_agent = Column(String(512), nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(String(500), nullable=True, default=None)
    online_at = Column(DateTime, nullable=True, default=None)
    on_hold_expire_duration = Column(BigInteger, nullable=True, default=None)
    on_hold_timeout = Column(DateTime, nullable=True, default=None)

    # * Positive values: User will be deleted after the value of this field in days automatically.
    # * Negative values: User won't be deleted automatically at all.
    # * NULL: Uses global settings.
    auto_delete_in_days = Column(Integer, nullable=True, default=None)

    edit_at = Column(DateTime, nullable=True, default=None)
    last_status_change = Column(DateTime, default=datetime.utcnow, nullable=True)

    next_plan = relationship(
        "NextPlan",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @hybrid_property
    def reseted_usage(self) -> int:
        return int(sum([log.used_traffic_at_reset for log in self.usage_logs]))

    @reseted_usage.expression
    def reseted_usage(cls):
        return (
            select(func.sum(UserUsageResetLogs.used_traffic_at_reset)).
            where(UserUsageResetLogs.user_id == cls.id).
            label('reseted_usage')
        )

    @property
    def lifetime_used_traffic(self) -> int:
        return int(
            sum([log.used_traffic_at_reset for log in self.usage_logs])
            + self.used_traffic
        )

    @property
    def last_traffic_reset_time(self):
        return self.usage_logs[-1].reset_at if self.usage_logs else self.created_at

    @property
    def excluded_inbounds(self):
        _ = {}
        for proxy in self.proxies:
            _[proxy.type] = [i.tag for i in proxy.excluded_inbounds]
        return _

    @property
    def inbounds(self):
        _ = {}
        for proxy in self.proxies:
            _[proxy.type] = []
            excluded_tags = [i.tag for i in proxy.excluded_inbounds]
            for inbound in xray.config.inbounds_by_protocol.get(proxy.type, []):
                if inbound["tag"] not in excluded_tags:
                    _[proxy.type].append(inbound["tag"])

        return _


excluded_inbounds_association = Table(
    "exclude_inbounds_association",
    Base.metadata,
    Column("proxy_id", ForeignKey("proxies.id")),
    Column("inbound_tag", ForeignKey("inbounds.tag")),
)

template_inbounds_association = Table(
    "template_inbounds_association",
    Base.metadata,
    Column("user_template_id", ForeignKey("user_templates.id")),
    Column("inbound_tag", ForeignKey("inbounds.tag")),
)


class NextPlan(Base):
    __tablename__ = 'next_plans'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    data_limit = Column(BigInteger, nullable=False)
    expire = Column(Integer, nullable=True)
    add_remaining_traffic = Column(Boolean, nullable=False, default=False, server_default='0')
    fire_on_either = Column(Boolean, nullable=False, default=True, server_default='0')

    user = relationship("User", back_populates="next_plan")


class UserTemplate(Base):
    __tablename__ = "user_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    data_limit = Column(BigInteger, default=0)
    expire_duration = Column(BigInteger, default=0)  # in seconds
    username_prefix = Column(String(20), nullable=True)
    username_suffix = Column(String(20), nullable=True)

    inbounds = relationship(
        "ProxyInbound", secondary=template_inbounds_association
    )


class UserUsageResetLogs(Base):
    __tablename__ = "user_usage_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="usage_logs")
    used_traffic_at_reset = Column(BigInteger, nullable=False)
    reset_at = Column(DateTime, default=datetime.utcnow)


class Proxy(Base):
    __tablename__ = "proxies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="proxies")
    type = Column(Enum(ProxyTypes), nullable=False)
    settings = Column(JSON, nullable=False)
    excluded_inbounds = relationship(
        "ProxyInbound", secondary=excluded_inbounds_association
    )


class ProxyInbound(Base):
    __tablename__ = "inbounds"

    id = Column(Integer, primary_key=True)
    tag = Column(String(256), unique=True, nullable=False, index=True)
    hosts = relationship(
        "ProxyHost", back_populates="inbound", cascade="all, delete-orphan"
    )


class ProxyHost(Base):
    __tablename__ = "hosts"
    # __table_args__ = (
    #     UniqueConstraint('inbound_tag', 'remark'),
    # )

    id = Column(Integer, primary_key=True)
    remark = Column(String(256), unique=False, nullable=False)
    address = Column(String(256), unique=False, nullable=False)
    port = Column(Integer, nullable=True)
    path = Column(String(256), unique=False, nullable=True)
    sni = Column(String(1000), unique=False, nullable=True)
    host = Column(String(1000), unique=False, nullable=True)
    security = Column(
        Enum(ProxyHostSecurity),
        unique=False,
        nullable=False,
        default=ProxyHostSecurity.inbound_default,
    )
    alpn = Column(
        Enum(ProxyHostALPN),
        unique=False,
        nullable=False,
        default=ProxyHostSecurity.none,
        server_default=ProxyHostSecurity.none.name
    )
    fingerprint = Column(
        Enum(ProxyHostFingerprint),
        unique=False,
        nullable=False,
        default=ProxyHostSecurity.none,
        server_default=ProxyHostSecurity.none.name
    )

    inbound_tag = Column(String(256), ForeignKey("inbounds.tag"), nullable=False)
    inbound = relationship("ProxyInbound", back_populates="hosts")
    allowinsecure = Column(Boolean, nullable=True)
    is_disabled = Column(Boolean, nullable=True, default=False)
    mux_enable = Column(Boolean, nullable=False, default=False, server_default='0')
    fragment_setting = Column(String(100), nullable=True)
    noise_setting = Column(String(2000), nullable=True)
    random_user_agent = Column(Boolean, nullable=False, default=False, server_default='0')
    use_sni_as_host = Column(Boolean, nullable=False, default=False, server_default="0")


class System(Base):
    __tablename__ = "system"

    id = Column(Integer, primary_key=True)
    uplink = Column(BigInteger, default=0)
    downlink = Column(BigInteger, default=0)


class JWT(Base):
    __tablename__ = "jwt"

    id = Column(Integer, primary_key=True)
    secret_key = Column(
        String(64), nullable=False, default=lambda: os.urandom(32).hex()
    )


class TLS(Base):
    __tablename__ = "tls"

    id = Column(Integer, primary_key=True)
    key = Column(String(4096), nullable=False)
    certificate = Column(String(2048), nullable=False)


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    name = Column(String(256, collation='NOCASE'), unique=True)
    address = Column(String(256), unique=False, nullable=False)
    port = Column(Integer, unique=False, nullable=False)
    api_port = Column(Integer, unique=False, nullable=False)
    xray_version = Column(String(32), nullable=True)
    status = Column(Enum(NodeStatus), nullable=False, default=NodeStatus.connecting)
    last_status_change = Column(DateTime, default=datetime.utcnow)
    message = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    uplink = Column(BigInteger, default=0)
    downlink = Column(BigInteger, default=0)
    user_usages = relationship("NodeUserUsage", back_populates="node", cascade="all, delete-orphan")
    usages = relationship("NodeUsage", back_populates="node", cascade="all, delete-orphan")
    usage_coefficient = Column(Float, nullable=False, server_default=text("1.0"), default=1)


class NodeUserUsage(Base):
    __tablename__ = "node_user_usages"
    __table_args__ = (
        UniqueConstraint('created_at', 'user_id', 'node_id'),
    )

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, unique=False, nullable=False)  # one hour per record
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="node_usages")
    node_id = Column(Integer, ForeignKey("nodes.id"))
    node = relationship("Node", back_populates="user_usages")
    used_traffic = Column(BigInteger, default=0)


class NodeUsage(Base):
    __tablename__ = "node_usages"
    __table_args__ = (
        UniqueConstraint('created_at', 'node_id'),
    )

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, unique=False, nullable=False)  # one hour per record
    node_id = Column(Integer, ForeignKey("nodes.id"))
    node = relationship("Node", back_populates="usages")
    uplink = Column(BigInteger, default=0)
    downlink = Column(BigInteger, default=0)


class NotificationReminder(Base):
    __tablename__ = "notification_reminders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="notification_reminders")
    type = Column(Enum(ReminderType), nullable=False)
    threshold = Column(Integer, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    slug = Column(String(32), nullable=False, unique=True, index=True)
    name_zh = Column(String(128), nullable=False)
    name_en = Column(String(128), nullable=False)
    category = Column(String(16), nullable=False)  # period | traffic (legacy, always period)
    features_zh = Column(JSON, nullable=False, default=list)
    features_en = Column(JSON, nullable=False, default=list)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    is_listed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class InviteCode(Base):
    __tablename__ = "invite_codes"
    __table_args__ = (
        UniqueConstraint("code", name="uq_invite_codes_code"),
        UniqueConstraint("owner_user_id", name="uq_invite_codes_owner_user_id"),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), unique=True, index=True, nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    owner = relationship("User", foreign_keys=[owner_user_id])
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ReferralCommission(Base):
    __tablename__ = "referral_commissions"
    __table_args__ = (UniqueConstraint("order_id", name="uq_referral_commissions_order_id"),)

    id = Column(Integer, primary_key=True)
    referrer_user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    referred_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(String(64), ForeignKey("portal_orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    status = Column(String(16), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    available_at = Column(DateTime, nullable=False)
    transferred_at = Column(DateTime, nullable=True)


class CommissionPayout(Base):
    __tablename__ = "commission_payouts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WalletRedemption(Base):
    __tablename__ = "wallet_redemptions"
    __table_args__ = (UniqueConstraint("user_id", "coupon_code", name="uq_wallet_redemptions_user_coupon"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coupon_code = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PortalOrder(Base):
    __tablename__ = "portal_orders"

    id = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    user = relationship("User", backref="portal_orders")
    plan_id = Column(String(32), nullable=False)
    cycle_id = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    status = Column(Enum(PortalOrderStatus), nullable=False, default=PortalOrderStatus.pending, index=True)
    payment_provider = Column(String(32), nullable=False, default="paypal")
    paypal_order_id = Column(String(64), nullable=True, index=True)
    coupon = Column(String(64), nullable=True)
    discount = Column(Float, nullable=False, default=0.0)
    wallet_credit = Column(Float, nullable=False, default=0.0)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    snapshot_data_limit_gb = Column(Integer, nullable=True)
    snapshot_duration_days = Column(Integer, nullable=True)
    snapshot_product_name = Column(String(128), nullable=True)
