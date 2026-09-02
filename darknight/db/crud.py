"""
Functions for managing proxy hosts, users, user templates, nodes, and administrative tasks.
"""

import secrets
import string
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, delete, func, or_
from sqlalchemy.orm import Query, Session, joinedload
from sqlalchemy.sql.functions import coalesce

from darknight.db.models import (
    EmailVerificationCode,
    CommissionPayout,
    InviteCode,
    JWT,
    ReferralCommission,
    WalletRedemption,
    TLS,
    Admin,
    AdminUsageLogs,
    NextPlan,
    Node,
    NodeUsage,
    NodeUserUsage,
    NotificationReminder,
    PortalOrder,
    PortalOrderStatus,
    Product,
    Proxy,
    ProxyHost,
    ProxyInbound,
    ProxyTypes,
    System,
    User,
    UserTemplate,
    UserUsageResetLogs,
)
from darknight.models.admin import AdminCreate, AdminModify, AdminPartialModify
from darknight.models.node import NodeCreate, NodeModify, NodeStatus, NodeUsageResponse
from darknight.models.product import (
    ProductCreate,
    ProductModify,
)
from darknight.models.proxy import ProxyHost as ProxyHostModify
from darknight.models.user import (
    ReminderType,
    UserCreate,
    UserDataLimitResetStrategy,
    UserModify,
    UserResponse,
    UserStatus,
    UserUsageResponse,
)
from darknight.models.user_template import UserTemplateCreate, UserTemplateModify
from darknight.services.config.settings import get_app_config
from darknight.utils.helpers import calculate_expiration_days, calculate_usage_percent


def add_default_host(db: Session, inbound: ProxyInbound):
    """
    Adds a default host to a proxy inbound.

    Args:
        db (Session): Database session.
        inbound (ProxyInbound): Proxy inbound to add the default host to.
    """
    host = ProxyHost(remark="🚀 Marz ({USERNAME}) [{PROTOCOL} - {TRANSPORT}]", address="{SERVER_IP}", inbound=inbound)
    db.add(host)
    db.commit()


def get_or_create_inbound(db: Session, inbound_tag: str) -> ProxyInbound:
    """
    Retrieves or creates a proxy inbound based on the given tag.

    Args:
        db (Session): Database session.
        inbound_tag (str): The tag of the inbound.

    Returns:
        ProxyInbound: The retrieved or newly created proxy inbound.
    """
    inbound = db.query(ProxyInbound).filter(ProxyInbound.tag == inbound_tag).first()
    if not inbound:
        inbound = ProxyInbound(tag=inbound_tag)
        db.add(inbound)
        db.commit()
        add_default_host(db, inbound)
        db.refresh(inbound)
    return inbound


def get_hosts(db: Session, inbound_tag: str) -> List[ProxyHost]:
    """
    Retrieves hosts for a given inbound tag.

    Args:
        db (Session): Database session.
        inbound_tag (str): The tag of the inbound.

    Returns:
        List[ProxyHost]: List of hosts for the inbound.
    """
    inbound = get_or_create_inbound(db, inbound_tag)
    return inbound.hosts


def add_host(db: Session, inbound_tag: str, host: ProxyHostModify) -> List[ProxyHost]:
    """
    Adds a new host to a proxy inbound.

    Args:
        db (Session): Database session.
        inbound_tag (str): The tag of the inbound.
        host (ProxyHostModify): Host details to be added.

    Returns:
        List[ProxyHost]: Updated list of hosts for the inbound.
    """
    inbound = get_or_create_inbound(db, inbound_tag)
    inbound.hosts.append(
        ProxyHost(
            remark=host.remark,
            address=host.address,
            port=host.port,
            path=host.path,
            sni=host.sni,
            host=host.host,
            inbound=inbound,
            security=host.security,
            alpn=host.alpn,
            fingerprint=host.fingerprint
        )
    )
    db.commit()
    db.refresh(inbound)
    return inbound.hosts


def update_hosts(db: Session, inbound_tag: str, modified_hosts: List[ProxyHostModify]) -> List[ProxyHost]:
    """
    Updates hosts for a given inbound tag.

    Args:
        db (Session): Database session.
        inbound_tag (str): The tag of the inbound.
        modified_hosts (List[ProxyHostModify]): List of modified hosts.

    Returns:
        List[ProxyHost]: Updated list of hosts for the inbound.
    """
    inbound = get_or_create_inbound(db, inbound_tag)
    inbound.hosts = [
        ProxyHost(
            remark=host.remark,
            address=host.address,
            port=host.port,
            path=host.path,
            sni=host.sni,
            host=host.host,
            inbound=inbound,
            security=host.security,
            alpn=host.alpn,
            fingerprint=host.fingerprint,
            allowinsecure=host.allowinsecure,
            is_disabled=host.is_disabled,
            mux_enable=host.mux_enable,
            fragment_setting=host.fragment_setting,
            noise_setting=host.noise_setting,
            random_user_agent=host.random_user_agent,
            use_sni_as_host=host.use_sni_as_host,
        ) for host in modified_hosts
    ]
    db.commit()
    db.refresh(inbound)
    return inbound.hosts


def get_user_queryset(db: Session) -> Query:
    """
    Retrieves the base user query with joined admin details.

    Args:
        db (Session): Database session.

    Returns:
        Query: Base user query.
    """
    return db.query(User).options(joinedload(User.admin)).options(joinedload(User.next_plan))


