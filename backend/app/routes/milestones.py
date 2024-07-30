from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
import requests
import os

router = APIRouter()

@router.get("/milestones")
async def read_milestones(db=Depends(get_connection)):
    gitlab_token = os.getenv("GITLAB_KEY")
    headers = {
        'PRIVATE-TOKEN': gitlab_token,
    }
    
    base_url = 'https://code.ethicsinfotech.in/api/v4/groups/39/milestones'
    milestone_collection = db["milestones"]
    milestone_collection.delete_many({})

    all_milestones = []

    page = 1
    while True:
        response = requests.get(base_url, headers=headers, params={'page': page, 'per_page': 100})
        if response.status_code != 200:
            break

        milestones = response.json()
        if not milestones:
            break

        for milestone in milestones:
            milestone_collection.insert_one(milestone)
        
        all_milestones.extend(milestones)
        page += 1

    # remove _id from the response
    for milestone in all_milestones:
        milestone.pop('_id', None)

    return {"status": True, "data": all_milestones, "message": "Milestones fetched successfully"}


@router.post("/milestones")
async def get_milestones(request: dict, db=Depends(get_connection)):
    milestone_collection = db["milestones"]

    aggregate = [
        {
            "$group": {
                "_id": "$state",
                "milestones": {
                    "$push": "$$ROOT"
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "state": "$_id",
                "milestones": 1,
            }
        }
    ]

    results = list(milestone_collection.aggregate(aggregate))
    
    ongoing_milestones = []
    completed_milestones = []
    all_milestones = []

    for result in results:
        for milestone in result['milestones']:
            milestone_data = {
                'title': milestone['title'],
                'start_date': milestone['start_date'],
                'due_date': milestone['due_date'],
                'web_url': milestone['web_url'],
                'id': milestone['id']
            }
            if milestone['state'] == 'active':
                ongoing_milestones.append(milestone_data)
            else:
                completed_milestones.append(milestone_data)
            all_milestones.append(milestone_data)
    issues_collection = db["issues"]
    for ongoing_milestone in ongoing_milestones:
        # get issues for each milestone
        pipeline = [
            {
                "$match": {
                    "milestone.milestone_id": ongoing_milestone['id']
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
        issues = list(issues_collection.aggregate(pipeline))
        ongoing_milestone['issues'] = issues


    return {
        "status": True,
        "data": {
            "ongoing_milestones": ongoing_milestones,
            "completed_milestones": completed_milestones,
            "all_milestones": all_milestones
        },
        "message": "Milestones fetched successfully"
    }


@router.post("/active_milestones")
async def get_active_milestones(db=Depends(get_connection)):
    # get all active milestones from the database
    milestone_collection = db["milestones"]
    milestones = list(milestone_collection.find({"state": "active"}))
    for milestone in milestones:
        milestone.pop('_id', None)
    return {
        "status": True,
        "data": milestones,
        "message": "Active milestones fetched successfully"
    }
    