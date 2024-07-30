from fastapi import APIRouter, Depends
from app.db import get_connection

router = APIRouter()
@router.post("/issue_lifetime", tags=["issue"])
async def issue_lifetime(request: dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        milestone_id = request.get("milestone_id")
        user_collection = conn["users"]
        display_type = "work"

        aggregate = [
            { "$unwind": f"${display_type}" },
            { "$match": { f"{display_type}.end_time": { "$ne": None } } }
        ]

        if project_id != 0:
            aggregate.append(
                {
                    "$match": {
                        f"{display_type}.project_id": project_id
                    }
                }
            )

        aggregate += [
            {
                "$lookup": {
                    "from": "issues",
                    "localField": "work.issue_id" if display_type == "work" else f"{display_type}.issues_id",
                    "foreignField": "id",
                    "as": "issue_info"
                }
            },
            { "$unwind": "$issue_info" },
        ]
        
        if milestone_id != 0:
            aggregate.append(
                {
                    "$match": {
                        "issue_info.milestone.milestone_id": milestone_id
                    }
                }
            )

        aggregate += [
            {
                "$group": {
                    "_id": "$issue_info.title",
                    "work": {
                        "$push": {
                            "label": "$work.label" if display_type == "work" else f"${display_type}.label",
                            "duration": f"${display_type}.duration",
                            "start_time": f"${display_type}.start_time"
                        }
                    },
                    "total_duration": { "$sum": f"${display_type}.duration" },
                    "id": { "$first": "$issue_info.id" }
                }
            },
            {
                "$addFields": {
                    "work": {
                        "$map": {
                            "input": "$work",
                            "as": "item",
                            "in": {
                                "label": "$$item.label",
                                "duration": "$$item.duration",
                                "start_time": "$$item.start_time"
                            }
                        }
                    }
                }
            }
        ]

        result = user_collection.aggregate(aggregate)
        data = list(result)
        
        for issue in data:
            issue["work"] = sorted(issue["work"], key=lambda x: x["start_time"])
            for work in issue["work"]:
                work.pop("start_time", None)
        
        
        data = sorted(data, key=lambda x: x["total_duration"])

        
        formatted_data = [
            {
                "title": issue["_id"],
                "work": issue["work"],
                "total": issue["total_duration"],
                "id": issue["id"]
            }
            for issue in data
        ]
        
        return {
            "status": True,
            "data": formatted_data,
            "message": "Issues fetched successfully",
        }
    except Exception as e:
        return {"status": False, "data": [], "message": str(e)}





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





@router.post("/milestone_issues", tags=["issue"])
async def milestone_issues(request: dict, conn = Depends(get_connection)):
    try:
        milestone_id = request.get("milestone_id")
        user_collection = conn["issues"]
        # get issue total time by date time now - created_at
        aggregate = [
            {
                "$match": {
                    "milestone.milestone_id": milestone_id
                }
            },
            {
                "$project": {
                    "title": 1,
                    "id": 1,
                    "total_time": {
                        "$divide": [
                            { "$subtract": ["$$NOW", "$created_at"] },
                            1000
                        ]
                    },
                    "assign_time": {
                        "$divide": [
                            {
                                "$sum": {
                                    "$map": {
                                        "input": "$assign",
                                        "as": "a",
                                        "in": "$$a.duration"
                                    }
                                }
                            },1000
                        ]
                    }
                }
            }
        ]



        result = user_collection.aggregate(aggregate)
        data = list(result)
        for d in data:
            d['_id'] = str(d['_id'])
        return {
            "status": True,
            "data": data,
            "message": "Issues fetched successfully",
        }
    except Exception as e:
        return {"status": False, "data": list([]), "message": str(e)}