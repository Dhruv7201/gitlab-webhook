from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import pytz
from datetime import datetime, timezone
from typing import List, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel


router = APIRouter()


class DailyReportRequest(BaseModel):
    project_id: int
    selected_date: str


@router.post("/daily_report", response_model=List[Dict], tags=['reports'])
async def daily_report(
    report_request: DailyReportRequest,
    conn=Depends(get_connection)
):
    selected_date = report_request.selected_date
    if selected_date is None:
        selected_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    date = selected_date
    issues_collection = conn["issues"]

    issue_list = [
        {'$unwind': '$work'},
        {
            '$lookup': {
                'from': 'users',
                'localField': 'work.user_id',
                'foreignField': 'id',
                'as': 'assigned_to'
            }
        },
        {'$unwind': '$assigned_to'},
        {
            '$lookup': {
                'from': 'milestones',
                'localField': 'milestone.milestone_id',
                'foreignField': 'id',
                'as': 'milestone_details'
            }
        },
        {'$unwind': {'path': '$milestone_details', 'preserveNullAndEmptyArrays': True}},
        {
            '$lookup': {
                'from': 'comments_efforts',
                'let': {'issue_id': '$iid'},
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$and': [
                                    {'$eq': ['$issue_id', '$$issue_id']},
                                    {'$eq': ['$date', date]}
                                ]
                            }
                        }
                    }
                ],
                'as': 'efforts_comments'
            }
        },
        {'$unwind': {'path': '$efforts_comments', 'preserveNullAndEmptyArrays': True}},
    ]
    
    project_id = report_request.project_id
    if project_id != 0:
        issue_list.append({'$match': {'project_id': project_id}})

    issue_list.append({
        '$match': {
            'work.label': {'$in': ['Doing', 'Testing', 'Documentation']},
            'work.start_time': {
                '$gte': datetime.strptime(date, '%Y-%m-%d'),
                '$lt': datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
            }
        }
    })

    issue_list.extend([
        {
            '$project': {
                'id': '$iid',
                'issue_id': '$id',
                'issue_url': '$url',
                'name': '$title',
                'assigned_to': '$assigned_to.name',
                'milestone': '$milestone_details.title',
                'milestone_start_time': '$milestone_details.start_time',
                'status': '$work.label',
                'start_time': '$work.start_time',
                'due_date': '$due_date',
                'efforts': {'$ifNull': ['$efforts_comments.efforts', 0]},
                'comments': {'$ifNull': ['$efforts_comments.comments', '']}
            }
        }
    ])

    issues = list(issues_collection.aggregate(issue_list))
    report = [{k: v for k, v in issue.items() if k != '_id'} for issue in issues]
    
    # Dictionary to track unique issues based on title (name)
    unique_issues = {}

    for issue in report:
        if issue.get('due_date'):
            issue['due_date'] = str(issue['due_date']).split(' ')[0]
        
        issue_id = issue['issue_id']
        start_time = issue.get('start_time')
        milestone_start_time = issue.get('milestone_start_time')

        # Identify if the issue_id is already being tracked
        if issue_id not in unique_issues:
            unique_issues[issue_id] = issue
        else:
            existing_issue = unique_issues[issue_id]
            
            # 1. Compare milestone_start_time: Keep the latest one
            if milestone_start_time and (
                not existing_issue.get('milestone_start_time') or 
                milestone_start_time > existing_issue['milestone_start_time']
            ):
                unique_issues[issue_id] = issue
            
            # 2. If milestone_start_time is equal, check for the latest start_time (status update)
            elif milestone_start_time == existing_issue.get('milestone_start_time'):
                if start_time and (not existing_issue.get('start_time') or start_time > existing_issue['start_time']):
                    unique_issues[issue_id] = issue

    # Convert the dictionary back to a list
    report = list(unique_issues.values())
    return report


@router.post("/daily_report_comments", tags=['reports'])
async def daily_report_comments(request: Dict, conn=Depends(get_connection)):
    date_str = request.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d'))

    local_tz = pytz.timezone("Asia/Kolkata")

    try:
        local_date = local_tz.localize(datetime.strptime(date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0))
        date_to_store = local_date.strftime('%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")

    username = request.get('username')
    data = request.get('data', [])

    comments_efforts_collection = conn["comments_efforts"]

    for item in data:
        if not item.get('comments') and not item.get('efforts'):
            continue
        print(item)
        issue_id = item.get('id')
        comment = item.get('comments')
        effort_hours = item.get('efforts', 0)

        existing_comment = comments_efforts_collection.find_one({
            'issue_id': issue_id,
            'date': date_to_store,
            'user_id': username
        })

        if existing_comment:
            comments_efforts_collection.update_one(
                {'_id': existing_comment['_id']},
                {'$set': {'comments': comment, 'efforts': effort_hours}}
            )
        else:
            comments_efforts_collection.insert_one({
                'issue_id': issue_id,
                'date': date_to_store,
                'user_id': username,
                'comments': comment,
                'efforts': effort_hours
            })

    return {"status": True, "message": "Comments saved successfully"}
