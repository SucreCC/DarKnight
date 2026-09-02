from fastapi import APIRouter

from darknight.api.v1.routers import (
    admin,
    auth,
    core,
    invite,
    node,
    order,
    product,
    profile,
    subscription,
    system,
    ticket,
    user,
    user_template,
)
from darknight.services.config import get_app_config

api_prefix = get_app_config().project.api_version
api_router = APIRouter(prefix=api_prefix)

for router in (
    auth.router,
    admin.router,
    core.router,
    invite.router,
    profile.router,
    node.router,
    system.router,
    user_template.router,
    user.router,
    order.router,
    product.router,
    ticket.router,
):
    api_router.include_router(router)

__all__ = ["api_router", "subscription"]
