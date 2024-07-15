from datetime import datetime
from app.methods.data_entry import  update_work_of_user, insert_user, insert_project, insert_issues
from app.utils.date_utils import convert_to_ISC


labels_list = {'doing':0, 'testing':1, 'doc':2}
def employee(payload, db):
    user = payload['user']
    # If user is not present in DB insert him without 'work'
    
    employee = {'id':user['id']  , 'username':user['username'], 'name':user['name'], 'email':user['name'], 'avatar_url':user['avatar_url'], 'assign_issues':[]
            }
    insert_user(employee, db)

def insert_work_in_user(payload, db):
    
    curr_work = []
    changed_works = [0,0,0]

    for prev_label in payload['changes']['labels']['previous']:
        if prev_label['title'] in labels_list:
            changed_works[labels_list[prev_label['title']]] -= 1
    
    for curr_label in payload['changes']['labels']['current']:
        if curr_label['title'] in labels_list:
            changed_works[labels_list[curr_label['title']]] += 1
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
             
    update_work_of_user(curr_work, payload['user']['username'], db)


def project(project_info, db):
    insert_project({'id':project_info['id'], 'name':project_info['name'], 'description':project_info['description'], 'web_url':project_info['web_url'], 'homepage':project_info['homepage']}, db)

def issue(issue_object, project_info, changes, db): 
        insert_issues({'id':issue_object['id'], 'title':issue_object['title'],'author_id':issue_object['author_id'], 'created_at':convert_to_ISC(issue_object['created_at']), 'updated_at':convert_to_ISC(issue_object['updated_at']),'project_id':project_info['id'], 'description':issue_object['description'], 'due_date':convert_to_ISC(issue_object['due_date']),'url':issue_object['url'], 'state':issue_object['state'], 'closed_at':None }, changes,  db)