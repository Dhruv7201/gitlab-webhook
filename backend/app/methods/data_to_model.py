from datetime import datetime
from app.methods.data_entry import (
    update_work_of_user,
    insert_user,
    insert_project,
    insert_issues,
    insertReOpen,
    reOpenIncrement,
    end_qa_assign,
    onHold,
    bind_child_task_to_issue,
    update_work_of_issue,
)
from app.utils.date_utils import convert_to_ISC
import requests
import os
from fastapi import HTTPException

"""
label list is list of labels that are tracked for user
issue_labels_list is the list of labels that are tracked for issues
# TODO automate this as i have added the labels setting in the front end
"""
labels_list = {"Doing": 0, "Testing": 1, "Documentation": 2}
issue_labels_list = {
    "Documentation": 0,
    "DocComplete": 1,
    "DevReady": 2,
    "Doing": 3,
    "QA": 4,
    "Testing": 5,
    "Ready for release": 6,
    "ReleasePlan": 7,
    "Regression": 8,
    "ReadyForProd": 9,
    "LivePublishing": 10,
    "LivePublished": 11,
    "Smoke": 12,
    "SmokeDone": 13,
    "OnHold": 14,
    "Re-Open": 15,
    "Unplanned": 16,
}

"""
Re-Open is for tracking the reopen count of the issue
"""
reOpen = "Re-Open"


def employee(payload: dict, db):
    """
    this method is to insert the employee details in the user collection
    """
    user = payload["user"]
    token = os.getenv("GITLAB_KEY")
    headers = {"Private-Token": token}
    """
    get the employee details from the gitlab api as we are not getting the email in the payload
    """
    response = requests.get(
        f"https://code.ethicsinfotech.in/api/v4/users/{user['id']}", headers=headers
    )
    response.raise_for_status()

    user_email = response.json().get("email") or user["username"]
    employee_data = {
        "id": user["id"],
        "username": user["username"],
        "name": user["name"],
        "email": user_email,
        "avatar_url": user["avatar_url"],
        "assign_issues": [],
    }
    insert_user(employee_data, db)

    assignees = payload.get("assignees", [])
    for assign in assignees:
        assigned_employee = {
            "id": assign["id"],
            "username": assign["username"],
            "name": assign["name"],
            "email": user_email,
            "avatar_url": assign["avatar_url"],
            "assign_issues": [],
        }
        insert_user(assigned_employee, db)


def insert_work_in_user(payload: dict, db):
    """
    this method adds and modifies the work of the user in the user collection details are issue_id, project_id, label, start_time, end_time, duration
    conditions is that if the label is added then the start_time will be added and if the label is removed then the end_time will be added
    based on start time and end time the duration will be calculated and added
    """
    curr_work = []
    changed_works = [0] * len(labels_list)

    previous_labels = payload["changes"]["labels"]["previous"]
    for label in previous_labels:
        if label["title"] in labels_list:
            changed_works[labels_list[label["title"]]] -= 1

    curr_labels = payload["changes"]["labels"]["current"]
    for label in curr_labels:
        if label["title"] in labels_list:
            changed_works[labels_list[label["title"]]] += 1

    curr_time = datetime.now()
    for label, change in labels_list.items():
        if changed_works[change] == -1:
            curr_work.append(
                {
                    "issue_id": payload["object_attributes"]["id"],
                    "project_id": payload["project"]["id"],
                    "label": label,
                    "start_time": None,
                    "end_time": curr_time,
                }
            )
        elif changed_works[change] == 1:
            curr_work.append(
                {
                    "issue_id": payload["object_attributes"]["id"],
                    "project_id": payload["project"]["id"],
                    "label": label,
                    "start_time": curr_time,
                    "end_time": None,
                    "duration": None,
                }
            )

    user_id = payload["user"]["username"]
    curr_label_titles = [label["title"] for label in curr_labels]
    prev_label_titles = [label["title"] for label in previous_labels]
    """
    this is to maintain the Ready for release and OnHold fields in the issue collection
    """
    if (
        "Ready for release" in curr_label_titles
        and "Ready for release" not in prev_label_titles
    ):
        end_qa_assign(payload, db)
    if "OnHold" in curr_label_titles and "OnHold" not in prev_label_titles:
        onHold(payload, db)

    update_work_of_user(curr_work, user_id, db)


