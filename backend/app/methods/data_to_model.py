from datetime import datetime
from app.methods.data_entry import  update_work_of_user, insert_user, insert_project, insert_issues, insertReOpen, reOpenIncrement, end_qa_assign, onHold, insert_work_item, bind_child_task_to_issue
from app.utils.date_utils import convert_to_ISC
import requests
import os

labels_list = {'Doing':0, 'Testing':1, 'Documentation':2}
reOpen = 'Re-Open'
def employee(payload, db):
    user = payload['user']
    token = os.getenv('GITLAB_KEY')
    headers = {
        "Private-Token": token
    }
    user_email = requests.get(f"https://code.ethicsinfotech.in/api/v4/users/{user['id']}", headers=headers).json()['email']
    if not user_email:
        user_email = user['username']
    employee = {'id':user['id']  , 'username':user['username'], 'name':user['name'], 'email':user_email, 'avatar_url':user['avatar_url'], 'assign_issues':[]
            }
    insert_user(employee, db)
    if 'assignees' in payload:
        assign = payload['assignees'][0]
        assigned_employee = {'id':assign['id']  , 'username':assign['username'], 'name':assign['name'], 'email':user_email, 'avatar_url':assign['avatar_url'], 'assign_issues':[]
            }
        insert_user(assigned_employee, db)


def insert_work_in_user(payload, db):
    
    curr_work = []
    changed_works = [0,0,0]
    previous_labels = payload['changes']['labels']['previous']
    for label in previous_labels:
        if label['title'] in labels_list:
            changed_works[labels_list[label['title']]] -= 1
    
    curr_labels = payload['changes']['labels']['current']
    for label in curr_labels:

        if label['title'] in labels_list:
            changed_works[labels_list[label['title']]] += 1
    curr_time = datetime.now()
    for label in labels_list:
        if changed_works[labels_list[label]] == -1:
            curr_work.append({
                'issue_id':payload['object_attributes']['id'],
                'project_id':payload['project']['id'],
                'label':label,
                'start_time':None,
                'end_time':curr_time
            })
        elif changed_works[labels_list[label]] == 1:
            curr_work.append({
                'issue_id':payload['object_attributes']['id'],
                'project_id':payload['project']['id'],
                'label':label,
                'start_time' : curr_time,
                'end_time':None,
                'duration': None
            })
    user_id = payload['user']['username']
    if 'Ready for release' in [label['title'] for label in curr_labels] and 'Ready for release' not in [label['title'] for label in previous_labels]:
        end_qa_assign(payload, db)
    if 'OnHold' in [label['title'] for label in curr_labels] and 'OnHold' not in [label['title'] for label in previous_labels]:
        onHold(payload, db)

    update_work_of_user(curr_work, user_id, db)


def project(project_info, db):
    insert_project({'id':project_info['id'], 'name':project_info['name'], 'description':project_info['description'], 'web_url':project_info['web_url'], 'homepage':project_info['homepage']}, db)

def issue(payload,  db): 
        changes = payload['changes']
        issue_object = payload['object_attributes']
        project_info = payload['project']
            
        insert_issues(payload, {'id':issue_object['id'], 'iid':issue_object['iid'], 'title':issue_object['title'],'author_id':issue_object['author_id'], 'created_at':convert_to_ISC(issue_object['created_at']), 'updated_at':convert_to_ISC(issue_object['updated_at']),'project_id':project_info['id'], 'description':issue_object['description'], 'due_date':convert_to_ISC(issue_object['due_date']),'url':issue_object['url'], 'state':issue_object['state'], 'closed_at':None }, changes,  db)

        if 'labels' in payload['changes']:
            currLabel = payload['changes']['labels']['current']
            prevLabels = payload['changes']['labels']['previous']
            prevTitles = [obj['title'] for obj in prevLabels]
            titles = [obj['title'] for obj in currLabel]

            if 'Testing' in titles and reOpen in titles and ('Testing' not in prevTitles or reOpen not in prevTitles):
                reOpenIncrement(issue_object['id'], db)
            elif 'Testing' in titles and reOpen in titles:
                insertReOpen(issue_object['id'],1,  db)
            elif reOpen in titles:
                insertReOpen(issue_object['id'],0,  db)


def work_item(payload, db):
    import requests
    import os

    # Your GitLab instance URL and Personal Access Token (PAT)
    gitlab_url = "https://code.ethicsinfotech.in/"
    private_token = os.getenv('GITLAB_KEY')
    headers = {
        "Private-Token": private_token
    }
    task_id = payload['object_attributes']['iid']
    project_id = payload['object_attributes']['project_id']
    print(task_id)
    print(project_id)
    task_url = f"{gitlab_url}/api/v4/projects/{project_id}/issues/{task_id}/notes"
    response = requests.get(task_url, headers=headers)
    task = response.json()
    bind_child_task_to_issue(task, db)
    insert_work_item(payload, db)
    