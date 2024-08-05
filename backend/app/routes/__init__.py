
from app.routes.webhook import router as home_router
from app.routes.user import router as user_router
from app.routes.work import router as work_router
from app.routes.issue import router as issue_router
from app.routes.milestones import router as milestone_router
from app.routes.filter import router as filter_routes


def register_routers(app):
    app.include_router(home_router)
    app.include_router(user_router)
    app.include_router(work_router)
    app.include_router(issue_router)
    app.include_router(milestone_router)
    app.include_router(filter_routes)