def get_user(db: Session, username: str) -> Optional[User]:
    """
    Retrieves a user by username.

    Args:
        db (Session): Database session.
        username (str): The username of the user.

    Returns:
        Optional[User]: The user object if found, else None.
    """
    return get_user_queryset(db).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return get_user_queryset(db).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a user by user ID.

    Args:
        db (Session): Database session.
        user_id (int): The ID of the user.

    Returns:
        Optional[User]: The user object if found, else None.
    """
    return get_user_queryset(db).filter(User.id == user_id).first()


UsersSortingOptions = Enum('UsersSortingOptions', {
    'username': User.username.asc(),
    'used_traffic': User.used_traffic.asc(),
    'data_limit': User.data_limit.asc(),
    'expire': User.expire.asc(),
    'created_at': User.created_at.asc(),
    '-username': User.username.desc(),
    '-used_traffic': User.used_traffic.desc(),
    '-data_limit': User.data_limit.desc(),
    '-expire': User.expire.desc(),
    '-created_at': User.created_at.desc(),
})


def get_users(db: Session,
              offset: Optional[int] = None,
              limit: Optional[int] = None,
              usernames: Optional[List[str]] = None,
              search: Optional[str] = None,
              status: Optional[Union[UserStatus, list]] = None,
              sort: Optional[List[UsersSortingOptions]] = None,
              admin: Optional[Admin] = None,
              admins: Optional[List[str]] = None,
              reset_strategy: Optional[Union[UserDataLimitResetStrategy, list]] = None,
              return_with_count: bool = False) -> Union[List[User], Tuple[List[User], int]]:
    """
    Retrieves users based on various filters and options.

    Args:
        db (Session): Database session.
        offset (Optional[int]): Number of records to skip.
        limit (Optional[int]): Number of records to retrieve.
        usernames (Optional[List[str]]): List of usernames to filter by.
        search (Optional[str]): Search term to filter by username or note.
        status (Optional[Union[UserStatus, list]]): User status or list of statuses to filter by.
        sort (Optional[List[UsersSortingOptions]]): Sorting options.
        admin (Optional[Admin]): Admin to filter users by.
        admins (Optional[List[str]]): List of admin usernames to filter users by.
        reset_strategy (Optional[Union[UserDataLimitResetStrategy, list]]): Data limit reset strategy to filter by.
        return_with_count (bool): Whether to return the total count of users.

    Returns:
        Union[List[User], Tuple[List[User], int]]: List of users or tuple of users and total count.
    """
    query = get_user_queryset(db)

    if search:
        query = query.filter(or_(User.username.ilike(f"%{search}%"), User.note.ilike(f"%{search}%")))

    if usernames:
        query = query.filter(User.username.in_(usernames))

    if status:
        if isinstance(status, list):
            query = query.filter(User.status.in_(status))
        else:
            query = query.filter(User.status == status)

    if reset_strategy:
        if isinstance(reset_strategy, list):
            query = query.filter(User.data_limit_reset_strategy.in_(reset_strategy))
        else:
            query = query.filter(User.data_limit_reset_strategy == reset_strategy)

    if admin:
        query = query.filter(User.admin == admin)

    if admins:
        query = query.filter(User.admin.has(Admin.username.in_(admins)))

    if return_with_count:
        count = query.count()

    if sort:
        query = query.order_by(*(opt.value for opt in sort))

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    if return_with_count:
        return query.all(), count

    return query.all()


def get_user_usages(db: Session, dbuser: User, start: datetime, end: datetime) -> List[UserUsageResponse]:
    """
    Retrieves user usages within a specified date range.

    Args:
        db (Session): Database session.
        dbuser (User): The user object.
        start (datetime): Start date for usage retrieval.
        end (datetime): End date for usage retrieval.

    Returns:
        List[UserUsageResponse]: List of user usage responses.
    """

    usages = {0: UserUsageResponse(  # Main Core
        node_id=None,
        node_name="Master",
        used_traffic=0
    )}

    for node in db.query(Node).all():
        usages[node.id] = UserUsageResponse(
            node_id=node.id,
            node_name=node.name,
            used_traffic=0
        )

    cond = and_(NodeUserUsage.user_id == dbuser.id,
                NodeUserUsage.created_at >= start,
                NodeUserUsage.created_at <= end)

    for v in db.query(NodeUserUsage).filter(cond):
        try:
            usages[v.node_id or 0].used_traffic += v.used_traffic
        except KeyError:
            pass

    return list(usages.values())


def get_users_count(db: Session, status: UserStatus = None, admin: Admin = None) -> int:
    """
    Retrieves the count of users based on status and admin filters.

    Args:
        db (Session): Database session.
        status (UserStatus, optional): Status to filter users by.
        admin (Admin, optional): Admin to filter users by.

    Returns:
        int: Count of users matching the criteria.
    """
    query = db.query(User.id)
    if admin:
        query = query.filter(User.admin == admin)
    if status:
        query = query.filter(User.status == status)
    return query.count()


def create_user(
    db: Session,
    user: UserCreate,
    admin: Admin = None,
    *,
    email: Optional[str] = None,
    hashed_password: Optional[str] = None,
    email_verified_at: Optional[datetime] = None,
    referrer_user_id: Optional[int] = None,
) -> User:
    """
    Creates a new user with provided details.

    Args:
        db (Session): Database session.
        user (UserCreate): User creation details.
        admin (Admin, optional): Admin associated with the user.

    Returns:
        User: The created user object.
    """
    excluded_inbounds_tags = user.excluded_inbounds
    proxies = []
    for proxy_type, settings in user.proxies.items():
        excluded_inbounds = [
            get_or_create_inbound(db, tag) for tag in excluded_inbounds_tags[proxy_type]
        ]
        proxies.append(
            Proxy(type=proxy_type.value,
                  settings=settings.dict(no_obj=True),
                  excluded_inbounds=excluded_inbounds)
        )

    dbuser = User(
        username=user.username,
        email=email,
        hashed_password=hashed_password,
        email_verified_at=email_verified_at,
        referrer_user_id=referrer_user_id,
        proxies=proxies,
        status=user.status,
        data_limit=(user.data_limit or None),
        expire=(user.expire or None),
        admin=admin,
        data_limit_reset_strategy=user.data_limit_reset_strategy,
        note=user.note,
        on_hold_expire_duration=(user.on_hold_expire_duration or None),
        on_hold_timeout=(user.on_hold_timeout or None),
        auto_delete_in_days=user.auto_delete_in_days,
        next_plan=NextPlan(
            data_limit=user.next_plan.data_limit,
            expire=user.next_plan.expire,
            add_remaining_traffic=user.next_plan.add_remaining_traffic,
            fire_on_either=user.next_plan.fire_on_either,
        ) if user.next_plan else None
    )
    db.add(dbuser)
    db.commit()
    db.refresh(dbuser)
    return dbuser


def remove_user(db: Session, dbuser: User) -> User:
    """
    Removes a user from the database.

    Args:
        db (Session): Database session.
        dbuser (User): The user object to be removed.

    Returns:
        User: The removed user object.
    """
    db.delete(dbuser)
    db.commit()
    return dbuser


def remove_users(db: Session, dbusers: List[User]):
    """
    Removes multiple users from the database.

    Args:
        db (Session): Database session.
        dbusers (List[User]): List of user objects to be removed.
    """
    for dbuser in dbusers:
        db.delete(dbuser)
    db.commit()
    return


def update_user(db: Session, dbuser: User, modify: UserModify) -> User:
    """
    Updates a user with new details.

    Args:
        db (Session): Database session.
        dbuser (User): The user object to be updated.
        modify (UserModify): New details for the user.

    Returns:
        User: The updated user object.
    """
    added_proxies: Dict[ProxyTypes, Proxy] = {}
    if modify.proxies:
        for proxy_type, settings in modify.proxies.items():
            dbproxy = db.query(Proxy) \
                .where(Proxy.user == dbuser, Proxy.type == proxy_type) \
                .first()
            if dbproxy:
                dbproxy.settings = settings.dict(no_obj=True)
            else:
                new_proxy = Proxy(type=proxy_type, settings=settings.dict(no_obj=True))
                dbuser.proxies.append(new_proxy)
                added_proxies.update({proxy_type: new_proxy})
        for proxy in dbuser.proxies:
            if proxy.type not in modify.proxies:
                db.delete(proxy)
    if modify.inbounds:
        for proxy_type, tags in modify.excluded_inbounds.items():
            dbproxy = db.query(Proxy) \
                .where(Proxy.user == dbuser, Proxy.type == proxy_type) \
                .first() or added_proxies.get(proxy_type)
            if dbproxy:
                dbproxy.excluded_inbounds = [get_or_create_inbound(db, tag) for tag in tags]

    if modify.status is not None:
        dbuser.status = modify.status

    notifications = get_app_config().notifications

    if modify.data_limit is not None:
        dbuser.data_limit = (modify.data_limit or None)
        if dbuser.status not in (UserStatus.expired, UserStatus.disabled):
            if not dbuser.data_limit or dbuser.used_traffic < dbuser.data_limit:
                if dbuser.status != UserStatus.on_hold:
                    dbuser.status = UserStatus.active

                for percent in sorted(notifications.reached_usage_percent, reverse=True):
                    if not dbuser.data_limit or (calculate_usage_percent(
                            dbuser.used_traffic, dbuser.data_limit) < percent):
                        reminder = get_notification_reminder(db, dbuser.id, ReminderType.data_usage, threshold=percent)
                        if reminder:
                            delete_notification_reminder(db, reminder)

            else:
                dbuser.status = UserStatus.limited

    if modify.expire is not None:
        dbuser.expire = (modify.expire or None)
        if dbuser.status in (UserStatus.active, UserStatus.expired):
            if not dbuser.expire or dbuser.expire > datetime.utcnow().timestamp():
                dbuser.status = UserStatus.active
                for days_left in sorted(notifications.days_left):
                    if not dbuser.expire or (calculate_expiration_days(
                            dbuser.expire) > days_left):
                        reminder = get_notification_reminder(
                            db, dbuser.id, ReminderType.expiration_date, threshold=days_left)
                        if reminder:
                            delete_notification_reminder(db, reminder)
            else:
                dbuser.status = UserStatus.expired

    if modify.note is not None:
        dbuser.note = modify.note or None

    if modify.data_limit_reset_strategy is not None:
        dbuser.data_limit_reset_strategy = modify.data_limit_reset_strategy.value

    if modify.on_hold_timeout is not None:
        dbuser.on_hold_timeout = modify.on_hold_timeout

    if modify.on_hold_expire_duration is not None:
        dbuser.on_hold_expire_duration = modify.on_hold_expire_duration

    if modify.next_plan is not None:
        dbuser.next_plan = NextPlan(
            data_limit=modify.next_plan.data_limit,
            expire=modify.next_plan.expire,
            add_remaining_traffic=modify.next_plan.add_remaining_traffic,
            fire_on_either=modify.next_plan.fire_on_either,
        )
    elif dbuser.next_plan is not None:
        db.delete(dbuser.next_plan)

    dbuser.edit_at = datetime.utcnow()

    db.commit()
    db.refresh(dbuser)
    return dbuser


def reset_user_data_usage(db: Session, dbuser: User) -> User:
    """
    Resets the data usage of a user and logs the reset.

    Args:
        db (Session): Database session.
        dbuser (User): The user object whose data usage is to be reset.

    Returns:
        User: The updated user object.
    """
    usage_log = UserUsageResetLogs(
        user=dbuser,
        used_traffic_at_reset=dbuser.used_traffic,
    )
    db.add(usage_log)

    dbuser.used_traffic = 0
    dbuser.node_usages.clear()
    if dbuser.status not in (UserStatus.expired or UserStatus.disabled):
        dbuser.status = UserStatus.active.value

    if dbuser.next_plan:
        db.delete(dbuser.next_plan)
        dbuser.next_plan = None
    db.add(dbuser)

    db.commit()
    db.refresh(dbuser)
    return dbuser


def reset_user_by_next(db: Session, dbuser: User) -> User:
    """
    Resets the data usage of a user based on next user.

    Args:
        db (Session): Database session.
        dbuser (User): The user object whose data usage is to be reset.

    Returns:
        User: The updated user object.
    """

    if (dbuser.next_plan is None):
        return

    usage_log = UserUsageResetLogs(
        user=dbuser,
        used_traffic_at_reset=dbuser.used_traffic,
    )
    db.add(usage_log)

    dbuser.node_usages.clear()
    dbuser.status = UserStatus.active.value

    dbuser.data_limit = dbuser.next_plan.data_limit + \
        (0 if dbuser.next_plan.add_remaining_traffic else dbuser.data_limit - dbuser.used_traffic)
    dbuser.expire = dbuser.next_plan.expire

    dbuser.used_traffic = 0
    db.delete(dbuser.next_plan)
    dbuser.next_plan = None
    db.add(dbuser)

    db.commit()
    db.refresh(dbuser)
    return dbuser


def revoke_user_sub(db: Session, dbuser: User) -> User:
    """
    Revokes the subscription of a user and updates proxies settings.

    Args:
        db (Session): Database session.
        dbuser (User): The user object whose subscription is to be revoked.

    Returns:
        User: The updated user object.
    """
    dbuser.sub_revoked_at = datetime.utcnow()

    user = UserResponse.model_validate(dbuser)
    for proxy_type, settings in user.proxies.copy().items():
        settings.revoke()
        user.proxies[proxy_type] = settings
    dbuser = update_user(db, dbuser, user)

    db.commit()
    db.refresh(dbuser)
    return dbuser


def update_user_sub(db: Session, dbuser: User, user_agent: str) -> User:
    """
    Updates the user's subscription details.

    Args:
        db (Session): Database session.
        dbuser (User): The user object whose subscription is to be updated.
        user_agent (str): The user agent string to update.

    Returns:
        User: The updated user object.
    """
    dbuser.sub_updated_at = datetime.utcnow()
    dbuser.sub_last_user_agent = user_agent

    db.commit()
    db.refresh(dbuser)
    return dbuser


def reset_all_users_data_usage(db: Session, admin: Optional[Admin] = None):
    """
    Resets the data usage for all users or users under a specific admin.

    Args:
        db (Session): Database session.
        admin (Optional[Admin]): Admin to filter users by, if any.
    """
    query = get_user_queryset(db)

    if admin:
        query = query.filter(User.admin == admin)

    for dbuser in query.all():
        dbuser.used_traffic = 0
        if dbuser.status not in [UserStatus.on_hold, UserStatus.expired, UserStatus.disabled]:
            dbuser.status = UserStatus.active
        dbuser.usage_logs.clear()
        dbuser.node_usages.clear()
        if dbuser.next_plan:
            db.delete(dbuser.next_plan)
            dbuser.next_plan = None
        db.add(dbuser)

    db.commit()


def disable_all_active_users(db: Session, admin: Optional[Admin] = None):
    """
    Disable all active users or users under a specific admin.

    Args:
        db (Session): Database session.
        admin (Optional[Admin]): Admin to filter users by, if any.
    """
    query = db.query(User).filter(User.status.in_((UserStatus.active, UserStatus.on_hold)))
    if admin:
        query = query.filter(User.admin == admin)

    query.update({User.status: UserStatus.disabled, User.last_status_change: datetime.utcnow()}, synchronize_session=False)

    db.commit()


def activate_all_disabled_users(db: Session, admin: Optional[Admin] = None):
    """
    Activate all disabled users or users under a specific admin.

    Args:
        db (Session): Database session.
        admin (Optional[Admin]): Admin to filter users by, if any.
    """
    query_for_active_users = db.query(User).filter(User.status == UserStatus.disabled)
    query_for_on_hold_users = db.query(User).filter(
        and_(
            User.status == UserStatus.disabled, User.expire.is_(
                None), User.on_hold_expire_duration.isnot(None), User.online_at.is_(None)
        ))
    if admin:
        query_for_active_users = query_for_active_users.filter(User.admin == admin)
        query_for_on_hold_users = query_for_on_hold_users.filter(User.admin == admin)

    query_for_on_hold_users.update(
        {User.status: UserStatus.on_hold, User.last_status_change: datetime.utcnow()}, synchronize_session=False)
    query_for_active_users.update(
        {User.status: UserStatus.active, User.last_status_change: datetime.utcnow()}, synchronize_session=False)

    db.commit()


def autodelete_expired_users(db: Session,
                             include_limited_users: bool = False) -> List[User]:
    """
    Deletes expired (optionally also limited) users whose auto-delete time has passed.

    Args:
        db (Session): Database session
        include_limited_users (bool, optional): Whether to delete limited users as well.
            Defaults to False.

    Returns:
        list[User]: List of deleted users.
    """
    target_status = (
        [UserStatus.expired] if not include_limited_users
        else [UserStatus.expired, UserStatus.limited]
    )

    auto_delete = coalesce(User.auto_delete_in_days, get_app_config().users.autodelete_days)

    query = db.query(
        User, auto_delete,  # Use global auto-delete days as fallback
    ).filter(
        auto_delete >= 0,  # Negative values prevent auto-deletion
        User.status.in_(target_status),
    ).options(joinedload(User.admin))

    # TODO: Handle time filter in query itself (NOTE: Be careful with sqlite's strange datetime handling)
    expired_users = [
        user
        for (user, auto_delete) in query
        if user.last_status_change + timedelta(days=auto_delete) <= datetime.utcnow()
    ]

    if expired_users:
        remove_users(db, expired_users)

    return expired_users


def get_all_users_usages(
        db: Session, admin: Admin, start: datetime, end: datetime
) -> List[UserUsageResponse]:
    """
    Retrieves usage data for all users associated with an admin within a specified time range.

    This function calculates the total traffic used by users across different nodes,
    including a "Master" node that represents the main core.

    Args:
        db (Session): Database session for querying.
        admin (Admin): The admin user for which to retrieve user usage data.
        start (datetime): The start date and time of the period to consider.
        end (datetime): The end date and time of the period to consider.

    Returns:
        List[UserUsageResponse]: A list of UserUsageResponse objects, each representing
        the usage data for a specific node or the main core.
    """
    usages = {0: UserUsageResponse(  # Main Core
        node_id=None,
        node_name="Master",
        used_traffic=0
    )}

    for node in db.query(Node).all():
        usages[node.id] = UserUsageResponse(
            node_id=node.id,
            node_name=node.name,
            used_traffic=0
        )

    admin_users = set(user.id for user in get_users(db=db, admins=admin))

    cond = and_(
        NodeUserUsage.created_at >= start,
        NodeUserUsage.created_at <= end,
        NodeUserUsage.user_id.in_(admin_users)
    )

    for v in db.query(NodeUserUsage).filter(cond):
        try:
            usages[v.node_id or 0].used_traffic += v.used_traffic
        except KeyError:
            pass

    return list(usages.values())


def update_user_status(db: Session, dbuser: User, status: UserStatus) -> User:
    """
    Updates a user's status and records the time of change.

    Args:
        db (Session): Database session.
        dbuser (User): The user to update.
        status (UserStatus): The new status.

    Returns:
        User: The updated user object.
    """
    dbuser.status = status
    dbuser.last_status_change = datetime.utcnow()
    db.commit()
    db.refresh(dbuser)
    return dbuser


def set_owner(db: Session, dbuser: User, admin: Admin) -> User:
    """
    Sets the owner (admin) of a user.

    Args:
        db (Session): Database session.
        dbuser (User): The user object whose owner is to be set.
        admin (Admin): The admin to set as owner.

    Returns:
        User: The updated user object.
    """
    dbuser.admin = admin
    db.commit()
    db.refresh(dbuser)
    return dbuser


def start_user_expire(db: Session, dbuser: User) -> User:
    """
    Starts the expiration timer for a user.

    Args:
        db (Session): Database session.
        dbuser (User): The user object whose expiration timer is to be started.

    Returns:
        User: The updated user object.
    """
    expire = int(datetime.utcnow().timestamp()) + dbuser.on_hold_expire_duration
    dbuser.expire = expire
    dbuser.on_hold_expire_duration = None
    dbuser.on_hold_timeout = None
    db.commit()
    db.refresh(dbuser)
    return dbuser


def get_system_usage(db: Session) -> System:
    """
    Retrieves system usage information.

    Args:
        db (Session): Database session.

    Returns:
        System: System usage information.
    """
    return db.query(System).first()


def get_jwt_secret_key(db: Session) -> str:
    """
    Retrieves the JWT secret key.

    Args:
        db (Session): Database session.

    Returns:
        str: JWT secret key.
    """
    return db.query(JWT).first().secret_key


def get_tls_certificate(db: Session) -> TLS:
    """
    Retrieves the TLS certificate.

    Args:
        db (Session): Database session.

    Returns:
        TLS: TLS certificate information.
    """
    return db.query(TLS).first()


def get_admin(db: Session, username: str) -> Admin:
    """
    Retrieves an admin by username.

    Args:
        db (Session): Database session.
        username (str): The username of the admin.

    Returns:
        Admin: The admin object.
    """
    return db.query(Admin).filter(Admin.username == username).first()


def create_admin(db: Session, admin: AdminCreate) -> Admin:
    """
    Creates a new admin in the database.

    Args:
        db (Session): Database session.
        admin (AdminCreate): The admin creation data.

    Returns:
        Admin: The created admin object.
    """
    dbadmin = Admin(
        username=admin.username,
        hashed_password=admin.hashed_password,
        is_sudo=admin.is_sudo,
        telegram_id=admin.telegram_id if admin.telegram_id else None,
        discord_webhook=admin.discord_webhook if admin.discord_webhook else None
    )
    db.add(dbadmin)
    db.commit()
    db.refresh(dbadmin)
    return dbadmin


def update_admin(db: Session, dbadmin: Admin, modified_admin: AdminModify) -> Admin:
    """
    Updates an admin's details.

    Args:
        db (Session): Database session.
        dbadmin (Admin): The admin object to be updated.
        modified_admin (AdminModify): The modified admin data.

    Returns:
        Admin: The updated admin object.
    """
    if modified_admin.is_sudo:
        dbadmin.is_sudo = modified_admin.is_sudo
    if modified_admin.password is not None and dbadmin.hashed_password != modified_admin.hashed_password:
        dbadmin.hashed_password = modified_admin.hashed_password
        dbadmin.password_reset_at = datetime.utcnow()
    if modified_admin.telegram_id:
        dbadmin.telegram_id = modified_admin.telegram_id
    if modified_admin.discord_webhook:
        dbadmin.discord_webhook = modified_admin.discord_webhook

    db.commit()
    db.refresh(dbadmin)
    return dbadmin


def partial_update_admin(db: Session, dbadmin: Admin, modified_admin: AdminPartialModify) -> Admin:
    """
    Partially updates an admin's details.

    Args:
        db (Session): Database session.
        dbadmin (Admin): The admin object to be updated.
        modified_admin (AdminPartialModify): The modified admin data.

    Returns:
        Admin: The updated admin object.
    """
    if modified_admin.is_sudo is not None:
        dbadmin.is_sudo = modified_admin.is_sudo
    if modified_admin.password is not None and dbadmin.hashed_password != modified_admin.hashed_password:
        dbadmin.hashed_password = modified_admin.hashed_password
        dbadmin.password_reset_at = datetime.utcnow()
    if modified_admin.telegram_id is not None:
        dbadmin.telegram_id = modified_admin.telegram_id
    if modified_admin.discord_webhook is not None:
        dbadmin.discord_webhook = modified_admin.discord_webhook

    db.commit()
    db.refresh(dbadmin)
    return dbadmin


def remove_admin(db: Session, dbadmin: Admin) -> Admin:
    """
    Removes an admin from the database.

    Args:
        db (Session): Database session.
        dbadmin (Admin): The admin object to be removed.

    Returns:
        Admin: The removed admin object.
    """
    db.delete(dbadmin)
    db.commit()
    return dbadmin


def get_admin_by_id(db: Session, id: int) -> Admin:
    """
    Retrieves an admin by their ID.

    Args:
        db (Session): Database session.
        id (int): The ID of the admin.

    Returns:
        Admin: The admin object.
    """
    return db.query(Admin).filter(Admin.id == id).first()


def get_admin_by_telegram_id(db: Session, telegram_id: int) -> Admin:
    """
    Retrieves an admin by their Telegram ID.

    Args:
        db (Session): Database session.
        telegram_id (int): The Telegram ID of the admin.

    Returns:
        Admin: The admin object.
    """
    return db.query(Admin).filter(Admin.telegram_id == telegram_id).first()


def get_admins(db: Session,
               offset: Optional[int] = None,
               limit: Optional[int] = None,
               username: Optional[str] = None) -> List[Admin]:
    """
    Retrieves a list of admins with optional filters and pagination.

    Args:
        db (Session): Database session.
        offset (Optional[int]): The number of records to skip (for pagination).
        limit (Optional[int]): The maximum number of records to return.
        username (Optional[str]): The username to filter by.

    Returns:
        List[Admin]: A list of admin objects.
    """
    query = db.query(Admin)
    if username:
        query = query.filter(Admin.username.ilike(f'%{username}%'))
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    return query.all()


def reset_admin_usage(db: Session, dbadmin: Admin) -> int:
    """
    Retrieves an admin's usage by their username.
    Args:
        db (Session): Database session.
        dbadmin (Admin): The admin object to be updated.
    Returns:
        Admin: The updated admin.
    """
    if (dbadmin.users_usage == 0):
        return dbadmin

    usage_log = AdminUsageLogs(
        admin=dbadmin,
        used_traffic_at_reset=dbadmin.users_usage
    )
    db.add(usage_log)
    dbadmin.users_usage = 0

    db.commit()
    db.refresh(dbadmin)
    return dbadmin


def create_user_template(db: Session, user_template: UserTemplateCreate) -> UserTemplate:
    """
    Creates a new user template in the database.

    Args:
        db (Session): Database session.
        user_template (UserTemplateCreate): The user template creation data.

    Returns:
        UserTemplate: The created user template object.
    """
    inbound_tags: List[str] = []
    for _, i in user_template.inbounds.items():
        inbound_tags.extend(i)
    dbuser_template = UserTemplate(
        name=user_template.name,
        data_limit=user_template.data_limit,
        expire_duration=user_template.expire_duration,
        username_prefix=user_template.username_prefix,
        username_suffix=user_template.username_suffix,
        inbounds=db.query(ProxyInbound).filter(ProxyInbound.tag.in_(inbound_tags)).all()
    )
    db.add(dbuser_template)
    db.commit()
    db.refresh(dbuser_template)
    return dbuser_template


def update_user_template(
        db: Session, dbuser_template: UserTemplate, modified_user_template: UserTemplateModify) -> UserTemplate:
    """
    Updates a user template's details.

    Args:
        db (Session): Database session.
        dbuser_template (UserTemplate): The user template object to be updated.
        modified_user_template (UserTemplateModify): The modified user template data.

    Returns:
        UserTemplate: The updated user template object.
    """
    if modified_user_template.name is not None:
        dbuser_template.name = modified_user_template.name
    if modified_user_template.data_limit is not None:
        dbuser_template.data_limit = modified_user_template.data_limit
    if modified_user_template.expire_duration is not None:
        dbuser_template.expire_duration = modified_user_template.expire_duration
    if modified_user_template.username_prefix is not None:
        dbuser_template.username_prefix = modified_user_template.username_prefix
    if modified_user_template.username_suffix is not None:
        dbuser_template.username_suffix = modified_user_template.username_suffix

    if modified_user_template.inbounds:
        inbound_tags: List[str] = []
        for _, i in modified_user_template.inbounds.items():
            inbound_tags.extend(i)
        dbuser_template.inbounds = db.query(ProxyInbound).filter(ProxyInbound.tag.in_(inbound_tags)).all()

    db.commit()
    db.refresh(dbuser_template)
    return dbuser_template


def remove_user_template(db: Session, dbuser_template: UserTemplate):
    """
    Removes a user template from the database.

    Args:
        db (Session): Database session.
        dbuser_template (UserTemplate): The user template object to be removed.
    """
    db.delete(dbuser_template)
    db.commit()


def get_user_template(db: Session, user_template_id: int) -> UserTemplate:
    """
    Retrieves a user template by its ID.

    Args:
        db (Session): Database session.
        user_template_id (int): The ID of the user template.

    Returns:
        UserTemplate: The user template object.
    """
    return db.query(UserTemplate).filter(UserTemplate.id == user_template_id).first()


def get_user_templates(
        db: Session, offset: Union[int, None] = None, limit: Union[int, None] = None) -> List[UserTemplate]:
    """
    Retrieves a list of user templates with optional pagination.

    Args:
        db (Session): Database session.
        offset (Union[int, None]): The number of records to skip (for pagination).
        limit (Union[int, None]): The maximum number of records to return.

    Returns:
        List[UserTemplate]: A list of user template objects.
    """
    dbuser_templates = db.query(UserTemplate)
    if offset:
        dbuser_templates = dbuser_templates.offset(offset)
    if limit:
        dbuser_templates = dbuser_templates.limit(limit)

    return dbuser_templates.all()


def get_node(db: Session, name: str) -> Optional[Node]:
    """
    Retrieves a node by its name.

    Args:
        db (Session): The database session.
        name (str): The name of the node to retrieve.

    Returns:
        Optional[Node]: The Node object if found, None otherwise.
    """
    return db.query(Node).filter(Node.name == name).first()


def get_node_by_id(db: Session, node_id: int) -> Optional[Node]:
    """
    Retrieves a node by its ID.

    Args:
        db (Session): The database session.
        node_id (int): The ID of the node to retrieve.

    Returns:
        Optional[Node]: The Node object if found, None otherwise.
    """
    return db.query(Node).filter(Node.id == node_id).first()


def get_nodes(db: Session,
              status: Optional[Union[NodeStatus, list]] = None,
              enabled: bool = None) -> List[Node]:
    """
    Retrieves nodes based on optional status and enabled filters.

    Args:
        db (Session): The database session.
        status (Optional[Union[NodeStatus, list]]): The status or list of statuses to filter by.
        enabled (bool): If True, excludes disabled nodes.

    Returns:
        List[Node]: A list of Node objects matching the criteria.
    """
    query = db.query(Node)

    if status:
        if isinstance(status, list):
            query = query.filter(Node.status.in_(status))
        else:
            query = query.filter(Node.status == status)

    if enabled:
        query = query.filter(Node.status != NodeStatus.disabled)

    return query.all()


def get_nodes_usage(db: Session, start: datetime, end: datetime) -> List[NodeUsageResponse]:
    """
    Retrieves usage data for all nodes within a specified time range.

    Args:
        db (Session): The database session.
        start (datetime): The start time of the usage period.
        end (datetime): The end time of the usage period.

    Returns:
        List[NodeUsageResponse]: A list of NodeUsageResponse objects containing usage data.
    """
    usages = {0: NodeUsageResponse(  # Main Core
        node_id=None,
        node_name="Master",
        uplink=0,
        downlink=0
    )}

    for node in db.query(Node).all():
        usages[node.id] = NodeUsageResponse(
            node_id=node.id,
            node_name=node.name,
            uplink=0,
            downlink=0
        )

    cond = and_(NodeUsage.created_at >= start, NodeUsage.created_at <= end)

    for v in db.query(NodeUsage).filter(cond):
        try:
            usages[v.node_id or 0].uplink += v.uplink
            usages[v.node_id or 0].downlink += v.downlink
        except KeyError:
            pass

    return list(usages.values())


def create_node(db: Session, node: NodeCreate) -> Node:
    """
    Creates a new node in the database.

    Args:
        db (Session): The database session.
        node (NodeCreate): The node creation model containing node details.

    Returns:
        Node: The newly created Node object.
    """
    dbnode = Node(name=node.name,
                  address=node.address,
                  port=node.port,
                  api_port=node.api_port)

    db.add(dbnode)
    db.commit()
    db.refresh(dbnode)
    return dbnode


def remove_node(db: Session, dbnode: Node) -> Node:
    """
    Removes a node from the database.

    Args:
        db (Session): The database session.
        dbnode (Node): The Node object to be removed.

    Returns:
        Node: The removed Node object.
    """
    db.delete(dbnode)
    db.commit()
    return dbnode


def update_node(db: Session, dbnode: Node, modify: NodeModify) -> Node:
    """
    Updates an existing node with new information.

    Args:
        db (Session): The database session.
        dbnode (Node): The Node object to be updated.
        modify (NodeModify): The modification model containing updated node details.

    Returns:
        Node: The updated Node object.
    """
    if modify.name is not None:
        dbnode.name = modify.name

    if modify.address is not None:
        dbnode.address = modify.address

    if modify.port is not None:
        dbnode.port = modify.port

    if modify.api_port is not None:
        dbnode.api_port = modify.api_port

    if modify.status is NodeStatus.disabled:
        dbnode.status = modify.status
        dbnode.xray_version = None
        dbnode.message = None
    else:
        dbnode.status = NodeStatus.connecting

    if modify.usage_coefficient:
        dbnode.usage_coefficient = modify.usage_coefficient

    db.commit()
    db.refresh(dbnode)
    return dbnode


def update_node_status(db: Session, dbnode: Node, status: NodeStatus, message: str = None, version: str = None) -> Node:
    """
    Updates the status of a node.

    Args:
        db (Session): The database session.
        dbnode (Node): The Node object to be updated.
        status (NodeStatus): The new status of the node.
        message (str, optional): A message associated with the status update.
        version (str, optional): The version of the node software.

    Returns:
        Node: The updated Node object.
    """
    dbnode.status = status
    dbnode.message = message
    dbnode.xray_version = version
    dbnode.last_status_change = datetime.utcnow()
    db.commit()
    db.refresh(dbnode)
    return dbnode


def create_notification_reminder(
        db: Session, reminder_type: ReminderType, expires_at: datetime, user_id: int, threshold: Optional[int] = None) -> NotificationReminder:
    """
    Creates a new notification reminder.

    Args:
        db (Session): The database session.
        reminder_type (ReminderType): The type of reminder.
        expires_at (datetime): The expiration time of the reminder.
        user_id (int): The ID of the user associated with the reminder.
        threshold (Optional[int]): The threshold value to check for (e.g., days left or usage percent).

    Returns:
        NotificationReminder: The newly created NotificationReminder object.
    """
    reminder = NotificationReminder(type=reminder_type, expires_at=expires_at, user_id=user_id)
    if threshold is not None:
        reminder.threshold = threshold
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def get_notification_reminder(
        db: Session, user_id: int, reminder_type: ReminderType, threshold: Optional[int] = None
) -> Union[NotificationReminder, None]:
    """
    Retrieves a notification reminder for a user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        reminder_type (ReminderType): The type of reminder to retrieve.
        threshold (Optional[int]): The threshold value to check for (e.g., days left or usage percent).

    Returns:
        Union[NotificationReminder, None]: The NotificationReminder object if found and not expired, None otherwise.
    """
    query = db.query(NotificationReminder).filter(
        NotificationReminder.user_id == user_id,
        NotificationReminder.type == reminder_type
    )

    # If a threshold is provided, filter for reminders with this threshold
    if threshold is not None:
        query = query.filter(NotificationReminder.threshold == threshold)

    reminder = query.first()

    if reminder is None:
        return None

    # Check if the reminder has expired
    if reminder.expires_at and reminder.expires_at < datetime.utcnow():
        db.delete(reminder)
        db.commit()
        return None

    return reminder


def delete_notification_reminder_by_type(
        db: Session, user_id: int, reminder_type: ReminderType, threshold: Optional[int] = None
) -> None:
    """
    Deletes a notification reminder for a user based on the reminder type and optional threshold.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        reminder_type (ReminderType): The type of reminder to delete.
        threshold (Optional[int]): The threshold to delete (e.g., days left or usage percent). If not provided, deletes all reminders of that type.
    """
    stmt = delete(NotificationReminder).where(
        NotificationReminder.user_id == user_id,
        NotificationReminder.type == reminder_type
    )

    # If a threshold is provided, include it in the filter
    if threshold is not None:
        stmt = stmt.where(NotificationReminder.threshold == threshold)

    db.execute(stmt)
    db.commit()


def delete_notification_reminder(db: Session, dbreminder: NotificationReminder) -> None:
    """
    Deletes a specific notification reminder.

    Args:
        db (Session): The database session.
        dbreminder (NotificationReminder): The NotificationReminder object to delete.
    """
    db.delete(dbreminder)
    db.commit()
    return


def count_online_users(db: Session, hours: int = 24):
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=hours)
    query = db.query(func.count(User.id)).filter(User.online_at.isnot(
        None), User.online_at >= twenty_four_hours_ago)
    return query.scalar()


def save_email_verification_code(
    db: Session,
    email: str,
    code: str,
    expires_at: datetime,
) -> EmailVerificationCode:
    db.query(EmailVerificationCode).filter(EmailVerificationCode.email == email).delete()
    record = EmailVerificationCode(
        email=email,
        code=code,
        expires_at=expires_at,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_verification_code(db: Session, email: str) -> Optional[EmailVerificationCode]:
    return (
        db.query(EmailVerificationCode)
        .filter(EmailVerificationCode.email == email)
        .order_by(EmailVerificationCode.created_at.desc())
        .first()
    )


def delete_verification_codes(db: Session, email: str) -> None:
    db.query(EmailVerificationCode).filter(EmailVerificationCode.email == email).delete()
    db.commit()


def list_products(db: Session) -> list[Product]:
    return (
        db.query(Product)
        .order_by(Product.sort_order.asc(), Product.id.asc())
        .all()
    )


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_slug(db: Session, slug: str) -> Product | None:
    return db.query(Product).filter(Product.slug == slug).first()


def create_product(db: Session, payload: ProductCreate) -> Product:
    max_sort = db.query(func.max(Product.sort_order)).scalar()
    sort_order = payload.sort_order if payload.sort_order is not None else (max_sort or 0) + 1
    product = Product(
        slug=payload.slug,
        name_zh=payload.name_zh,
        name_en=payload.name_en,
        category=payload.category,
        features_zh=payload.features_zh,
        features_en=payload.features_en,
        price=payload.price,
        duration_days=payload.duration_days,
        sort_order=sort_order,
        is_listed=payload.is_listed,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, payload: ProductModify) -> Product:
    if payload.slug is not None:
        product.slug = payload.slug
    if payload.name_zh is not None:
        product.name_zh = payload.name_zh
    if payload.name_en is not None:
        product.name_en = payload.name_en
    if payload.category is not None:
        product.category = payload.category
    if payload.features_zh is not None:
        product.features_zh = payload.features_zh
    if payload.features_en is not None:
        product.features_en = payload.features_en
    if payload.price is not None:
        product.price = payload.price
    if payload.duration_days is not None:
        product.duration_days = payload.duration_days
    if payload.sort_order is not None:
        product.sort_order = payload.sort_order
    if payload.is_listed is not None:
        product.is_listed = payload.is_listed

    db.commit()
    db.refresh(product)
    return product


def remove_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def list_listed_products(db: Session) -> list[Product]:
    return (
        db.query(Product)
        .filter(Product.is_listed.is_(True))
        .order_by(Product.sort_order.asc(), Product.id.asc())
        .all()
    )


def get_listed_product(db: Session, slug: str) -> Product | None:
    product = get_product_by_slug(db, slug)
    if not product or not product.is_listed:
        return None
    return product


def has_pending_orders_for_product(db: Session, slug: str) -> bool:
    return (
        db.query(PortalOrder)
        .filter(
            PortalOrder.plan_id == slug,
            PortalOrder.status == PortalOrderStatus.pending,
        )
        .first()
        is not None
    )


def create_portal_order(
    db: Session,
    *,
    order_id: str,
    user_id: int,
    plan_id: str,
    amount: float,
    currency: str,
    paypal_order_id: str | None = None,
    coupon: str | None = None,
    discount: float = 0.0,
    wallet_credit: float = 0.0,
    snapshot_data_limit_gb: int | None = None,
    snapshot_duration_days: int | None = None,
    snapshot_product_name: str | None = None,
) -> PortalOrder:
    order = PortalOrder(
        id=order_id,
        user_id=user_id,
        plan_id=plan_id,
        cycle_id="",
        amount=amount,
        currency=currency,
        paypal_order_id=paypal_order_id,
        coupon=coupon,
        discount=discount,
        wallet_credit=wallet_credit,
        status=PortalOrderStatus.pending,
        payment_provider="paypal",
        snapshot_data_limit_gb=snapshot_data_limit_gb,
        snapshot_duration_days=snapshot_duration_days,
        snapshot_product_name=snapshot_product_name,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_portal_order(db: Session, order_id: str) -> Optional[PortalOrder]:
    return db.query(PortalOrder).filter(PortalOrder.id == order_id).first()


def get_portal_order_by_paypal_id(db: Session, paypal_order_id: str) -> Optional[PortalOrder]:
    return db.query(PortalOrder).filter(PortalOrder.paypal_order_id == paypal_order_id).first()


def list_portal_orders_for_user(db: Session, user_id: int) -> list[PortalOrder]:
    return (
        db.query(PortalOrder)
        .filter(PortalOrder.user_id == user_id)
        .order_by(PortalOrder.created_at.desc())
        .all()
    )


def get_user_current_plan(
    db: Session, user_id: int
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (plan_id, name_zh, name_en) from the most recent paid portal order."""
    order = (
        db.query(PortalOrder)
        .filter(
            PortalOrder.user_id == user_id,
            PortalOrder.status == PortalOrderStatus.paid,
        )
        .order_by(PortalOrder.paid_at.desc(), PortalOrder.created_at.desc())
        .first()
    )
    if not order:
        return None, None, None

    product = get_product_by_slug(db, order.plan_id)
    if product:
        return product.slug, product.name_zh, product.name_en

    snapshot = order.snapshot_product_name
    return order.plan_id, snapshot, snapshot


