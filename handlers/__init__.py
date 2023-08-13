from aiogram import Router

from .admin import admin_router
from .basic import basic_router
from .client import client_router


routers: list[Router] = [admin_router, basic_router, client_router]


def register_handlers(main_router: Router) -> None:
    for router in routers:
        main_router.include_router(router)