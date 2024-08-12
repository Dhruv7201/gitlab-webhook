from app.models  import  project_model
from datetime import datetime
import requests
import os

def insert_logs(data, db):
    logs_collection = db['logs']
    data['inserted_at'] = datetime.now()
    logs_collection.insert_one(data)

def insertReOpen(issue_id, count,   db):

    issue_collection = db['issues']
    filter = {'id':issue_id}
    curr_issue = issue_collection.find_one(filter)
    if 'Re-Open' not in curr_issue:
        update = {"$set": {"Re-Open": count}}
        issue_collection.update_one(filter, update)

def reOpenIncrement(issue_id, db):
    insertReOpen(issue_id, 0,   db)
    issue_collection = db['issues']
    filter = {'id':issue_id}
    curr_issue = issue_collection.find_one(filter)
    currReOpen = curr_issue["Re-Open"]
    update = {"$set": {"Re-Open": currReOpen+1}}
    issue_collection.update_one(filter, update)

def insert_project(project:project_model, db):
    curr_time = datetime.now()
    project_collection = db['projects']
    if project_collection.find_one({'id':project['id']}):
        if project_collection.find_one({'id':project['id']})['description'] != project['description']:
            filter = {'id':project['id']}
            newvalues = {'$set':{'description':project['description'], 'updated_at' : curr_time}}
            project_collection.update_one(filter, newvalues)
    else:
        project['updated_at'] = curr_time
        project['created_at'] = curr_time
        project_collection.insert_one(project)

def insert_user(employee, db):
    user_collection = db['users']
    if not user_collection.find_one({'id':employee['id']}):
        user_collection.insert_one(employee)

def update_work_of_user(curr_work_arr, username, db):
    user_collection = db['users']
    
    filter = {'username': username}
    for curr_work in curr_work_arr:
        if curr_work['start_time']:
            update = {"$push": {"work": curr_work}}
            user_collection.update_one(filter, update)
        else:
            works = user_collection.find_one(filter)
            if works is None or 'work' not in works:
                return
            work_arr = works['work']
            for i in range(len(work_arr)-1, -1, -1):
                work = work_arr[i]
                if work['issue_id'] == curr_work['issue_id'] and work['label'] == curr_work['label'] and work['start_time'] and not work['end_time']:
                    work_arr[i]['end_time'] = curr_work['end_time']
                    work_arr[i]['duration'] = (curr_work['end_time'] -  work['start_time']).total_seconds()
                    break
            update = {"$set": {"work": work_arr}}
            user_collection.update_one(filter, update)

def insert_issues(payload, issue, changes,  db):
    issue_collection = db['issues']

    filter = {'id':issue['id']}
    curr_issue = issue_collection.find_one(filter)
    if not curr_issue:
        issue_collection.insert_one(issue)
        if  'assignees' in payload and payload['assignees'] != []:
            id = payload['object_attributes']['id']
            current_assign = payload['assignees']
            push_new_assign(id, current_assign, payload['project']['id'], db) 

    else:
        for key in changes:
            if key =='state_id':
                if changes[key]['current'] == 2:
                    update = {'$set':{'closed_at':datetime.now(), 'state':'closed'}}
                    issue_collection.update_one(filter, update)
                elif changes[key]['current'] == 1 and curr_issue['closed_at']:
                    update = {'$set':{'state':'reopen'}}
                    issue_collection.update_one(filter, update)
                elif changes[key]['current'] == 1:
                    update = {'$set':{'state':'open'}}
                    issue_collection.update_one(filter, update)
            else:
                if key in issue:
                    if key == 'closed_at':
                        continue
                    update = {'$set':{key: changes[key]['current']}}
                    issue_collection.update_one(filter, update)
                 
def push_milestone(issue_id, curr_milestone_id, prev_milestone_id, updated_at ,db):
    
    issue_collection = db['issues']
    filter = {'id':issue_id}
    curr_issue = issue_collection.find_one(filter)
    new_milestone = {'milestone_id':curr_milestone_id, 'updated_at':updated_at, 'title':None, 'start_time':datetime.now()}
    if 'milestone' in curr_issue and prev_milestone_id != None:
        curr_milestone_info = curr_issue['milestone']
        
        for index in range(len(curr_milestone_info)-1, -1, -1):
            if curr_milestone_info[index]['milestone_id'] == prev_milestone_id and 'end_time' not in curr_milestone_info[index]:
                curr_milestone_info[index]['end_time'] = datetime.now()
                curr_milestone_info[index]['duration'] = (datetime.now() - curr_milestone_info[index]['start_time']).total_seconds()
                break
        if curr_milestone_id != None:
            curr_milestone_info.append(new_milestone)
        update = {"$set": {'milestone':curr_milestone_info}}
        issue_collection.update_one(filter, update)
    else:
        update = {"$push": {'milestone':new_milestone}} 
        issue_collection.update_one(filter, update)


def push_assign(id, previous_assign, current_assign, project_id, db):
    issue_collection = db['issues']
    curr_time = datetime.now()
    filter = {'id':id}
    push_assign_to_user(id, previous_assign, current_assign, project_id, db)
    issue = issue_collection.find_one(filter)
    if 'assign' not in issue or previous_assign == []:
        first_assign = {'user_id':current_assign[0]['id'], 'start_time':curr_time, 'end_time':None, 'duration':None}
        update = {'$push':{'assign':first_assign}}
        issue_collection.update_one(filter, update)
    else:
        assign_arr = issue['assign']
        
        assign_arr[-1]['end_time'] = curr_time
        assign_arr[-1]['duration'] = (assign_arr[-1]['end_time'] - assign_arr[-1]['start_time']).total_seconds()
        if current_assign != []:
            new_assign = {'user_id' : current_assign[0]['id'], 'start_time':curr_time, 'end_time':None, 'duration':None}
            assign_arr.append(new_assign)
        update = {'$set':{'assign':assign_arr}}
        issue_collection.update_one(filter, update)