def update_portal_order(db: Session, order: PortalOrder, **fields) -> PortalOrder:
    for key, value in fields.items():
        setattr(order, key, value)
    db.commit()
    db.refresh(order)
    return order


def close_stale_portal_orders(db: Session, created_before: datetime) -> int:
    """Close pending orders that were never paid, returning how many were closed."""
    orders = (
        db.query(PortalOrder)
        .filter(
            PortalOrder.status == PortalOrderStatus.pending,
            PortalOrder.created_at < created_before,
        )
        .all()
    )
    if not orders:
        return 0

    closed = 0
    for order in orders:
        if order.wallet_credit > 0:
            refund_wallet_credit(db, order.user_id, order.wallet_credit)
            order.wallet_credit = 0
        order.status = PortalOrderStatus.closed
        db.add(order)
        closed += 1
    db.commit()
    return closed


_INVITE_CODE_ALPHABET = string.ascii_letters + string.digits
_INVITE_CODE_LENGTH = 8
_INVITE_CODE_MAX_ATTEMPTS = 10


def _generate_invite_code_value() -> str:
    return "".join(secrets.choice(_INVITE_CODE_ALPHABET) for _ in range(_INVITE_CODE_LENGTH))


def get_invite_code_by_owner(db: Session, owner_user_id: int) -> Optional[InviteCode]:
    return db.query(InviteCode).filter(InviteCode.owner_user_id == owner_user_id).first()


