from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._helpers import as_tuple_str


@dataclass(frozen=True)
class FeaturesConfig:
    disable_recording_node_usage: bool = False
    external_config: str = ""
    login_notify_white_list: tuple[str, ...] = ()
    use_custom_json_default: bool = False
    use_custom_json_for_v2rayn: bool = False
    use_custom_json_for_v2rayng: bool = False
    use_custom_json_for_streisand: bool = False
    use_custom_json_for_happ: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> FeaturesConfig:
        data = raw or {}
        return cls(
            disable_recording_node_usage=bool(
                data.get("disable_recording_node_usage", cls.disable_recording_node_usage)
            ),
            external_config=str(data.get("external_config", cls.external_config)),
            login_notify_white_list=as_tuple_str(data.get("login_notify_white_list", [])),
            use_custom_json_default=bool(
                data.get("use_custom_json_default", cls.use_custom_json_default)
            ),
            use_custom_json_for_v2rayn=bool(
                data.get("use_custom_json_for_v2rayn", cls.use_custom_json_for_v2rayn)
            ),
            use_custom_json_for_v2rayng=bool(
                data.get("use_custom_json_for_v2rayng", cls.use_custom_json_for_v2rayng)
            ),
            use_custom_json_for_streisand=bool(
                data.get("use_custom_json_for_streisand", cls.use_custom_json_for_streisand)
            ),
            use_custom_json_for_happ=bool(
                data.get("use_custom_json_for_happ", cls.use_custom_json_for_happ)
            ),
        )


__all__ = ["FeaturesConfig"]
