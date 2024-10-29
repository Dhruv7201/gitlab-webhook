from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from datetime import datetime, timedelta, timezone
import pytz
from typing import List, Dict
from pydantic import BaseModel
from typing import Any


router = APIRouter()


class DailyReportRequest(BaseModel):
    project_id: int
    selected_date: str


@router.post("/daily_report", response_model=List[Dict[str, Any]], tags=['reports'])
async def daily_report(
    report_request: DailyReportRequest,
    conn=Depends(get_connection)
):
    selected_date = datetime.strptime(report_request.selected_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

    # Fetch all issues that match the criteria
    issues_collection = conn["issues"]
    all_issues = list(issues_collection.find({
        'project_id': report_request.project_id if report_request.project_id != 0 else {'$exists': True}
    }))

    # Fetch users and milestones in a single call
    users_collection = conn["users"]
    milestones_collection = conn["milestones"]

    users_dict = {user['id']: user['name'] for user in users_collection.find()}
    milestones_dict = {milestone['id']: milestone for milestone in milestones_collection.find()}

    report = []
    unique_issues = {}

    for issue in all_issues:
        # Check for relevant work entries
        for work in issue.get('work', []):
            if work['label'] in ['Doing', 'Testing', 'Documentation'] and work.get('end_time') is None:
                assigned_to_name = users_dict.get(work['user_id'], 'Unknown')

                # Initialize variable for last milestone details
                milestone_details = None

                # Get the last milestone
                milestones = issue.get('milestone', [])
                if milestones:
                    last_milestone = milestones[-1]  # Get the last milestone
                    milestone_id = last_milestone.get('milestone_id')
                    if milestone_id:
                        milestone_details = milestones_dict.get(milestone_id)

                # Build the report entry
                report_entry = {
                    'id': issue['iid'],
                    'issue_id': issue['id'],
                    'issue_url': issue['url'],
                    'name': issue['title'],
                    'assigned_to': assigned_to_name,
                    'milestone': milestone_details['title'] if milestone_details else None,
                    'milestone_start_time': milestone_details['start_date'] if milestone_details else None,
                    'status': work['label'],
                    'start_time': work['start_time'],
                    'due_date': issue.get('due_date'),
                    'efforts': 0,  # Default efforts
                    'comments': ''  # Default comments
                }

                # Check for efforts and comments from comments_efforts collection
                efforts_comments = list(conn["comments_efforts"].find({
                    'issue_id': issue['iid'],
                    'date': selected_date.date().strftime('%Y-%m-%d'),
                }))

                if efforts_comments:
                    report_entry['efforts'] = efforts_comments[0].get('efforts', 0)
                    report_entry['comments'] = efforts_comments[0].get('comments', '')

                # Manage unique issues based on issue_id
                issue_id = report_entry['issue_id']
                if issue_id not in unique_issues:
                    unique_issues[issue_id] = report_entry
                else:
                    existing_issue = unique_issues[issue_id]
                    milestone_start_time = report_entry['milestone_start_time']
                    
                    # Keep the latest milestone start time
                    if milestone_start_time and (
                        not existing_issue.get('milestone_start_time') or 
                        milestone_start_time > existing_issue['milestone_start_time']
                    ):
                        unique_issues[issue_id] = report_entry
                    
                    # If milestone start times are equal, check start_time
                    elif milestone_start_time == existing_issue.get('milestone_start_time'):
                        start_time = report_entry['start_time']
                        if start_time and (not existing_issue.get('start_time') or start_time > existing_issue['start_time']):
                            unique_issues[issue_id] = report_entry

    # Convert the unique issues dictionary back to a list
    report = list(unique_issues.values())
    
    # Format due_date
    for issue in report:
        if issue.get('due_date'):
            issue['due_date'] = str(issue['due_date']).split(' ')[0]
    
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
