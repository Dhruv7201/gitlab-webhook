from fastapi import APIRouter, Depends
from app.db import get_connection
import pandas as pd

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
                "$lookup": {
                    "from": "users",
                    "localField": "assign.user_id",
                    "foreignField": "id",
                    "as": "assignee_info"
                }
            },
            {
                "$unwind": {
                    "path": "$assignee_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$match": {
                    "assign.end_time": None
                }
            },
            {
                "$group": {
                    "_id": "$title",
                    "issue_url": {
                        "$first": "$url"
                    },
                    "assigned": {
                        "$first": {
                            "$cond": {
                                "if": {"$ne": ["$assignee_info", None]},
                                "then": "$assignee_info.name",
                                "else": "not assigned"
                            }
                        }
                    }
                }
            }
        ]

        result = list(issues_collection.aggregate(aggregate))

        response_data = [{"task": doc["_id"], "assigned": doc["assigned"], "issue_url": doc["issue_url"]} for doc in result]

        return {
            "status": True,
            "data": response_data,
            "message": "Work fetched successfully"
        }
    except Exception as e:
        return {
            "status": False,
            "data": [],
            "message": str(e)
        }


@router.post("/get_user_by_work", tags=["work"])
def get_user_by_work(request:dict, conn=Depends(get_connection)):
    issue_id = request.get('issue_id')
    users_collection = conn['users']
    aggregation = [
            {'$unwind':'$work'},
            {'$match':{'work.issue_id':issue_id}},
            {'$sort':{
                'work.start_time':1
            }},
            {
                '$project':{
                '_id':0,
                'name':'$name',
                'started_at':'$work.start_time',
                'label_info':{'start_time':'$work.start_time', 
                                        'label':'$work.label',
                                        'duration':{'$cond':{
                                            'if': {'$ne': ['$work.end_time', None]},
                                        'then':'$work.duration',
                                        'else':{ "$subtract": ["$$NOW", "$work.start_time"] },
                                        
                                        }}
                            }
                            
                    }
            },
        ]

    response =  users_collection.aggregate(aggregation)
    result = list(response)
    total_time = 0
    for individual_data in result:
        total_time += individual_data['label_info']['duration']

    for individual_data in result:
        individual_data['label_info']['percentage'] = (individual_data['label_info']['duration']*100)/total_time
    data = []
    for res in result:
        data.append(res)
    return {'status':True, 'data':data, 'message':'Successfully return user with total_duration and time'}
    

@router.post("/daily_work_report", tags=["work"])
async def get_daily_work_report(request: dict, conn=Depends(get_connection)):
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
                    "user_name": "$name",
                    "issue_id": "$work.issue_id"
                },
                "project_id": { "$first": "$work.project_id" },
                "task_name": { "$first": "$issue_info.title" },
                "label": { "$first": "$work.label" },
                "start_time": { "$min": "$work.start_time" },
                "end_time": { "$max": "$work.end_time" },
                "duration": { "$sum": "$work.duration" },
                "issue_link": { "$first": "$issue_info.url" }
            }
        },
        {
            "$project": {
                "_id": 0,
                "name": "$_id.user_name",
                "project_id": 1,
                "issue_id": "$_id.issue_id",
                "task_name": 1,
                "label": 1,
                "start_time": 1,
                "end_time": 1,
                "duration": 1,
                "issue_link": 1
            }
        }
    ]

    result = user_collection.aggregate(aggregate)
    data = list(result)

    project_collection = conn["projects"]
    for item in data:
        project_id = item["project_id"]
        project = project_collection.find_one({"id": project_id})
        item["project_name"] = project["name"]
        item["start_time"] = item["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        item["end_time"] = item["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        item["duration"] = item["duration"] / 3600
        item["duration"] = round(item["duration"], 2)

    # Convert data to csv columns as Name, project name, task name, label, start time, end time, duration, issue link
    data = [
        {
            "Name": item["name"],
            "Project Name": item["project_name"],
            "Task ID": item["issue_id"],
            "Task Name": item["task_name"],
            "Label": item["label"],
            "Start Time": item["start_time"],
            "End Time": item["end_time"],
            "Duration": item["duration"],
            "Issue Link": item["issue_link"]
        }
        for item in data
    ]

    # Convert data to cvs and save it to file
    df = pd.DataFrame(data)
    df.to_csv("daily_work_report.csv", index=False)
    


    return {
        "status": True,
        "data": data,
        "message": "Work fetched successfully"
    }