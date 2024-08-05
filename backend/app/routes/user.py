from fastapi import APIRouter, Depends
from app.db import get_connection
from typing import Dict, Any
from app.utils.date_utils import format_duration

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
    
    

@router.post("/projects")
async def read_user(db=Depends(get_connection)):
    try : 
        user_collection = db["projects"]
        projects = user_collection.find({}, {"name": 1, "id":1, '_id':1})
        user_response = []
        
        for project in projects:
            user_response.append({
                'id': str(project['id']),
                'name': project['name']
            })

        return {"status": True, "data": user_response, 'message':'Fetch Project Successfully'}
    except Exception as e:
        return {"status":False, 'data' :list([]), 'message':e }

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



@router.post("/get-labels")
async def get_labels(db=Depends(get_connection)):
    try:
        user_collection = db["users"]
        users = user_collection.find()
        
        labels = set()

        for user in users:
            work_entries = user.get('work', [])

            for work in work_entries:
                labels.add(work.get('label', 'Unknown'))
    
        return { 'status':True, 'data':list(labels), "message": "Work fetched successfully"}
    
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }

@router.post("/worktime", response_model=list)
async def get_work_time(request:dict, db=Depends(get_connection)):
    try:
       
        label = request.get("label")
        user_collection = db["users"]
        users = user_collection.find()
        
        user_work_times = []

        for user in users:
            total_duration = 0.0
            username = user.get('username', 'Unknown')
            work_entries = user.get('work', [])

            for work in work_entries:
                if work.get('label') == label:
                    total_duration += work.get('duration', 0.0)
            
            user_work_times.append({
                'username': username,
                'total_duration': total_duration
            })
        
        user_work_times = [uwt for uwt in user_work_times if uwt['total_duration'] > 0]

        for uwt in user_work_times:
            uwt['total_duration'] = format_duration(uwt['total_duration'])

        return { 'status':True, 'data':user_work_times, "message": "Work fetched successfully"}
    
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }




@router.post("/donut_labels/")
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
                    "work.end_time": {"$ne": None}
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
async def get_user_activity_chart(request:dict, conn = Depends(get_connection)):
    try:
        
        project_id = request.get("project_id")
        user_collection = conn["users"]
        
        completed_pipeline =[{"$unwind": "$work"},
            {"$match": {"work.end_time": {"$ne":None}}},
            {"$lookup": {
                "from": "projects",
                "localField": "work.issue_id",
                "foreignField": "id",
                "as": "project_info"
            }}
            ]
        if project_id != 0:
            completed_pipeline.append({"$match": {"work.project_id": project_id}})
        completed_pipeline.append(
            {"$group": {"_id": "$username", "completed_count": {"$sum": 1}}},
        )
        
        assigned_pipeline =[
            {"$unwind": "$assign_issues"},
            {"$lookup": {
                "from": "projects",
                "localField": "assign_issues.issue_id",
                "foreignField": "id",
                "as": "project_info"
            }}]
        if project_id != 0:
            assigned_pipeline.append(
            {"$match": {"assign_issues.project_id": project_id}}
            )
        assigned_pipeline += [
        {"$group": {"_id": "$username", "assigned_count": {"$sum": 1}}},
        {"$sort": {"assigned_count": -1}}
        ]
        
        completed_result = list(user_collection.aggregate(completed_pipeline))
        
        assigned_result = list(user_collection.aggregate(assigned_pipeline))
        
        labels = list(set([entry["_id"] for entry in completed_result + assigned_result]))
        completed_data = {entry["_id"]: entry["completed_count"] for entry in completed_result}
        assigned_data = {entry["_id"]: entry["assigned_count"] for entry in assigned_result}
        
        completed_issues = [completed_data.get(label, 0) for label in labels]
        assigned_issues = [assigned_data.get(label, 0) for label in labels]
        
        label = {"labels": labels, "completed_issues": completed_issues, "assigned_issues": assigned_issues}
        return { 'status':True, 'data':label, "message": "Work fetched successfully"}
    
    except Exception as e:
        return { "status": False, "data": list([]), "message": str(e) }


@router.post("/user_time_waste")
async def get_user_activity_chart(request: dict, conn = Depends(get_connection)):
    try:
        project_id = request.get("project_id")
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
                '$project': {
                    'name': 1,
                    'time_waste': {
                        '$subtract': ['$work.start_time', '$assign_issues.start_time']
                    }
                }
            },
            {
                '$group': {
                    '_id': '$name',
                    'total_time_waste': { '$sum': '$time_waste' }
                }
            },
            {
                '$project': {
                    'username': '$_id',
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

        response = [{'name': res['username'], 'time_waste': res['total_time_waste']} for res in results]

        return {'status': True, 'data': response, 'message': "Work fetched successfully"}

    except Exception as e:
        return {'status': False, 'data': [], 'message': str(e)}
