from datetime import datetime as dt
from datetime import timedelta as td
from typing import Any, Dict, List

from fastapi.encoders import jsonable_encoder
from requests import Session

from darknight.db import GetDB
from darknight.db.models import NotificationReminder
from darknight.utils.notification import queue
from darknight.jobs.manager import JobManager
from darknight.jobs.manager import mgr

session = Session()


def send(data: List[Dict[Any, Any]]) -> bool:
    """Send the notification to the webhook address provided by WEBHOOK_ADDRESS

    Args:
        data (List[Dict[Any, Any]]): list of json encoded notifications

    Returns:
        bool: returns True if an ok response received
    """

    webhook = mgr().config.webhook
    headers = {"x-webhook-secret": webhook.secret} if webhook.secret else None

    result_list = []
    for address in webhook.addresses:
        result = send_req(w_address=address, data=data, headers=headers)
        result_list.append(result)
    if True in result_list:
        return True
    else:
        return False


def send_req(w_address: str, data, headers):
    logger = mgr().logger
    try:
        logger.debug(f"Sending {len(data)} webhook updates to {w_address}")
        r = session.post(w_address, json=data, headers=headers)
        if r.ok:
            return True
        logger.error(r)
    except Exception as err:
        logger.error(err)
    return False


def send_notifications():
    recurrent = mgr().config.notifications.recurrent

    if not queue:
        return

    notifications_to_send = list()
    try:
        while (notification := queue.popleft()):
            if (notification.tries > recurrent.count):
                continue
            if notification.send_at > dt.utcnow().timestamp():
                queue.append(notification)  # add it to the queue again for the next check
                continue
            notifications_to_send.append(notification)
    except IndexError:  # if the queue is empty
        pass

    if not notifications_to_send:
        return
    if not send([jsonable_encoder(notif) for notif in notifications_to_send]):
        for notification in notifications_to_send:
            if (notification.tries + 1) > recurrent.count:
                continue
            notification.tries += 1
            notification.send_at = (  # schedule notification for n seconds later
                dt.utcnow() + td(seconds=recurrent.timeout)).timestamp()
            queue.append(notification)


def delete_expired_reminders() -> None:
    with GetDB() as db:
        db.query(NotificationReminder).filter(NotificationReminder.expires_at < dt.utcnow()).delete()
        db.commit()


def shutdown_send_pending():
    logger = mgr().logger
    logger.info("Sending pending notifications before shutdown...")
    send_notifications()


def register(manager: JobManager) -> None:
    if not manager.config.webhook.addresses:
        return

    jobs = manager.config.jobs
    logger = manager.logger

    manager.on_shutdown(shutdown_send_pending)

    logger.info("Send webhook job started")
    manager.add_job(
        send_notifications,
        "interval",
        seconds=jobs.send_notifications_interval,
        replace_existing=True,
    )
    manager.add_job(
        delete_expired_reminders,
        "interval",
        hours=2,
        start_date=dt.utcnow() + td(minutes=1),
    )
