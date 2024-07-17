from fastapi import APIRouter, Depends
from app.db import get_connection


router = APIRouter()


@router.post("/work_done", tags=["work"])
async def get_work(conn = Depends(get_connection)):
    try:
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
            {
                "$match": {
                "work.end_time": { "$ne": None }
                }
            },
            {
                "$group": {
                "_id": "$username",
                "work_done_count": { "$sum": 1 }
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/work_duration", tags=["work"])
async def get_work_duration(conn = Depends(get_connection)):
    try:
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
            {
                "$match": {
                "work.end_time": { "$ne": None }
                }
            },
            {
                "$group": {
                "_id": "$username",
                "total_duration": { "$sum": "$work.duration" }
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/ongoing_work", tags=["work"])
async def get_ongoing_work(conn = Depends(get_connection)):
    try:
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
            {
                "$match": {
                "work.end_time": None
                }
            },
            {
                "$group": {
                "_id": "$username",
                "ongoing_work_count": { "$sum": 1 }
                }
            }
        ]
        result = user_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/work_duration_by_task", tags=["work"])
async def get_work_duration_by_task(conn = Depends(get_connection)):
    try:
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
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
async def get_ongoing_task(conn = Depends(get_connection)):
    try:
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
            {
                "$match": {
                    "work.end_time": None
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
async def get_user_work_done_list(conn = Depends(get_connection)):
    try:
        user_collection = conn["users"]
        aggregate = [
            {
                "$unwind": "$work"
            },
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
                        "username": "$username",
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
async def get_assignee_task_list(conn = Depends(get_connection)):
    try:
        issues_collection = conn["issues"]
        aggregate = [
            {
                "$unwind": "$assign"
            },
            {
                "$match": {
                    "assign.end_time": { "$eq": None }
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "assign.user_id",
                    "foreignField": "id",
                    "as": "user_info"
                }
            },
            {
                "$unwind": "$user_info"
            },
            {
                "$project": {
                    "_id": 0,
                    "title": "$title",
                    "username": "$user_info.username"
                }
            }
        ]
        result = issues_collection.aggregate(aggregate)
        return { "status": True, "data": list(result) , "message": "Work fetched successfully" }
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    