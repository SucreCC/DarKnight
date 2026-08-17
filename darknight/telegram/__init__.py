"""Telegram 通知（占位模块，待实现具体推送逻辑）。"""

from typing import Any, Optional


def _noop(*args: Any, **kwargs: Any) -> None:
    pass


report_status_change = _noop
report_new_user = _noop
report_user_modification = _noop
report_user_deletion = _noop
report_user_usage_reset = _noop
report_user_data_reset_by_next = _noop
report_user_subscription_revoked = _noop
report_login = _noop
