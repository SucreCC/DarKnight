from darknight.services.config.settings import get_app_config
from darknight.telegram import bot

from telebot import types
from telebot.custom_filters import AdvancedCustomFilter

_telegram = get_app_config().telegram


class IsAdminFilter(AdvancedCustomFilter):
    key = 'is_admin'

    def check(self, message, text):
        """
        :meta private:
        """
        if isinstance(message, types.CallbackQuery):
            return message.from_user.id in _telegram.admin_id
        return message.chat.id in _telegram.admin_id


def cb_query_equals(text: str):
    return lambda query: query.data == text


def cb_query_startswith(text: str):
    return lambda query: query.data.startswith(text)



def setup() -> None:
    bot.add_custom_filter(IsAdminFilter())
