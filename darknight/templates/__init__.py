from datetime import datetime
from typing import Union

import jinja2

from darknight.services.config.settings import get_app_config

from .filters import CUSTOM_FILTERS

_templates = get_app_config().templates

template_directories = ["darknight/templates"]
if _templates.custom_directory:
    template_directories.insert(0, _templates.custom_directory)

env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_directories))
env.filters.update(CUSTOM_FILTERS)
env.globals['now'] = datetime.utcnow


def render_template(template: str, context: Union[dict, None] = None) -> str:
    return env.get_template(template).render(context or {})