def get_invite_code_by_code(db: Session, code: str) -> Optional[InviteCode]:
    return db.query(InviteCode).filter(InviteCode.code == code).first()


def list_invite_codes_for_user(db: Session, owner_user_id: int) -> list[InviteCode]:
    row = get_invite_code_by_owner(db, owner_user_id)
    return [row] if row else []


def create_invite_code_for_user(db: Session, owner_user_id: int) -> InviteCode:
    existing = get_invite_code_by_owner(db, owner_user_id)
    if existing:
        return existing

    for _ in range(_INVITE_CODE_MAX_ATTEMPTS):
        code = _generate_invite_code_value()
        if get_invite_code_by_code(db, code):
            continue
        row = InviteCode(code=code, owner_user_id=owner_user_id)
        db.add(row)
        try:
            db.commit()
            db.refresh(row)
            return row
        except Exception:
            db.rollback()
            existing = get_invite_code_by_owner(db, owner_user_id)
            if existing:
                return existing

    raise RuntimeError("Failed to generate a unique invite code")


def count_referred_users(db: Session, referrer_user_id: int) -> int:
    return db.query(User).filter(User.referrer_user_id == referrer_user_id).count()


def get_referral_commission_by_order(db: Session, order_id: str) -> Optional[ReferralCommission]:
    return db.query(ReferralCommission).filter(ReferralCommission.order_id == order_id).first()


