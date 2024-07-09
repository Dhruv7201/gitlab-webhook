from datetime import datetime
from app.methods.data_entry import  update_work_of_employee, check_if_user, insert_user, insert_project, insert_issues
from app.utils.date_utils import convert_to_ISC


labels_list = ['doing', 'testing', 'doc']
def employee(payload, db):
   
    user = payload['user']
    # If user is not present in DB insert him without 'work'
    if check_if_user(payload['user']['username'], db):
        employee = {'id':user['id']  , 'username':user['username'], 'name':user['name'], 'email':user['name'], 'avatar_url':user['avatar_url'], 'id':user['id'],
                     }
        insert_user(employee, db)

    curr_work = []


    current_labels_names = [] 
    previous_label_names = []

    # from current labels in json insert names into current_labels_name
    for curr_label in payload['changes']['labels']['current']:
        current_labels_names.append(curr_label['title'])

    # from previous labels in json insert names into previous_labels_name
    for curr_label in payload['changes']['labels']['previous']:
        previous_label_names.append(curr_label['title'])


    for label_name in labels_list:
        # lable is in in current but not in prev it means new label is added
        if label_name in current_labels_names and label_name not in previous_label_names:
            # for added_labels end_time is none to check further
            curr_work.append({
                'issue_id':payload['object_attributes']['id'],
                'label':label_name,
                'start_time' : datetime.now(),
                'end_time':None,
                'duration': 0
            })
        # lable is in in prev but not in current it means new label is removed
        if label_name not in current_labels_names and label_name in previous_label_names:
            # for remove_labels start_time is none to check further
            curr_work.append({
                'issue_id':payload['object_attributes']['id'],
                'label':label_name,
                'start_time':None,
                'end_time':datetime.now()
            })

    update_work_of_employee(curr_work, payload['user']['username'], db)


def project(project_info, db):
    insert_project({'id':project_info['id'], 'name':project_info['name'], 'description':project_info['description'], 'web_url':project_info['web_url'], 'homepage':project_info['homepage']}, db)

def issue(issue_object, project_info, db):
        
        insert_issues({'id':issue_object['id'], 'title':issue_object['title'],
                        'assignee_id':issue_object['assignee_id'], 'author_id':issue_object['author_id'], 
                        'created_at':convert_to_ISC(issue_object['created_at']), 'updated_at':convert_to_ISC(issue_object['updated_at']),
                        'project_id':project_info['id'], 'description':issue_object['description'], 
                        'milestone_id':issue_object['milestone_id'], 'due_date':convert_to_ISC(issue_object['due_date']),
                        'url':issue_object['url'], 'state':issue_object['state']}, db)

