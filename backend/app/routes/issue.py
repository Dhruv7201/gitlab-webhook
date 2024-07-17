from fastapi import APIRouter, Depends
from app.db import get_connection

router = APIRouter()

@router.post("/issue_lifetime", tags=["issue"])
async def issue_lifetime(request: dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$assign_issues"
            },
            {
                "$match": {
                    "assign_issues.end_time": {"$ne": None},
                    "assign_issues.project_id": project_id
                }
            },
            {
                "$lookup": {
                    "from": "issues",
                    "localField": "work.issue_id",
                    "foreignField": "id",
                    "as": "issue_info"
                }
            },
            {
                "$unwind": "$issue_info"
            },
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
        
        return {
            "status": True,
            "data": list(result),
            "message": "Work fetched successfully",
        }
    except Exception as e:
        return {"status": False, "data": list([]), "message": str(e)}
