from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
from app.utils.date_utils import convert_to_ISC
from app.methods.data_entry import push_milestone, push_assign
from app.methods.data_to_model import (
    employee,
    project,
    issue,
    insert_work_in_user,
    work_item,
    insert_work_in_issue,
)

router = APIRouter()


@router.post("/webhook", tags=["webhook"])
async def webhook(request: dict, db=Depends(get_connection)):
    payload = request
    try:
        """
        Git lab will give us the payload there will be changes in the payload
        so we have to check the type of the payload and then we have to insert the data in the database
        issues are gitlab project issues
        work_item are the child task that are added in gitlab issues
        """
        project_info = payload.get("project")
        project(project_info, db)
        employee(payload, db)

        if payload["object_kind"] == "issue":
            """
            object attributes are the main part as we'll get all details in that
            """
            issue_object = payload["object_attributes"]
            payload["type"] = "issue"
            """
            this method is used to insert the issue in the database and frame the data for better storage
            """
            issue(payload, db)
            """
            changes will contain the changes that are made in the issue after the initial creation
            """

            changes = payload.get("changes", {})

            if "labels" in changes:
                """
                initial insertion of the work in the user and issue table
                """
                insert_work_in_user(payload, db)
                insert_work_in_issue(payload, db)

            if "milestone_id" in changes:
                try:
                    """
                    push new milestone in the array of milestones in the issue collection
                    """
                    curr_milestone_id = changes["milestone_id"]["current"]
                    prev_milestone_id = changes["milestone_id"]["previous"]
                    updated_at = convert_to_ISC(changes["updated_at"]["current"])
                    push_milestone(
                        issue_object["id"],
                        curr_milestone_id,
                        prev_milestone_id,
                        updated_at,
                        db,
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Milestone update failed: {str(e)}"
                    )

            if "assignees" in changes:
                """
                push the assignee in the assignee array in the issue collection
                """
                id = issue_object["id"]
                project_id = project_info["id"]
                previous_assign = changes["assignees"]["previous"]
                current_assign = changes["assignees"]["current"]
                push_assign(id, previous_assign, current_assign, project_id, db)

        elif payload["object_kind"] == "work_item":
            """
            work item are the child task of the issues
            same process will happen for both issues and work items but the type will be different in type field
            """
            work_item(payload, db)
            changes = payload.get("changes", {})

            if "labels" in changes:
                insert_work_in_user(payload, db)
                insert_work_in_issue(payload, db)

            if "assignees" in changes:
                id = payload["object_attributes"]["id"]
                project_id = payload["project"]["id"]
                previous_assign = changes["assignees"]["previous"]
                current_assign = changes["assignees"]["current"]
                push_assign(id, previous_assign, current_assign, project_id, db)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Webhook processing failed: {str(e)}"
        )

    return {"status": True, "message": "Webhook processed successfully"}
