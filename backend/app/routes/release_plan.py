from fastapi import APIRouter, Depends
from app.db import get_connection
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()


class DailyReportRequest(BaseModel):
    project_id: int
    selected_date: str


@router.post("/release_plan", tags=["release_plan"])
async def release_plan(
    report_request: DailyReportRequest, conn=Depends(get_connection)
):
    selected_date = datetime.strptime(report_request.selected_date, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59
    )

    issues_collection = conn["issues"]
    query = {"work.label": "ReleasePlan", "work.start_time": {"$lt": selected_date}}
    all_issues = list(issues_collection.find(query))

    projects_collection = conn["projects"]
    all_projects = {
        project["id"]: project["name"] for project in projects_collection.find()
    }

    filtered_issues = []
    for issue in all_issues:
        issue.pop("_id", None)

        project_id = issue.get("project_id")
        issue["project_name"] = all_projects.get(project_id)

        work_items = issue.get("work", [])
        if work_items:
            issue["status"] = work_items[-1]["label"]

        project_list = [
            "id",
            "iid",
            "title",
            "due_date",
            "url",
            "created_at",
            "project_name",
            "status",
        ]
        filtered_issue = {k: issue[k] for k in project_list if k in issue}

        filtered_issues.append(filtered_issue)

    return filtered_issues
