from fastapi import APIRouter

from darknight.api.v1.routers import (
    admin,
    core,
    home,
    node,
    subscription,
    system,
    user,
    user_template,
)
from darknight.services.config import get_app_config

api_prefix = get_app_config().project.api_version
api_router = APIRouter(prefix=api_prefix)

for router in (
    admin.router,
    core.router,
    node.router,
    system.router,
    user_template.router,
    user.router,
):
    api_router.include_router(router)

__all__ = ["api_router", "home", "subscription"]
