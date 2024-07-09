
from app.routes.webhook import router as home_router
from app.routes.user import router as user_router


def register_routers(app):
    app.include_router(home_router)
    app.include_router(user_router)
