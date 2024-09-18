from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import httpx

router = APIRouter()

async def get_connection() -> AsyncIOMotorClient:
    # Replace with your MongoDB connection details
    mongo_url = os.getenv("DATABASE_URL")
    client = AsyncIOMotorClient(mongo_url)
    return client['GitlabReports']

@router.get("/milestones")
async def read_milestones(db=Depends(get_connection)) -> dict:
    gitlab_token = os.getenv("GITLAB_KEY")
    headers = {
        'PRIVATE-TOKEN': gitlab_token,
    }
    
    base_url = 'https://code.ethicsinfotech.in/api/v4/groups/39/milestones'
    milestone_collection = db["milestones"]

    existing_milestones = await milestone_collection.find().to_list(None)
    existing_ids = {milestone['id'] for milestone in existing_milestones}


    

    all_milestones = []
    page = 1

    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(base_url, headers=headers, params={'page': page, 'per_page': 100})

            if response.status_code != 200:
                return {"status": False, "message": f"Failed to fetch milestones: {response.status_code}"}

            milestones = response.json()
            if not milestones:
                break

            new_milestones = [milestone for milestone in milestones if milestone['id'] not in existing_ids]
            if new_milestones:
                await milestone_collection.insert_many(new_milestones)
                existing_ids.update(milestone['id'] for milestone in new_milestones)
            
            all_milestones.extend(milestones)
            page += 1

    # Remove _id from the response
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
    
    results = await milestone_collection.aggregate(aggregate).to_list(None)
    
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
        issues = await issues_collection.aggregate(pipeline).to_list(None)
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
    try:
        # Get all active milestones from the database
        await read_milestones(db)
        milestone_collection = db["milestones"]
        
        # Fetch active milestones asynchronously
        active_milestones = []
        async for milestone in milestone_collection.find({"state": "active"}):
            milestone.pop('_id', None)
            active_milestones.append(milestone)
            # check date of milestone if exceeded
            milestone_due_date = datetime.strptime(milestone['due_date'], "%Y-%m-%d")
            today = datetime.now()
            today = today.replace(hour=0, minute=0, second=0, microsecond=0)
            if milestone_due_date < today:
                milestone['title'] = milestone['title'] + " (Expired)"
            else:
                milestone['status'] = 'Active'
        # remove duplicate milestone
        active_milestones = [dict(t) for t in {tuple(d.items()) for d in active_milestones}]
        return {
            "status": True,
            "data": active_milestones,
            "message": "Active milestones fetched successfully"
        }
    except Exception as e:
        return {
            "status": False,
            "data": list([]),
            "message": str(e)
        }
