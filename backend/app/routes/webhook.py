from typing import Dict
from fastapi import APIRouter, Request, Depends
from app.db import get_connection
from app.methods.data_entry import insert_logs
from app.methods.data_to_model import employee, project, issue

router = APIRouter()



@router.post("/webhook")
async def simple(request:Request, db = Depends(get_connection)):
    payload: Dict = await request.json()
    print(payload)
    # Insert Logs in DB
    insert_logs(payload, db)
    project_info = payload['project']

    project(project_info, db)

    if payload['event_type'] == 'issue':

        issue_object = payload['object_attributes']

        if 'labels' in payload['changes']:

            issue(issue_object, project_info, db)
            employee(payload, db)

    