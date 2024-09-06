from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from app.utils.date_utils import convert_to_ISC
from app.methods.data_entry import insert_logs, push_milestone, push_assign
from app.methods.data_to_model import employee, project, issue, insert_work_in_user, work_item, insert_work_in_issue

router = APIRouter()


@router.post("/webhook", tags=["webhook"])
async def webhook(request: dict, db=Depends(get_connection)):
    payload = request
    try:
        insert_logs(payload, db)
        project_info = payload.get('project')
        project(project_info, db)
        employee(payload, db)
        
        if payload['object_kind'] == 'issue':
            issue_object = payload['object_attributes']
            payload['type'] = 'issue'
            issue(payload, db)

            changes = payload.get('changes', {})
            
            if 'labels' in changes:
                insert_work_in_user(payload, db)
                insert_work_in_issue(payload, db)

            if 'milestone_id' in changes:
                try:
                    curr_milestone_id = changes['milestone_id']['current']
                    prev_milestone_id = changes['milestone_id']['previous']
                    updated_at = convert_to_ISC(changes['updated_at']['current'])
                    push_milestone(issue_object['id'], curr_milestone_id, prev_milestone_id, updated_at, db)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Milestone update failed: {str(e)}")

            if 'assignees' in changes:
                id = issue_object['id']
                project_id = project_info['id']
                previous_assign = changes['assignees']['previous']
                current_assign = changes['assignees']['current']
                push_assign(id, previous_assign, current_assign, project_id, db)

        elif payload['object_kind'] == 'work_item':
            work_item(payload, db)
            changes = payload.get('changes', {})
            
            if 'labels' in changes:
                insert_work_in_user(payload, db)
                insert_work_in_issue(payload, db)

            if 'assignees' in changes:
                id = payload['object_attributes']['id']
                project_id = payload['project']['id']
                previous_assign = changes['assignees']['previous']
                current_assign = changes['assignees']['current']
                push_assign(id, previous_assign, current_assign, project_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

    return {"status": True, "message": "Webhook processed successfully"}
