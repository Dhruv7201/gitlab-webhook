from typing import Dict
from fastapi import APIRouter, Depends, Request
from app.db import get_connection
from datetime import datetime
router = APIRouter()


@router.post("/get_issues_by_filter", tags=['filter'])
async def get_issues_by_filter(request: Dict, conn = Depends(get_connection)):
    try:
        project_id = request['project_id']
        filter = request['filter']
        users_collection = conn["users"]
        
        issue_list = [
            {'$unwind': '$work'},
        ]
        
        if project_id != 0:
            issue_list.append(
                {'$match': {'work.project_id': project_id}}
            )
        if filter != "":
            issue_list.append(
                {'$match': {'work.label':filter}}
            )
        issue_list.extend([
            {'$sort': {
                'work.start_time': -1,
                'work.end_time': -1
            }},
            {'$group': {
                '_id': '$work.issue_id',
                'work': {'$first': '$work'},
                'user': {'$first': '$name'}
            }},
            {'$lookup': {
                'from': 'issues',
                'localField': 'work.issue_id',
                'foreignField': 'id',
                'as': 'result'
            }},
            {'$unwind': '$result'},
            {'$lookup': {
                'from': 'users',
                'localField': 'result.author_id',
                'foreignField': 'id',
                'as': 'creator'
            }},
            {'$unwind': '$creator'},
            {'$project': {
                '_id': 0,
                'label':'$work.label',
                'creator_name': '$creator.name',
                'name': '$user',
                'duration': '$work.duration',
                'issue_name': '$result.title',
                'url':'$result.url',
                'created_at': '$result.created_at',
                'creator_username':'$creator.username',
                'last_update': {
                    '$cond': {
                        'if': {'$ne': ['$work.end_time', None]},
                        'then': '$work.end_time',
                        'else': '$work.start_time'
                    }
                }
            }}
        ])
        
        issues_list = list(users_collection.aggregate(issue_list))
        curr_time = datetime.now()

        for issue in issues_list:
            if issue['duration'] is None:
                issue['duration'] = (curr_time - issue['last_update']).total_seconds()
            issue['last_update'] = (curr_time - issue['last_update']).total_seconds()
            issue['created_at'] = (curr_time - issue['created_at']).total_seconds()
        
        return {'status': True, 'data': issues_list, 'message': 'Issues fetched successfully'}
    except Exception as e:
        return {"status": False, "data": [], "message": str(e)}