def create_referral_commission(
    db: Session,
    *,
    referrer_user_id: int,
    referred_user_id: int,
    order_id: str,
    amount: float,
    currency: str,
    available_at: datetime,
) -> ReferralCommission:
    row = ReferralCommission(
        referrer_user_id=referrer_user_id,
        referred_user_id=referred_user_id,
        order_id=order_id,
        amount=amount,
        currency=currency,
        available_at=available_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _credit_commissions_to_wallet(
    db: Session,
    rows: list[ReferralCommission],
    *,
    now: datetime,
) -> None:
    if not rows:
        return

    wallet_deltas: dict[int, float] = {}
    for row in rows:
        row.status = "transferred"
        row.transferred_at = now
        db.add(
            CommissionPayout(
                user_id=row.referrer_user_id,
                amount=row.amount,
                currency=row.currency or "USD",
                created_at=now,
            )
        )
        wallet_deltas[row.referrer_user_id] = wallet_deltas.get(row.referrer_user_id, 0) + row.amount

    for user_id, delta in wallet_deltas.items():
        dbuser = db.query(User).filter(User.id == user_id).first()
        if dbuser:
            dbuser.wallet_balance = round((dbuser.wallet_balance or 0) + delta, 2)
            db.add(dbuser)


def promote_due_referral_commissions(db: Session, referrer_user_id: int | None = None) -> None:
    now = datetime.utcnow()
    pending_q = db.query(ReferralCommission).filter(
        ReferralCommission.status == "pending",
        ReferralCommission.available_at <= now,
    )
    available_q = db.query(ReferralCommission).filter(ReferralCommission.status == "available")
    if referrer_user_id is not None:
        pending_q = pending_q.filter(ReferralCommission.referrer_user_id == referrer_user_id)
        available_q = available_q.filter(ReferralCommission.referrer_user_id == referrer_user_id)

    rows = pending_q.all() + available_q.all()
    if not rows:
        return

    _credit_commissions_to_wallet(db, rows, now=now)
    db.commit()


def get_invite_commission_summary(db: Session, referrer_user_id: int) -> tuple[float, float, float, str]:
    promote_due_referral_commissions(db, referrer_user_id)
    dbuser = db.query(User).filter(User.id == referrer_user_id).first()
    balance = round((dbuser.wallet_balance or 0) if dbuser else 0.0, 2)

    now = datetime.utcnow()
    rows = (
        db.query(ReferralCommission)
        .filter(ReferralCommission.referrer_user_id == referrer_user_id)
        .all()
    )
    currency = "USD"
    pending = 0.0
    total = 0.0
    for row in rows:
        currency = row.currency or currency
        total += row.amount
        if row.status == "pending" and row.available_at > now:
            pending += row.amount
    return balance, round(pending, 2), round(total, 2), currency


def apply_wallet_credit(db: Session, user_id: int, max_amount: float) -> float:
    promote_due_referral_commissions(db, user_id)
    if max_amount <= 0:
        return 0.0

    dbuser = db.query(User).filter(User.id == user_id).first()
    if not dbuser:
        return 0.0

    credit = round(min(dbuser.wallet_balance or 0, max_amount), 2)
    if credit <= 0:
        return 0.0

    dbuser.wallet_balance = round((dbuser.wallet_balance or 0) - credit, 2)
    db.add(dbuser)
    db.commit()
    return credit


def refund_wallet_credit(db: Session, user_id: int, amount: float) -> None:
    if amount <= 0:
        return

    dbuser = db.query(User).filter(User.id == user_id).first()
    if not dbuser:
        return

    dbuser.wallet_balance = round((dbuser.wallet_balance or 0) + amount, 2)
    db.add(dbuser)
    db.commit()


def transfer_referral_commissions(
    db: Session, user_id: int
) -> tuple[float, str, CommissionPayout | None]:
    promote_due_referral_commissions(db, user_id)
    rows = (
        db.query(ReferralCommission)
        .filter(
            ReferralCommission.referrer_user_id == user_id,
            ReferralCommission.status == "available",
        )
        .all()
    )
    if not rows:
        return 0.0, "USD", None

    amount = round(sum(row.amount for row in rows), 2)
    currency = rows[0].currency or "USD"
    now = datetime.utcnow()
    dbuser = db.query(User).filter(User.id == user_id).first()
    if not dbuser:
        return 0.0, currency, None

    for row in rows:
        row.status = "transferred"
        row.transferred_at = now

    dbuser.wallet_balance = round((dbuser.wallet_balance or 0) + amount, 2)
    payout = CommissionPayout(user_id=user_id, amount=amount, currency=currency)
    db.add(payout)
    db.add(dbuser)
    db.commit()
    db.refresh(payout)
    return amount, currency, payout


def list_commission_payouts(db: Session, user_id: int) -> list[CommissionPayout]:
    return (
        db.query(CommissionPayout)
        .filter(CommissionPayout.user_id == user_id)
        .order_by(CommissionPayout.created_at.desc())
        .all()
    )


def get_wallet_redemption(db: Session, user_id: int, coupon_code: str) -> Optional[WalletRedemption]:
    return (
        db.query(WalletRedemption)
        .filter(
            WalletRedemption.user_id == user_id,
            WalletRedemption.coupon_code == coupon_code,
        )
        .first()
    )


def redeem_wallet_coupon(db: Session, user_id: int, coupon_code: str, amount: float) -> WalletRedemption:
    dbuser = db.query(User).filter(User.id == user_id).first()
    if not dbuser:
        raise ValueError("User not found")
    row = WalletRedemption(user_id=user_id, coupon_code=coupon_code, amount=amount)
    dbuser.wallet_balance = round((dbuser.wallet_balance or 0) + amount, 2)
    db.add(row)
    db.add(dbuser)
    db.commit()
    db.refresh(row)
    return row
