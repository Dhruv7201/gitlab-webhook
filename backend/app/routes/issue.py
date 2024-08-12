from fastapi import APIRouter, Depends
from app.db import get_connection
from app.utils.date_utils import formate_date_range

router = APIRouter()


@router.post("/issue_lifetime", tags=["issue"])
async def issue_lifetime(request: dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        milestone_id = request.get("milestone_id")
        all_milestones = request.get("all_milestones")
        date_range = request.get("date_range")
        user_collection = conn["users"]

        date_range = formate_date_range(date_range)
            

        aggregate = [
            {
                "$unwind": "$work"
            },
            {
                "$match": { "work.end_time": { "$ne": None } }
            }
        ]

        if date_range.get("from") and date_range.get("to"):
            aggregate.append(
                {
                    "$match": {
                        "work.start_time": {
                            "$gte": date_range["from"],
                            "$lte": date_range["to"]
                        }
                    }
                }
            )

        if project_id is not None and project_id != 0:
            aggregate.append(
                { "$match": { "work.project_id": project_id } }
            )

        aggregate += [
            {
                "$lookup": {
                    "from": "issues",
                    "localField": "work.issue_id",
                    "foreignField": "id",
                    "as": "issue_info"
                }
            },
            { "$unwind": "$issue_info" }
        ]
        
        if milestone_id is not None and milestone_id != 0:
            aggregate.append(
                { "$match": { "issue_info.milestone.milestone_id": milestone_id } }
            )
        else:
            if not all_milestones:
                aggregate.append(
                    { "$match": { "issue_info.milestone.milestone_id": { "$ne": None } } }
                )
            else:
                aggregate.append(
                    { "$match": { "issue_info.milestone.milestone_id": { "$in": all_milestones } } }
                )

        aggregate += [
            {
                "$group": {
                    "_id": "$issue_info.title",
                    "work": {
                        "$push": {
                            "label": "$work.label",
                            "duration": "$work.duration",
                            "start_time": "$work.start_time"
                        }
                    },
                    "total_duration": { "$sum": "$work.duration" },
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


@router.post("/milestone_issues", tags=["issue"])
async def milestone_issues(request: dict, conn = Depends(get_connection)):
    try:
        milestone_id = request.get("milestone_id")
        project_id = request.get("project_id")
        all_milestones = request.get("all_milestones")
        user_collection = conn["issues"]

        # Build the match criteria dynamically
        match_criteria = {}

        if milestone_id and milestone_id != 0:
            match_criteria["milestone.milestone_id"] = milestone_id
        else:
            if not all_milestones:
                match_criteria["milestone.milestone_id"] = { "$ne": None }
            else:
                match_criteria["milestone.milestone_id"] = { "$in": all_milestones }

        if project_id and project_id != 0:
            match_criteria["project_id"] = project_id
        
        # total_time = now - created_at

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
                            { "$subtract": [ "$$NOW", "$created_at" ] },
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
                    'id':1,
                    "title": 1,
                    "total_time": 1,
                    "assign_time": 1
                }
            }
        ]

        # Run the aggregation pipeline
        result = user_collection.aggregate(aggregate)
        data = list(result)

        # Convert _id to string for response
        for d in data:
            d['_id'] = str(d['_id'])
            d['total_time'] = d['total_time'] / 60

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


@router.post("/project_issues_report", tags=['issue'])
def project_issues_report(request: dict, conn=Depends(get_connection)):
    project_id = request.get('project_id')
    issues_collection = conn['issues']
    users_collection = conn['users']

    aggregation = [
    { '$match': { 'project_id': project_id }},
    { '$lookup': {
        'from': 'users',
        'localField': 'assign.user_id',
        'foreignField': 'id',
        'as': 'assigned_users'
    }},
    { '$unwind': '$assign' },
    { '$lookup': {
        'from': 'users',
        'localField': 'assign.user_id',
        'foreignField': 'id',
        'as': 'assign_user'
    }},
    { '$unwind': '$assign_user' },
    { '$group': {
        '_id': { 'issue_id': '$id', 'title': '$title' },
        'total_assigned_time': { '$sum': '$assign.duration' },
    }},
    { '$project': {
        '_id': 0,
        'issue_id': '$_id.issue_id',
        'title': '$_id.title',
        'total_assigned_time': 1,
        'total_work_time': 1,
        'total_doing_time': 1,
        'total_testing_time': 1,
        'total_documentation_time': 1,
        'assignee_names': 1
    }}
]


    response = issues_collection.aggregate(aggregation)

    result = list(response)
    return result
