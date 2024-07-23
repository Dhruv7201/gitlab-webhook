from fastapi import APIRouter, Depends
from app.db import get_connection

router = APIRouter()
@router.post("/issue_lifetime", tags=["issue"])
async def issue_lifetime(request: dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        user_collection = conn["users"]
        aggregate = aggregate = [
        { "$unwind": "$assign_issues" },
        ]

        if project_id != 0:
            aggregate.append(
                {
                    "$match": {
                        "assign_issues.end_time": { "$ne": None },
                        "assign_issues.project_id": project_id
                    }
                }
            )

        aggregate += [
            { "$match": { "assign_issues.end_time": { "$ne": None } } },
            {
                "$lookup": {
                    "from": "issues",
                    "localField": "assign_issues.issues_id",
                    "foreignField": "id",
                    "as": "issue_info"
                }
            },
            { "$unwind": "$issue_info" },
            {
                "$group": {
                    "_id": "$issue_info.title",
                    "person_duration": {
                        "$push": {
                            "person": "$name",
                            "duration": "$assign_issues.duration"
                        }
                    }
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        data = list(result)
        print(data)
        return {
            "status": True,
            "data": data,
            "message": "Issues fetched successfully",
        }
    except Exception as e:
        return {"status": False, "data": list([]), "message": str(e)}


@router.post("/issue_status", tags=["issue"])
async def issue_status(request: dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        user_collection = conn["issues"]
        aggregate = [
            {
                "$match": {
                    "project_id": project_id
                }
            },
            {
                "$group": {
                    "_id": "$state",
                    "count": {
                        "$sum": 1
                    }
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        
        return {
            "status": True,
            "data": list(result),
            "message": "Issues fetched successfully",
        }
    except Exception as e:
        return {"status": False, "data": list([]), "message": str(e)}



