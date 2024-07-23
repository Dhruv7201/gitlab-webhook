from fastapi import APIRouter, Depends, Request
from app.db import get_connection

router = APIRouter()


@router.post("/work_done", tags=["work"])
async def get_work(request:dict, conn = Depends(get_connection)):
    try:
        
        project_id = request.get("project_id")
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            }]
        if project_id != 0:
            aggregate.append(
                {
                    "$match": {
                        "work.end_time": { "$ne": None },
                        "work.project_id": project_id
                    }
                }
            )
        aggregate += [
            {
                "$match": {
                "work.end_time": { "$ne": None }
                }
            },
            {
                "$group": {
                "_id": "$name",
                "work_done_count": { "$sum": 1 }
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/work_duration", tags=["work"])
async def get_work_duration(request:dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
            {
                "$match": {
                "work.end_time": { "$ne": None },
                "work.project_id": project_id
                }
            },
            {
                "$group": {
                "_id": "$name",
                "total_duration": { "$sum": "$work.duration" }
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/ongoing_work", tags=["work"])
async def get_ongoing_work(request:dict, conn = Depends(get_connection)):
    try:

        project_id = request.get("project_id")
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
            {
                "$match": {
                "work.end_time": None,
                "work.project_id": project_id
                }
            },
            {
                "$group": {
                "_id": "$name",
                "ongoing_work_count": { "$sum": 1 }
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/work_duration_by_task", tags=["work"])
async def get_work_duration_by_task(request:dict, conn = Depends(get_connection)):
    try:

        project_id = request.get("project_id")
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            }]
        if project_id != 0:
            aggregate.append(
                {
                    "$match": {
                        "work.end_time": { "$ne": None },
                        "work.project_id": project_id
                    }
                }
            )
        aggregate += [
            {
                "$match": {
                    "work.end_time": { "$ne": None }
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
                    "total_duration": { 
                        "$sum": "$work.duration"
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "title": "$_id",
                    "total_duration": 1
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/ongoing_task", tags=["work"])
async def get_ongoing_task(request:dict, conn = Depends(get_connection)):
    try:
        
        project_id = request.get("project_id")
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
            {
                "$match": {
                    "work.end_time": None,
                    "work.project_id": project_id    
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
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "title": "$_id",
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/user_work_done_list", tags=["work"])
async def get_user_work_done_list(request:dict, conn = Depends(get_connection)):
    try:

        project_id = request.get("project_id")
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            }]
        if project_id != 0:
            aggregate.append(
                {
                    "$match": {
                        "work.end_time": { "$ne": None },
                        "work.project_id": project_id
                    }
                }
            )
        aggregate += [
            {
                "$match": {
                    "work.end_time": { "$ne": None }
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
                    "_id": {
                        "username": "$name",
                        "issue_id": "$work.issue_id"
                    },
                    "total_duration": { "$sum": "$work.duration" },
                    "issue_title": { "$first": "$issue_info.title" }
                }
            },
            {
                "$group": {
                    "_id": "$_id.username",
                    "issues": {
                        "$push": {
                            "issue_title": "$issue_title",
                            "total_duration": "$total_duration"
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "username": "$_id",
                    "issues": 1
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/assignee_task_list", tags=["work"])
async def get_assignee_task_list(request: dict, conn=Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        issues_collection = conn["issues"]
        
        aggregate = []
        
        if project_id != 0:
            aggregate.append({
                "$match": {
                    "project_id": project_id
                }
            })
        
        aggregate += [
            {
                "$unwind": "$assign"
            },
            {
                "$match": {
                    "assign.end_time": None
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "assign.id",
                    "foreignField": "id",
                    "as": "assignee_info"
                }
            },
            {
                "$unwind": "$assignee_info"
            },
            {
                "$group": {
                    "_id": "$assign.id",
                    "issues": {
                        "$push": {
                            "username": "$assignee_info.username",
                            "title": "$title"
                        }
                    }
                }
            }
        ]

        result = list(issues_collection.aggregate(aggregate))


        return {
            "status": True,
            "data": result,
            "message": "Work fetched successfully"
        }
    except Exception as e:
        return {
            "status": False,
            "data": [],
            "message": str(e)
        }