def insert_work_in_issue(payload: dict, db):
    """
    this does the same thing as the insert_work_in_user but for the issue collection and details are user_id, label, start_time, end_time, duration
    """
    curr_work = []
    changed_works = [0] * len(issue_labels_list)

    previous_labels = payload["changes"]["labels"]["previous"]
    for label in previous_labels:
        if label["title"] in issue_labels_list:
            changed_works[issue_labels_list[label["title"]]] -= 1

    curr_labels = payload["changes"]["labels"]["current"]
    for label in curr_labels:
        if label["title"] in issue_labels_list:
            changed_works[issue_labels_list[label["title"]]] += 1

    curr_time = datetime.now()
    for label, change in issue_labels_list.items():
        if changed_works[change] == -1:
            curr_work.append(
                {
                    "user_id": payload["user"]["id"],
                    "label": label,
                    "start_time": None,
                    "end_time": curr_time,
                }
            )
        elif changed_works[change] == 1:
            curr_work.append(
                {
                    "user_id": payload["user"]["id"],
                    "label": label,
                    "start_time": curr_time,
                    "end_time": None,
                    "duration": None,
                }
            )

    issue_id = payload["object_attributes"]["id"]
    update_work_of_issue(curr_work, issue_id, db)


def project(project_info: dict, db):
    """
    only work is to insert this project details in projects collection if not present
    """
    project_data = {
        "id": project_info["id"],
        "name": project_info["name"],
        "description": project_info["description"],
        "web_url": project_info["web_url"],
        "homepage": project_info["homepage"],
    }
    insert_project(project_data, db)


def issue(payload: dict, db):
    """
    preparation of the issue data and insertion of the issue in the issue collection
    """
    changes = payload.get("changes", {})
    issue_object = payload["object_attributes"]
    project_info = payload["project"]
    issue_type = payload["type"]
    issue_data = {
        "id": issue_object["id"],
        "iid": issue_object["iid"],
        "title": issue_object["title"],
        "type": issue_type,
        "author_id": issue_object["author_id"],
        "created_at": convert_to_ISC(issue_object["created_at"]),
        "updated_at": convert_to_ISC(issue_object["updated_at"]),
        "project_id": project_info["id"],
        "description": issue_object["description"],
        "due_date": convert_to_ISC(issue_object["due_date"]),
        "url": issue_object["url"],
        "state": issue_object["state"],
        "closed_at": None,
    }
    insert_issues(payload, issue_data, changes, db)

    if "labels" in changes:
        """
        It is to maintain the reopen count of the issue
        """
        curr_labels = changes["labels"]["current"]
        prev_labels = changes["labels"]["previous"]
        curr_titles = [label["title"] for label in curr_labels]
        prev_titles = [label["title"] for label in prev_labels]

        if "Testing" in curr_titles and reOpen in curr_titles:
            if "Testing" not in prev_titles or reOpen not in prev_titles:
                reOpenIncrement(payload, db)
                insertReOpen(payload, db)

    if issue_type == "task":
        """
        Take the child task and bind it to the parent issue by calling the gitlab api and getting the child task details
        """
        # Your GitLab instance URL and Personal Access Token (PAT)
        gitlab_url = "https://code.ethicsinfotech.in/"
        private_token = os.getenv("GITLAB_KEY")
        headers = {"Private-Token": private_token}
        task_id = payload["object_attributes"]["iid"]
        project_id = payload["object_attributes"]["project_id"]
        print(task_id)
        print(project_id)
        task_url = f"{gitlab_url}/api/v4/projects/{project_id}/issues/{task_id}/notes"
        response = requests.get(task_url, headers=headers)
        task = response.json()
        bind_child_task_to_issue(task, db)


def work_item(payload: dict, db):
    try:
        payload["type"] = "task"
        issue(payload, db)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Work item processing failed: {str(e)}"
        )
