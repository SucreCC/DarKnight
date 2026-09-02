from functools import lru_cache
import logging
import sys
from typing import TYPE_CHECKING, Union

from sqlalchemy.exc import SQLAlchemyError

from darknight.db import GetDB, crud
from darknight.models.node import NodeStatus
from darknight.models.user import UserResponse
from darknight.utils.concurrency import threaded_function
from darknight.xray.node import XRayNode
from xray_api import XRay as XRayAPI
from xray_api.types.account import Account, XTLSFlows

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import darknight.xray as xray

    from darknight.db import User as DBUser
    from darknight.db.models import Node as DBNode

DBUserRef = Union["DBUser", str]


def _username_from_dbuser(dbuser: DBUserRef) -> str:
    return dbuser if isinstance(dbuser, str) else dbuser.username


def _load_user_response(username: str) -> tuple[UserResponse, str] | None:
    """Load a user for xray sync inside a fresh DB session."""
    with GetDB() as db:
        dbuser = crud.get_user(db, username)
        if not dbuser:
            logger.warning("xray user op: user %s not found", username)
            return None
        # Warm lazy relationships before the session closes.
        _ = dbuser.proxies
        _ = dbuser.usage_logs
        user = UserResponse.model_validate(dbuser)
        email = f"{dbuser.id}.{dbuser.username}"
        return user, email


def _load_user_email(username: str) -> str | None:
    with GetDB() as db:
        dbuser = crud.get_user(db, username)
        if not dbuser:
            logger.warning("xray user op: user %s not found", username)
            return None
        return f"{dbuser.id}.{dbuser.username}"


def _xray():
    return sys.modules["darknight.xray"]


@lru_cache(maxsize=None)
def get_tls():
    from darknight.db import GetDB, get_tls_certificate
    with GetDB() as db:
        tls = get_tls_certificate(db)
        return {
            "key": tls.key,
            "certificate": tls.certificate
        }


@threaded_function
def _add_user_to_inbound(api: XRayAPI, inbound_tag: str, account: Account):
    try:
        api.add_inbound_user(tag=inbound_tag, user=account, timeout=30)
    except (_xray().exc.EmailExistsError, _xray().exc.ConnectionError):
        pass


@threaded_function
def _remove_user_from_inbound(api: XRayAPI, inbound_tag: str, email: str):
    try:
        api.remove_inbound_user(tag=inbound_tag, email=email, timeout=30)
    except (_xray().exc.EmailNotFoundError, _xray().exc.ConnectionError):
        pass


@threaded_function
def _alter_inbound_user(api: XRayAPI, inbound_tag: str, account: Account):
    try:
        api.remove_inbound_user(tag=inbound_tag, email=account.email, timeout=30)
    except (_xray().exc.EmailNotFoundError, _xray().exc.ConnectionError):
        pass
    try:
        api.add_inbound_user(tag=inbound_tag, user=account, timeout=30)
    except (_xray().exc.EmailExistsError, _xray().exc.ConnectionError):
        pass


def add_user(dbuser: DBUserRef):
    loaded = _load_user_response(_username_from_dbuser(dbuser))
    if not loaded:
        return
    user, email = loaded

    for proxy_type, inbound_tags in user.inbounds.items():
        for inbound_tag in inbound_tags:
            inbound = _xray().config.inbounds_by_tag.get(inbound_tag, {})

            try:
                proxy_settings = user.proxies[proxy_type].dict(no_obj=True)
            except KeyError:
                pass
            account = proxy_type.account_model(email=email, **proxy_settings)

            # XTLS currently only supports transmission methods of TCP and mKCP
            if getattr(account, 'flow', None) and (
                inbound.get('network', 'tcp') not in ('tcp', 'kcp')
                or
                (
                    inbound.get('network', 'tcp') in ('tcp', 'kcp')
                    and
                    inbound.get('tls') not in ('tls', 'reality')
                )
                or
                inbound.get('header_type') == 'http'
            ):
                account.flow = XTLSFlows.NONE

            _add_user_to_inbound(_xray().api, inbound_tag, account)  # main core
            for node in list(_xray().nodes.values()):
                if node.connected and node.started:
                    _add_user_to_inbound(node.api, inbound_tag, account)


def remove_user(dbuser: DBUserRef):
    email = _load_user_email(_username_from_dbuser(dbuser))
    if not email:
        return

    for inbound_tag in _xray().config.inbounds_by_tag:
        _remove_user_from_inbound(_xray().api, inbound_tag, email)
        for node in list(_xray().nodes.values()):
            if node.connected and node.started:
                _remove_user_from_inbound(node.api, inbound_tag, email)


