from app.routes.webhook import router as home_router
from app.routes.user import router as user_router
from app.routes.work import router as work_router
from app.routes.issue import router as issue_router
from app.routes.milestones import router as milestone_router
from app.routes.filter import router as filter_routes
from app.routes.login import router as login_router
from app.routes.settings import router as settings_router
from app.routes.reports import router as reports_router
from app.routes.release_plan import router as release_plan_router


def register_routers(app):
    app.include_router(home_router)
    app.include_router(user_router)
    app.include_router(work_router)
    app.include_router(issue_router)
    app.include_router(milestone_router)
    app.include_router(filter_routes)
    app.include_router(login_router)
    app.include_router(settings_router)
    app.include_router(reports_router)
    app.include_router(release_plan_router)
