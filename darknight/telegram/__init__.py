import importlib.util
from os.path import dirname
from threading import Thread

from fastapi import FastAPI
from telebot import TeleBot, apihelper

from darknight.services.config.settings import get_app_config

_telegram = get_app_config().telegram

bot = None
if _telegram.api_token:
    if _telegram.proxy_url:
        apihelper.proxy = {
            'http': _telegram.proxy_url,
            'https': _telegram.proxy_url,
        }
    bot = TeleBot(_telegram.api_token)

handler_names = ["admin", "report", "user"]


def register(app: FastAPI) -> None:
    @app.on_event("startup")
    def start_bot():
        if bot:
            handler_dir = dirname(__file__) + "/handlers/"
            for name in handler_names:
                spec = importlib.util.spec_from_file_location(name, f"{handler_dir}{name}.py")
                spec.loader.exec_module(importlib.util.module_from_spec(spec))

            from darknight.telegram import utils  # setup custom handlers
            utils.setup()

            thread = Thread(target=bot.infinity_polling, daemon=True)
            thread.start()


from .handlers.report import (  # noqa
    report,
    report_new_user,
    report_user_modification,
    report_user_deletion,
    report_status_change,
    report_user_usage_reset,
    report_user_data_reset_by_next,
    report_user_subscription_revoked,
    report_login
)

__all__ = [
    "bot",
    "register",
    "report",
    "report_new_user",
    "report_user_modification",
    "report_user_deletion",
    "report_status_change",
    "report_user_usage_reset",
    "report_user_data_reset_by_next",
    "report_user_subscription_revoked",
    "report_login"
]
