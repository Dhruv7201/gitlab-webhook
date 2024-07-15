from fastapi import APIRouter, Depends
from app.db import get_connection
from typing import Dict, Any
from app.utils.date_utils import format_duration
from pydantic import BaseModel
from fastapi import HTTPException


router = APIRouter()

@router.get("/users")
async def read_user(db=Depends(get_connection)):
    user_collection = db["users"]
    # get distinct users and their name and username
    users = user_collection.find({}, {"name": 1, "username": 1, '_id':1})
    user_response = []
    
    for user in users:
        user_response.append({
            'id': str(user['_id']),
            'name': user['name'],
            'username': user['username']
        })

    
    return {"status": True, "data": user_response}

@router.get("/projects")
async def read_user(db=Depends(get_connection)):
    user_collection = db["projects"]
    # get distinct users and their name and username
    projects = user_collection.find({}, {"name": 1, "id":1, '_id':1})
    user_response = []
    
    for project in projects:
        user_response.append({
            'id': str(project['id']),
            'name': project['name']
        })

    
    return {"status": True, "data": user_response}

@router.get("/work/{username}")
async def read_work(username: str, db=Depends(get_connection)) -> Dict[str, Any]:
    user_collection = db["users"]
    issue_collection = db["issues"]
    project_collection = db["projects"]
    # Retrieve user data
    user = user_collection.find_one({"username": username})
    if not user:
        return {"error": "User not found"}
    
    work_logs = user.get("work", [])
    # print(work_logs)
    # Initialize data structures for aggregation
    project_data = {}
    
    for log in work_logs:
        print(log)
        issue_id = log["issue_id"]
        duration = log["duration"]
        
        # Ensure issue_id is an integer
        issue_id = int(issue_id)
        issue = issue_collection.find_one({"id": issue_id})
        print("------------",issue)
        if issue is None:
            continue
        
        project_id = issue["project_id"]
        issue_title = issue["title"]
        
        # Fetch the project name
        project = project_collection.find_one({"id": project_id})
        
        if project is None:
            continue
        
        project_name = project["name"]
        
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
    return result



@router.get("/get-labels")
async def get_labels(db=Depends(get_connection)):
    try:
        # Retrieve all users
        user_collection = db["users"]
        users = user_collection.find()
        
        labels = set()

        for user in users:
            work_entries = user.get('work', [])

            for work in work_entries:
                labels.add(work.get('label', 'Unknown'))
        
        return list(labels)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/worktime/{label}", response_model=list)
async def get_work_time(label: str, db=Depends(get_connection)):
    try:
        # Retrieve all users
        user_collection = db["users"]
        users = user_collection.find()
        
        user_work_times = []

        for user in users:
            total_duration = 0.0
            username = user.get('username', 'Unknown')
            work_entries = user.get('work', [])

            for work in work_entries:
                if work.get('label') == label:
                    total_duration += work.get('duration', 0.0)
            
            user_work_times.append({
                'username': username,
                'total_duration': total_duration
            })
        
        # Filter out users with no work time
        user_work_times = [uwt for uwt in user_work_times if uwt['total_duration'] > 0]

        for uwt in user_work_times:
            uwt['total_duration'] = format_duration(uwt['total_duration'])

        return user_work_times

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/donut_labels")
async def get_donut_labels(db=Depends(get_connection)):
    try:
        pipeline = [
            {"$unwind": "$work"},
            {"$group": {"_id": "$work.label", "count": {"$sum": 1}}}
        ]

        user_collection = db["users"]

        result = user_collection.aggregate(pipeline)

        labels = []
        for res in result:
            labels.append({
                'label': res['_id'],
                'count': res['count']
            })

        # total count
        total = sum([label['count'] for label in labels])
        for label in labels:
            label['percentage'] = round((label['count'] / total) * 100, 2)

        return labels
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/user_activity_chart/{project_id}")
async def get_user_activity_chart(db=Depends(get_connection), project_id: int = 0):
    try:
        user_collection = db["users"]
        
        # Aggregation pipeline for completed issues
        completed_pipeline =[{"$unwind": "$work"},
            {"$match": {"work.end_time": {"$ne":None}}},
            {"$lookup": {
                "from": "projects",
                "localField": "work.issue_id",
                "foreignField": "id",
                "as": "project_info"
            }},
            {"$match": {"work.project_id": project_id}},
            {"$group": {"_id": "$username", "completed_count": {"$sum": 1}}}
           ]
        
        # Aggregation pipeline for assigned issues
        assigned_pipeline =[
            {"$unwind": "$assign_issues"},
            {"$lookup": {
                "from": "projects",
                "localField": "assign_issues.issues_id",
                "foreignField": "id",
                "as": "project_info"
            }},
            {"$match": {"assign_issues.project_id": project_id}},
            {"$group": {"_id": "$username", "assigned_count": {"$sum": 1}}},
            {"$sort": {"assigned_count": -1}}
        ]
        
        completed_result = list(user_collection.aggregate(completed_pipeline))
        
        assigned_result = list(user_collection.aggregate(assigned_pipeline))
        
        labels = list(set([entry["_id"] for entry in completed_result + assigned_result]))
        completed_data = {entry["_id"]: entry["completed_count"] for entry in completed_result}
        assigned_data = {entry["_id"]: entry["assigned_count"] for entry in assigned_result}
        
        completed_issues = [completed_data.get(label, 0) for label in labels]
        assigned_issues = [assigned_data.get(label, 0) for label in labels]
        
        return {"labels": labels, "completed_issues": completed_issues, "assigned_issues": assigned_issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))