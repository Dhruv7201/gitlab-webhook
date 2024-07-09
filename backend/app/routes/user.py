from fastapi import APIRouter, Depends
from app.db import get_connection
from bson import ObjectId
from typing import Dict, Any
from app.utils.date_utils import format_duration


router = APIRouter()

@router.get("/users")
async def read_user(db=Depends(get_connection)):
    user_collection = db["users"]
    usernames = user_collection.distinct("username")
    
    users = [{"id": str(ObjectId()), "name": username} for username in usernames]
    return {"users": users}


@router.get("/work/{username}")
async def read_work(username: str, db=Depends(get_connection)) -> Dict[str, Any]:
    user_collection = db["users"]
    issue_collection = db["issue"]
    project_collection = db["projects"]
    
    # Retrieve user data
    user = user_collection.find_one({"username": username})
    if not user:
        return {"error": "User not found"}
    
    work_logs = user.get("work", [])
    
    # Initialize data structures for aggregation
    project_data = {}
    
    for log in work_logs:
        issue_id = log["issue_id"]
        duration = log["duration"]
        print(f"Looking up issue_id: {issue_id}")
        
        # Ensure issue_id is an integer
        issue_id = int(issue_id)
        issue = issue_collection.find_one({"id": issue_id})
        if issue is None:
            print(f"Issue not found for issue_id: {issue_id}")
            continue
        
        project_id = issue["project_id"]
        issue_title = issue["title"]
        print(f"Found issue: {issue_title} for issue_id: {issue_id}")
        
        # Fetch the project name
        project = project_collection.find_one({"id": project_id})
        if project is None:
            print(f"Project not found for project_id: {project_id}")
            continue
        
        project_name = project["name"]
        print(f"Found project: {project_name} for project_id: {project_id}")
        
        if project_name not in project_data:
            project_data[project_name] = {
                "project_name": project_name,
                "project_issues": {},
                "time_spend_on_project": 0
            }
        
        if issue_title not in project_data[project_name]["project_issues"]:
            project_data[project_name]["project_issues"][issue_title] = 0
        
        project_data[project_name]["project_issues"][issue_title] += duration
        project_data[project_name]["time_spend_on_project"] += duration
    
    # Format the response
    result = {
        "data": [
            {
                "project_name": project["project_name"],
                "project_issues": [
                    {
                        "issue_title": issue_title,
                        "time_spend_on_issue": format_duration(duration)
                    }
                    for issue_title, duration in project["project_issues"].items()
                ],
                "time_spend_on_project": format_duration(project["time_spend_on_project"])
            }
            for project in project_data.values()
        ]
    }
    print(result)
    return result
