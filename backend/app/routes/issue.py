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
                { "$match": { f"{display_type}.project_id": project_id } }
            )

        aggregate += [
            {
                "$lookup": {
                    "from": "issues",
                    "localField": f"{display_type}.issue_id",
                    "foreignField": "id",
                    "as": "issue_info"
                }
            },
            { "$unwind": "$issue_info" },
        ]
        
        if milestone_id != 0:
            aggregate.append(
                { "$match": { "issue_info.milestone.milestone_id": milestone_id } }
            )

        aggregate += [
            {
                "$group": {
                    "_id": "$issue_info.title",
                    "work": {
                        "$push": {
                            "label": f"${display_type}.label",
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
        
        # Sorting the work items by start_time and removing the start_time field from response
        for issue in data:
            issue["work"] = sorted(issue["work"], key=lambda x: x["start_time"])
            for work in issue["work"]:
                work.pop("start_time", None)
        
        # Sorting issues by total_duration
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
        project_id = request.get("project_id")
        user_collection = conn["issues"]
        from datetime import datetime
        current_time = datetime.utcnow()

        # Build the match criteria dynamically
        match_criteria = {}

        if milestone_id and milestone_id != 0:
            match_criteria["milestone.milestone_id"] = milestone_id

        if project_id and project_id != 0:
            match_criteria["project_id"] = project_id

        aggregate = [
            {
                "$match": match_criteria
            },
            {
                "$match": {
                    "milestone": { "$exists": True, "$not": { "$size": 0 } }
                }
            },
            {
                "$addFields": {
                    "total_time": {
                        "$divide": [
                            { "$subtract": [ current_time, "$created_at" ] },
                            1000
                        ]
                    },
                    "assign_time": {
                        "$divide": [
                            { "$sum": {
                                "$map": {
                                    "input": "$assign",
                                    "as": "a",
                                    "in": {
                                        "$cond": [
                                            {"$and": [{"$ne": ["$$a.end_time", None]}, {"$ne": ["$$a.duration", None]}]},
                                            "$$a.duration",
                                            0
                                        ]
                                    }
                                }
                            }},
                            1000
                        ]
                    }
                }
            },
            {
                "$project": {
                    "title": 1,
                    "total_time": 1,
                    "assign_time": 1
                }
            }
        ]

        # Run the aggregation pipeline
        result = user_collection.aggregate(aggregate)
        data = list(result)

        print('total issues in milestone', len(data))

        # Convert _id to string for response
        for d in data:
            d['_id'] = str(d['_id'])

        return {
            "status": True,
            "data": data,
            "message": "Issues fetched successfully",
        }
    except Exception as e:
        return {
            "status": False,
            "data": [],
            "message": str(e)
        }

    
@router.post("/get_issues_info", tags=['issue'])
def get_issues_info(request:dict, conn = Depends(get_connection)):
    issue_id = request.get('issue_id')
    try:
        aggregate = [
            
            {
            '$match':{
                'id':issue_id
            }
            },
            {'$lookup': {
                            'from': 'projects',
                            'localField': 'project_id',
                            'foreignField': 'id',
                            'as': 'result'
                        }},
            {'$unwind':'$result'},
            {'$project':{
                '_id':0,
                    'url':'$url',
                    'name':'$title',
                    'project_url':'$result.web_url',
                'project_name':'$result.name',
                'reopen_count': '$Re-Open',
                    'created_at':'$created_at'
            }}

        ]

        issue_id = request.get("issue_id")
        issues = conn['issues']
        curr_issue = issues.aggregate(aggregate)
        
        data = list(curr_issue)
        
        return {'status':True, 'data':data, 'message':'Successfully got back issues'}
    except Exception as e:
        return {'status':False, 'data':list([]), 'message':str(e)}
    



@router.post("/get_user_total_duration_time", tags=['issue'])
def get_user_total_duration_time(request: dict, conn=Depends(get_connection)):
    issue_id = request.get('issue_id')
    users_collection = conn['users']

    aggregation = [
        { '$unwind': '$work' },
        { '$match': { 'work.issue_id': issue_id }},
        { '$addFields': { 'current_time': { '$toDate': '$$NOW' }}},
        { 
            '$addFields': {
                'isWorkEnd': { '$eq': ['$work.end_time', None] },
                'timeToReturn': {
                    '$cond': {
                        'if': { '$eq': ['$work.end_time', None] },
                        'then': { '$divide': [{ '$subtract': [ '$$NOW', '$work.start_time' ]}, 1000] },
                        'else': '$work.duration'
                    }
                }
            }
        },
        {
            '$group': {
                '_id': '$name',
                'total_time': { '$sum': 1 },
                'total_duration': { '$sum': '$timeToReturn' }
            }
        }
    ]

    response = users_collection.aggregate(aggregation)
    result = list(response)
    total_time = sum(individual_data['total_duration'] for individual_data in result)
    
    for individual_data in result:
        individual_data['percentage'] = (individual_data['total_duration'] * 100) / total_time

    return {
        'status': True,
        'data': result,
        'message': 'Successfully returned user with total_duration and time'
    }



@router.post("/get_user_by_work", tags=['issue'])
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
    

 



def format_duration(seconds):
    # Utility function to convert seconds to a formatted string
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

@router.post("/export_issue_details", tags=['issue'])
def export_issue_details(request: dict, conn=Depends(get_connection)):
    project_id = request.get('project_id')
    issue_id = request.get('issue_id')

    user_collection = conn['users']
    issue_collection = conn['issues']