def update_user(dbuser: DBUserRef):
    loaded = _load_user_response(_username_from_dbuser(dbuser))
    if not loaded:
        return
    user, email = loaded

    active_inbounds = []
    for proxy_type, inbound_tags in user.inbounds.items():
        for inbound_tag in inbound_tags:
            active_inbounds.append(inbound_tag)
            inbound = _xray().config.inbounds_by_tag.get(inbound_tag, {})

            try:
                proxy_settings = user.proxies[proxy_type].dict(no_obj=True)
            except KeyError:
                pass
            account = proxy_type.account_model(email=email, **proxy_settings)

            # XTLS currently only supports transmission methods of TCP and mKCP
            if getattr(account, 'flow', None) and (
                inbound.get('network', 'tcp') not in ('tcp', 'kcp')
                or
                (
                    inbound.get('network', 'tcp') in ('tcp', 'kcp')
                    and
                    inbound.get('tls') not in ('tls', 'reality')
                )
                or
                inbound.get('header_type') == 'http'
            ):
                account.flow = XTLSFlows.NONE

            _alter_inbound_user(_xray().api, inbound_tag, account)  # main core
            for node in list(_xray().nodes.values()):
                if node.connected and node.started:
                    _alter_inbound_user(node.api, inbound_tag, account)

    for inbound_tag in _xray().config.inbounds_by_tag:
        if inbound_tag in active_inbounds:
            continue
        # remove disabled inbounds
        _remove_user_from_inbound(_xray().api, inbound_tag, email)
        for node in list(_xray().nodes.values()):
            if node.connected and node.started:
                _remove_user_from_inbound(node.api, inbound_tag, email)


def remove_node(node_id: int):
    if node_id in _xray().nodes:
        try:
            _xray().nodes[node_id].disconnect()
        except Exception:
            pass
        finally:
            try:
                del _xray().nodes[node_id]
            except KeyError:
                pass


def add_node(dbnode: "DBNode"):
    remove_node(dbnode.id)

    tls = get_tls()
    _xray().nodes[dbnode.id] = XRayNode(address=dbnode.address,
                                     port=dbnode.port,
                                     api_port=dbnode.api_port,
                                     ssl_key=tls['key'],
                                     ssl_cert=tls['certificate'],
                                     usage_coefficient=dbnode.usage_coefficient)

    return _xray().nodes[dbnode.id]


def _change_node_status(node_id: int, status: NodeStatus, message: str = None, version: str = None):
    with GetDB() as db:
        try:
            dbnode = crud.get_node_by_id(db, node_id)
            if not dbnode:
                return

            if dbnode.status == NodeStatus.disabled:
                remove_node(dbnode.id)
                return

            crud.update_node_status(db, dbnode, status, message, version)
        except SQLAlchemyError:
            db.rollback()


global _connecting_nodes
_connecting_nodes = {}


@threaded_function
def connect_node(node_id, config=None):
    global _connecting_nodes

    if _connecting_nodes.get(node_id):
        return

    with GetDB() as db:
        dbnode = crud.get_node_by_id(db, node_id)

    if not dbnode:
        return

    try:
        node = _xray().nodes[dbnode.id]
        assert node.connected
    except (KeyError, AssertionError):
        node = add_node(dbnode)

    try:
        _connecting_nodes[node_id] = True

        _change_node_status(node_id, NodeStatus.connecting)
        logger.info(f"Connecting to \"{dbnode.name}\" node")

        if config is None:
            config = _xray().config.include_db_users()

        node.start(config)
        version = node.get_version()
        _change_node_status(node_id, NodeStatus.connected, version=version)
        logger.info(f"Connected to \"{dbnode.name}\" node, xray run on v{version}")

    except Exception as e:
        _change_node_status(node_id, NodeStatus.error, message=str(e))
        logger.info(f"Unable to connect to \"{dbnode.name}\" node")

    finally:
        try:
            del _connecting_nodes[node_id]
        except KeyError:
            pass


@threaded_function
def restart_node(node_id, config=None):
    with GetDB() as db:
        dbnode = crud.get_node_by_id(db, node_id)

    if not dbnode:
        return

    try:
        node = _xray().nodes[dbnode.id]
    except KeyError:
        node = add_node(dbnode)

    if not node.connected:
        return connect_node(node_id, config)

    try:
        logger.info(f"Restarting Xray core of \"{dbnode.name}\" node")

        if config is None:
            config = _xray().config.include_db_users()

        node.restart(config)
        logger.info(f"Xray core of \"{dbnode.name}\" node restarted")
    except Exception as e:
        _change_node_status(node_id, NodeStatus.error, message=str(e))
        logger.info(f"Unable to restart node {node_id}")
        try:
            node.disconnect()
        except Exception:
            pass


__all__ = [
    "add_user",
    "remove_user",
    "add_node",
    "remove_node",
    "connect_node",
    "restart_node",
]
