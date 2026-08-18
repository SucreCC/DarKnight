import logging

from darknight.db import GetDB, crud
from darknight.models.admin import Admin
from darknight.utils import report
from darknight.jobs.manager import JobManager
from darknight.jobs.manager import mgr

SYSTEM_ADMIN = Admin(username='system', is_sudo=True, telegram_id=None, discord_webhook=None)


def remove_expired_users():
    logger = mgr().logger
    include_limited = mgr().config.users.autodelete_include_limited_accounts

    with GetDB() as db:
        deleted_users = crud.autodelete_expired_users(db, include_limited)

        for user in deleted_users:
            report.user_deleted(user.username, SYSTEM_ADMIN,
                                user_admin=Admin.model_validate(user.admin) if user.admin else None
                                )
            logger.log(logging.INFO, "Expired user %s deleted." % user.username)


def register(manager: JobManager) -> None:
    manager.add_job(remove_expired_users, "interval", coalesce=True, hours=6, max_instances=1)
