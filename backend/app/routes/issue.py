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
        date_range = request.get("dateRange")
        date_range = formate_date_range(date_range)
        start_date = date_range.get("from")
        end_date = date_range.get("to")
        issue_collection = conn["issues"]

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
                    "milestone": { "$exists": True, "$not": { "$size": 0 } },
                    "created_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
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
                            {
                                "$sum": {
                                    "$map": {
                                        "input": "$assign",
                                        "as": "a",
                                        "in": {
                                            "$cond": [
                                                { "$and": [ { "$ne": ["$$a.duration", None] }, { "$ne": ["$$a.duration", 0] } ] },
                                                "$$a.duration",
                                                0
                                            ]
                                        }
                                    }
                                }
                            },
                            1000
                        ]
                    }
                }
            },
            {
                "$project": {
                    "id": 1,
                    "title": 1,
                    "total_time": 1,
                    "assign_time": 1
                }
            }
        ]

        # Run the aggregation pipeline
        result = issue_collection.aggregate(aggregate)
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
                "$match": {
                    "id": issue_id
                }
            },
            {
                "$lookup": {
                    "from": "projects",
                    "localField": "project_id",
                    "foreignField": "id",
                    "as": "result"
                }
            },
            {
                "$unwind": "$result"
            },
            {
                "$addFields": {
                    "ready_for_release_value": {
                        "$ifNull": ["$ready_for_release", False]
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "url": 1,
                    "name": "$title",
                    "project_url": "$result.web_url",
                    "project_name": "$result.name",
                    "project_subgroup": "$result.subgroup_name",
                    "reopen_count": "$Re-Open",
                    "created_at": 1,
                    "ready_for_release": "$ready_for_release_value"
                }
            }
        ]


        issue_id = request.get("issue_id")
        issues = conn['issues']
        curr_issue = issues.aggregate(aggregate)
        
        data = list(curr_issue)

        # add subgroup as subgroup/project_name
        for issue in data:
            issue['project_name'] = f"{issue['project_subgroup']}/{issue['project_name']}"
            issue.pop('project_subgroup', None)
        
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


@router.post("/get_all_issues", tags=['issue'])
def get_all_issues(conn=Depends(get_connection)):
    # Get all issues ids with work
    issue_collection = conn['issues']

    aggregation = [
        { 
            '$match': { 
                'ready_for_release': { '$exists': False } 
            } 
        },
        { 
            '$lookup': {
                'from': 'projects',
                'localField': 'project_id',
                'foreignField': 'id',
                'as': 'project_info'
            } 
        },
        { 
            '$unwind': '$project_info' 
        },
        { 
            '$project': {
                '_id': 0,
                'issue_id': '$id',
                'title': '$title',
                'issue_url': '$url',
                'project_name': '$project_info.name',
                'project_url': '$project_info.web_url',
                'subgroup_name': '$project_info.subgroup_name'
            } 
        }
    ]

    response = issue_collection.aggregate(aggregation)
    result = list(response)
    # pop object id
    for issue in result:
        issue.pop('_id', None)
    result = sorted(result, key=lambda x: x['title'])

    return {
        'status': True,
        'data': result,
        'message': 'Successfully returned all issues'
    }


@router.post("/get_subgroup_link", tags=['issue'])
def get_subgroup_link(request: dict, conn=Depends(get_connection)):
    subgroup_name = request.get('subgroup_name')
    
    # get subgroup by gitlab rest api

    import requests
    import os

    token = os.getenv('GITLAB_KEY')
    headers = {
        'Private-Token': token
    }
    
    def find_subgroup(subgroup_name, group_id):
        url = f'https://code.ethicsinfotech.in/api/v4/groups/{group_id}/subgroups'
        response = requests.get(url, headers=headers)
        
        # Check for successful response
        if response.status_code != 200:
            return None
        
        subgroups = response.json()
        
        # Ensure subgroups is a list
        if not isinstance(subgroups, list):
            return None
        for subgroup in subgroups:
            # Ensure each item is a dictionary with expected keys
            if isinstance(subgroup, dict) and 'name' in subgroup:
                if subgroup['name'] == subgroup_name:
                    return subgroup
                else:
                    # Recursively search within subgroups
                    nested_subgroup = find_subgroup(subgroup_name, subgroup['id'])
                    if nested_subgroup:
                        return nested_subgroup
        
        return None

    
    group_id = 39
    subgroup = find_subgroup(subgroup_name, group_id)
    subgroup_link = subgroup.get('web_url')
    if subgroup:
        return {
            'status': True,
            'data': subgroup_link,
            'message': 'Successfully returned subgroup'
        }
    else:
        return {
            'status': False,
            'data': {},
            'message': 'Subgroup not found'
        }
    