def push_assign_to_user(issue_id,  prev_assign, curr_assign, project_id, db):

    curr_time = datetime.now()
    user_collection = db['users']
    if curr_assign != [] :
        added_issue = {
            'issue_id':issue_id, 
            'project_id':project_id,
            'start_time':curr_time,
            'end_time':None,
            'duration':None
            }
        filter = {'username':curr_assign[0]['username']}
        if not user_collection.find_one(filter):
            user = curr_assign[0]
            token = os.getenv('GITLAB_KEY')
            headers = {
                "Private-Token": token
            }
            user_email = requests.get(f"https://code.ethicsinfotech.in/api/v4/users/{user['id']}", headers=headers).json()['email']
            if not user_email:
                user_email = user['username']
            employee = {'id':user['id'],  'username':user['username'], 'name':user['name'], 'email':user_email, 'avatar_url':user['avatar_url'], 'assign_issues':[added_issue]}
            insert_user(employee, db)
        else:
            update = {'$push':{'assign_issues':added_issue}}
            user_collection.update_one(filter, update)

    if prev_assign != []:
        filter = {'username':prev_assign[0]['username']}
        if not user_collection.find_one(filter):
            user = curr_assign[0]
            token = os.getenv('GITLAB_KEY')
            headers = {
                "Private-Token": token
            }
            user_email = requests.get(f"https://code.ethicsinfotech.in/api/v4/users/{user['id']}", headers=headers).json()['email']
            if not user_email:
                user_email = user['username']
            employee = {'id':user['id']  , 'username':user['username'], 'name':user['name'],
                        'email':user_email, 'avatar_url':user['avatar_url'], 'assign_issues':[]}
            insert_user(employee, db)
        else:
            assign_issue_arr = user_collection.find_one(filter)['assign_issues']
            for index in range(len(assign_issue_arr)-1, -1, -1):
                if assign_issue_arr[index]['issue_id'] == issue_id and assign_issue_arr[index]['start_time'] and not assign_issue_arr[index]['end_time']:
                    assign_issue_arr[index]['end_time'] = curr_time
                    assign_issue_arr[index]['duration'] = (curr_time - assign_issue_arr[index]['start_time']).total_seconds()
                    update = {'$set':{'assign_issues':assign_issue_arr}}
                    user_collection.update_one(filter, update)
                    break 

def push_new_assign(id, current_assign, project_id, db):
    issue_collection = db['issues']
    curr_time = datetime.now()
    filter = {'id':id}
    first_assign = {'user_id':current_assign[0]['id'], 'start_time':curr_time, 'end_time':None, 'duration':None}
    update = {'$push':{'assign':first_assign}}
    issue_collection.update_one(filter, update)
    push_new_assign_to_user(id, current_assign, project_id, db)

def push_new_assign_to_user(issue_id, current_assign, project_id, db):
    curr_time = datetime.now()
    user_collection = db['users']
    if current_assign != [] :
        
        added_issue = {
            'issue_id':issue_id, 
            'project_id':project_id,
            'start_time':curr_time,
            'end_time':None,
            'duration':None
            }
        filter = {'username':current_assign[0]['username']}
        if not user_collection.find_one(filter):
            user = current_assign[0]
            token = os.getenv('GITLAB_KEY')
            headers = {
                "Private-Token": token
            }
            user_email = requests.get(f"https://code.ethicsinfotech.in/api/v4/users/{user['id']}", headers=headers).json()['email']
            if not user_email:
                user_email = user['username']
            employee = {'id':user['id'],  'username':user['username'], 'name':user['name'], 'email':user_email, 'avatar_url':user['avatar_url'], 'assign_issues':[added_issue]}
            insert_user(employee, db)
        else:
            update = {'$push':{'assign_issues':added_issue}}
            user_collection.update_one(filter, update)


def end_qa_assign(payload, db):
    issue_collection = db['issues']
    filter = {'id':payload['object_attributes']['id']}
    issue = issue_collection.find_one(filter)
    curr_time = datetime.now()
    assign_arr = issue['assign']
    for index in range(len(assign_arr)-1, -1, -1):
        if assign_arr[index]['end_time'] == None:
            assign_arr[index]['end_time'] = curr_time
            assign_arr[index]['duration'] = (curr_time - assign_arr[index]['start_time']).total_seconds()
            break
    update = {'$set':{'assign':assign_arr}}
    issue_collection.update_one(filter, update)
    user_collection = db['users']
    user = user_collection.find_one({'id':payload['user']['id']})
    assign_issue_arr = user['assign_issues']
    for index in range(len(assign_issue_arr)-1, -1, -1):
        if assign_issue_arr[index]['issue_id'] == payload['object_attributes']['id'] and assign_issue_arr[index]['end_time'] == None:
            assign_issue_arr[index]['end_time'] = curr_time
            assign_issue_arr[index]['duration'] = (curr_time - assign_issue_arr[index]['start_time']).total_seconds()
            break
    update = {'$set':{'assign_issues':assign_issue_arr}}
    user_collection.update_one({'id':payload['user']['id']}, update)