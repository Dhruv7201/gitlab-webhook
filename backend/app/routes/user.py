from fastapi import APIRouter, Depends
from app.db import get_connection
from typing import Dict, Any
from app.utils.date_utils import format_duration, formate_date_range
import requests
import os
from datetime import datetime

router = APIRouter()

@router.post("/users")
async def read_user(db=Depends(get_connection)):
    try :
        user_collection = db["users"]
        users = user_collection.find({}, {"name": 1, "username": 1, '_id':1})
        user_response = []
        for user in users:
            user_response.append({
                'id': str(user['_id']),
                'name': user['name'],
                'username': user['username']
            })

        
        return {"status": True, "data": user_response, "message":"Fetch User successfully"}
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    

@router.post("/all_users")
async def read_all_user(db=Depends(get_connection)):
    try :
        user_collection = db["users"]
        # get all the users
        users = user_collection.find({})
        user_response = []
        for user in users:
            if not 'work' in user:
                continue
            if 'assign_issues' not in user:
                user['assign_issues'] = []
            total_assign = len(user['assign_issues'])
            if 'work' not in user:
                user['work'] = []
            total_work = len(user['work'])
            user_response.append({
                'id': user['id'],
                'name': user['name'],
                'avatar_url': user['avatar_url'],
                'username': user['username'],
                'email': user['email'],
                'total_assign': total_assign,
                'total_work': total_work
            })

        user_response = sorted(user_response, key=lambda x: x['name'])

        
        
        return {"status": True, "data": user_response, "message":"Fetch User successfully"}
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    


def get_gitlab_subgroup(project_id: int) -> str:
    try:
        # Replace with your GitLab instance URL and API token
        gitlab_url = "https://code.ethicsinfotech.in/api/v4"
        api_token = os.getenv("GITLAB_KEY")

        response = requests.get(
            f"{gitlab_url}/projects/{project_id}",
            headers={"PRIVATE-TOKEN": api_token}
        )
        response.raise_for_status()  # Raise an error if the request failed

        project_data = response.json()
        # Extract subgroup name from project data
        if 'namespace' in project_data:
            return project_data['namespace']['name']
        return "Unknown"
    except Exception as e:
        return "Unknown"
    

@router.post("/projects")
async def read_user(db=Depends(get_connection)):
    try:
        projects_collection = db["projects"]
        projects = projects_collection.find({}, {"name": 1, "id": 1, "subgroup_name": 1})
        user_response = []
        
        for project in projects:
            if 'subgroup_name' not in project:
                subgroup_name = get_gitlab_subgroup(project['id'])
                projects_collection.update_one(
                    {"_id": project['_id']},
                    {"$set": {"subgroup_name": subgroup_name}}
                )
                full_project_name = f"{subgroup_name}/{project['name']}"
                user_response.append({
                    'id': str(project['id']),
                    'name': full_project_name
                })
            else:
                full_project_name = f"{project['subgroup_name']}/{project['name']}"
                user_response.append({
                    'id': str(project['id']),
                    'name': full_project_name
                })

        return {"status": True, "data": user_response, 'message': 'Fetch Project Successfully'}
    
    except Exception as e:
        return {"status": False, 'data': [], 'message': str(e)}


@router.post("/work")
async def read_work(request:dict, db=Depends(get_connection)) -> Dict[str, Any]:
    try:
       
        username = request.get("username")
        user_collection = db["users"]
        issue_collection = db["issues"]
        project_collection = db["projects"]
        
        user = user_collection.find_one({"username": username})
        if not user:
            return {"error": "User not found"}
        
        work_logs = user.get("work", [])
        project_data = {}
        
        for log in work_logs:

            issue_id = log["issue_id"]
            duration = log.get("duration") if log.get("duration") else 0
            
            issue_id = int(issue_id)
            issue = issue_collection.find_one({"id": issue_id})
    
            if issue is None:
                continue
            
            project_id = issue["project_id"]
            issue_title = issue["title"]
            
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
        return {"status": True, "data": result, "message":"Fetch User successfully"}
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }


@router.post("/donut_labels")
async def get_donut_labels(request:dict, conn = Depends(get_connection)):
    try:
        
        project_id = request.get("project_id")
        user_collection = conn["users"]
        pipeline = [
            {
                "$unwind": "$work"
            },
        ]
        if project_id != 0:
            pipeline.append(
            {
                "$match": {
                    "work.project_id": project_id
                    }
            },
            )
        pipeline.extend([
            {
                "$match": {
                    "work.end_time": {"$eq": None}
                }
            },
            {
                "$group": {
                    "_id": "$work.label", "count": {
                        "$sum": 1
                        }
                    }
                }
            ]
        )

        

        result = user_collection.aggregate(pipeline)

        labels = []
        for res in result:
            
            labels.append({
                'label': res['_id'],
                'count': res['count']
            })

        
        total = sum([label['count'] for label in labels])
        for label in labels:
            label['percentage'] = round((label['count'] / total) * 100, 2)
        
        return { 'status':True, 'data':labels, "message": "Work fetched successfully"}
    
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }
    


@router.post("/user_activity_chart")
async def get_user_activity_chart(request: dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        date_range = request.get("dateRange")
        date_range = formate_date_range(date_range)
        start_date = date_range["from"]
        end_date = date_range["to"]
        user_collection = conn["users"]
        
        completed_pipeline = [
            {"$unwind": "$work"},
            {"$match": {
                "work.end_time": {"$ne": None},
                "work.end_time": {"$gte": start_date, "$lte": end_date}
            }},
            {"$lookup": {
                "from": "projects",
                "localField": "work.issue_id",
                "foreignField": "id",
                "as": "project_info"
            }},
            {"$match": {"work.project_id": project_id if project_id != 0 else {"$exists": True}}},
            {"$group": {
                "_id": "$username", 
                'user_id': {"$first": "$id"}, 
                "completed_count": {"$sum": 1}
            }}
        ]
        
        assigned_pipeline = [
            {"$unwind": "$assign_issues"},
            {"$match": {
                "assign_issues.end_time": {"$ne": None},
                "assign_issues.end_time": {"$gte": start_date, "$lte": end_date}
            }},
            {"$lookup": {
                "from": "projects",
                "localField": "assign_issues.issue_id",
                "foreignField": "id",
                "as": "project_info"
            }},
            {"$match": {"assign_issues.project_id": project_id if project_id != 0 else {"$exists": True}}},
            {"$group": {
                "_id": "$username", 
                'user_id': {"$first": "$id"}, 
                "assigned_count": {"$sum": 1}
            }},
            {"$sort": {"assigned_count": -1}}
        ]
        
        completed_result = list(user_collection.aggregate(completed_pipeline))
        assigned_result = list(user_collection.aggregate(assigned_pipeline))
        all_results = completed_result + assigned_result

        labels = list(set(entry["_id"] for entry in all_results))
        user_map = {}
        for entry in all_results:
            user_id = entry["user_id"]
            label = entry["_id"]
            
            if label not in user_map:
                user_map[label] = {
                    'id': user_id,
                    'completed_count': 0,
                    'assigned_count': 0
                }

        for entry in completed_result:
            label = entry["_id"]
            if label in user_map:
                user_map[label]['completed_count'] = entry['completed_count']

        for entry in assigned_result:
            label = entry["_id"]
            if label in user_map:
                user_map[label]['assigned_count'] = entry['assigned_count']

        completed_issues = [user_map[user]['completed_count'] for user in user_map]
        assigned_issues = [user_map[user]['assigned_count'] for user in user_map]
        user_id = [user_map[user]['id'] for user in user_map]
        labels = list(user_map.keys())

        label = {"labels": labels, "completed_issues": completed_issues, "assigned_issues": assigned_issues, 'user_id': user_id}

        return {'status': True, 'data': label, "message": "Work fetched successfully"}
    
    except Exception as e:
        return {"status": False, "data": list([]), "message": str(e)}



@router.post("/user_time_waste")
async def get_user_time_waste(request: dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
        date_range = request.get("dateRange")
        date_range = formate_date_range(date_range)
        start_date = date_range["from"]
        end_date = date_range["to"]
        user_collection = conn["users"]

        # Define the pipeline
        pipeline = [
            {
                '$unwind': '$assign_issues'
            },
            {
                '$unwind': '$work'
            },
            {
                '$addFields': {
                    'areFieldsEqual': { '$eq': ['$assign_issues.issues_id', '$work.issue_id'] }
                }
            },
            {
                '$match': {
                    'areFieldsEqual': True
                }
            },
            {
                '$match': {
                    '$expr': {
                        '$and': [
                            { '$lt': ['$assign_issues.start_time', '$work.start_time'] },
                            { '$or': [
                                { '$eq': ['$assign_issues.end_time', None] },
                                { '$gt': ['$assign_issues.end_time', '$work.end_time'] }
                            ]}
                        ]
                    }
                }
            },
            {
                '$match': {
                    '$and': [
                        { 'assign_issues.start_time': { '$gte': start_date } },
                        { 'assign_issues.end_time': { '$lte': end_date } },
                        { 'work.start_time': { '$gte': start_date } },
                        { 'work.end_time': { '$lte': end_date } }
                    ]
                }
            },
            {
                '$project': {
                    'name': 1,
                    'id': '$id',
                    'time_waste': {
                        '$subtract': ['$work.start_time', '$assign_issues.start_time']
                    }
                }
            },
            {
                '$group': {
                    '_id': '$name',
                    'id': {'$first': '$id'},
                    'total_time_waste': { '$sum': '$time_waste' }
                }
            },
            {
                "$sort": {"total_time_waste": 1}

            },
            {
                '$project': {
                    'username': '$_id',
                    'user_id': '$id',
                    'total_time_waste': {
                        '$divide': ['$total_time_waste', 1000]
                    }
                }
            }
        ]
        
        if project_id != 0:
            pipeline.insert(0, {
                '$match': {
                    '$or': [
                        { 'assign_issues.project_id': project_id },
                        { 'work.project_id': project_id }
                    ]
                }
            })

        results = list(user_collection.aggregate(pipeline))

        response = [{'name': res['username'], 'user_id': res['user_id'], 'time_waste': res['total_time_waste']} for res in results]
        return {'status': True, 'data': response, 'message': "Work fetched successfully"}

    except Exception as e:
        return {'status': False, 'data': [], 'message': str(e)}



@router.post('/get_all_issues_duration')
def get_all_issues_duration(request: dict, conn=Depends(get_connection)):
    try:
        user_id = request.get('user_id')

        user_connection = conn['users']
        pipeline = [
            {'$match': {'id': user_id}},
            {'$unwind': '$work'},
            {
                '$addFields': {
                    'timeToReturn': {
                        '$cond': {
                            'if': {'$eq': ['$work.end_time', None]},
                            'then': {'$divide': [{'$subtract': ['$$NOW', '$work.start_time']}, 1000]},
                            'else': '$work.duration'
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': '$work.issue_id',
                    'total_time': {
                        '$sum': '$timeToReturn'
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'issues',
                    'localField': '_id',
                    'foreignField': 'id',
                    'as': 'result'
                }
            },
            {
                '$unwind': '$result'
            },
            {
                '$project': {
                    '_id': 0,
                    'issue_id': '$_id',
                    "url": "$result.url",
                    'issue_name': '$result.title',
                    'duration': '$total_time'
                }
            }
        ]
        result = list(user_connection.aggregate(pipeline))
        total_time = sum(res['duration'] for res in result)
        data = [
            {
                'issue_id': res['issue_id'],
                'url': res['url'],
                'issue_name': res['issue_name'],
                'duration': res['duration'],
                'percentage': (res['duration'] * 100) / total_time if total_time > 0 else 0
            } for res in result
        ]
        return {'status': True, 'data': data, 'message': "Data retrieved successfully"}
        
    except Exception as e:
        return {"status": False, "data": [], "message": str(e)}

@router.post("/get_work_duration_time")
def get_work_duration_time(request: Dict[str, Any], conn=Depends(get_connection)):
    try:
        user_connection = conn['users']
        user_id = request.get('userId')

        # Pipeline to aggregate work duration
        pipeline = [
            {'$match': {'id': user_id}},
            {'$unwind': '$work'},
            {
                '$addFields': {
                    'timeToReturn': {
                        '$cond': {
                            'if': {'$eq': ['$work.end_time', None]},
                            'then': {'$divide': [{'$subtract': [datetime.utcnow(), '$work.start_time']}, 1000]},
                            'else': '$work.duration'
                        }
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'issues',
                    'localField': 'work.issue_id',
                    'foreignField': 'id',
                    'as': 'result'
                }
            },
            {'$unwind': '$result'},
            {'$sort': {'work.start_time': 1}},
            {
                '$project': {
                    '_id': 0,
                    'duration': '$timeToReturn',
                    'issue_name': '$result.title',
                    'issue_url': '$result.url',
                    'start_time': '$work.start_time'
                }
            }
        ]

        # Execute the aggregation pipeline
        result = list(user_connection.aggregate(pipeline))

        # Calculate total time and percentage
        total_time = sum(res['duration'] for res in result if res['duration'] is not None)

        # Format result data
        data = [
            {
                'duration': res['duration'],
                'issue_name': res['issue_name'],
                'issue_url': res['issue_url'],
                'start_time': res['start_time'],
                'percentage': (res['duration'] * 100 / total_time) if total_time > 0 else 0
            }
            for res in result
        ]

        return {'status': True, 'data': data, 'message': 'Work and duration for user retrieved successfully'}

    except Exception as e:
        return {'status': False, 'data': [], 'message': f'Error in getting work and duration for user: {str(e)}'}
    
@router.post("/get_user_all_info")
def get_user_all_info(request: dict, conn=Depends(get_connection)):
    try:
        id = request.get('id')
        user_connection = conn['users']
        pipeline = [
            {'$match': {'id': id}},
            {'$addFields': {
                'completed_work': {
                    '$filter': {
                        'input': '$work',
                        'as': 'w',
                        'cond': {'$ne': ['$$w.end_time', None]}
                    }
                }
            }},
            {'$addFields': {
                'completed_issues': {
                    '$filter': {
                        'input': '$assign_issues',
                        'as': 'w',
                        'cond': {'$ne': ['$$w.end_time', None]}
                    }
                }
            }},
            {'$project': {
                '_id': 0,
                'avatar_url': '$avatar_url',
                'name': '$name',
                'username': '$username',
                'email': '$email',
                'all_work': {'$size': {'$ifNull': ['$completed_work', []]}},
                'all_assign': {'$size': {'$ifNull': ['$completed_issues', []]}}
            }},
        ]

        result = list(user_connection.aggregate(pipeline))
        if not result:
            return {'status': False, 'data': [], 'message': 'User not found'}

        result = dict(result[0])

        token = os.getenv('GITLAB_KEY')
        headers = {'PRIVATE-TOKEN': token}
        response = requests.get(f'https://code.ethicsinfotech.in/api/v4/users?username={result["username"]}', headers=headers)
        
        if response.status_code != 200:
            return {'status': False, 'data': [], 'message': f'Error fetching GitLab user info: {response.status_code}'}

        try:
            response_data = response.json()
            if not response_data:
                return {'status': False, 'data': [], 'message': 'No data returned from GitLab API'}
            
            email = response_data[0].get('email', 'Email not found')
            web_url = response_data[0].get('web_url', 'Web URL not found')
            result['email'] = email
            result['web_url'] = web_url

        except ValueError:
            return {'status': False, 'data': [], 'message': 'Invalid JSON response from GitLab API'}

        return {'status': True, 'data': result, 'message': 'Work and duration for user got Successfully'}
    except Exception as e:
        return {'status': False, 'data': [], 'message': str(e)}
