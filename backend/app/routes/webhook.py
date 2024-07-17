from typing import Dict
from fastapi import APIRouter, Request, Depends
from app.db import get_connection
from app.methods.data_entry import insert_logs, push_milestone, push_assign
from app.methods.data_to_model import employee, project, issue, insert_work_in_user

router = APIRouter()



@router.post("/webhook", tags=["webhook"])
async def webhook(request:Request, db = Depends(get_connection)):
    payload: Dict = await request.json()
    # Insert Logs in DB
    insert_logs(payload, db)
    # print(payload)
    project_info = payload['project']
    project(project_info, db)
    employee(payload, db)
    if payload['object_kind'] == 'issue':
        issue_object = payload['object_attributes']

        issue(issue_object, project_info, payload['changes'] , db)
        if 'labels' in payload['changes']:
            insert_work_in_user(payload, db)

        if 'milestone_id' in payload['changes']:
            curr_milestone_id = payload['changes']['milestone_id']['current']
            updated_at = payload['changes']['updated_at']['current']
            push_milestone(issue_object['id'], curr_milestone_id, updated_at, db)

        if 'assignees' in payload['changes']:
            id = payload['object_attributes']['id']
            previous_assign = payload['changes']['assignees']['previous']
            current_assign = payload['changes']['assignees']['current']
            push_assign(id, previous_assign, current_assign, payload['project']['id'], db)  

    