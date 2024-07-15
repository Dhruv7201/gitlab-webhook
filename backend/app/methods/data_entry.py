from app.models  import user_model, project_model
from datetime import datetime

def insert_logs(data, db):
    logs_collection = db['logs']
    data['inserted_at'] = datetime.now()
    logs_collection.insert_one(data)

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
        # if we have start_time add into db
        if curr_work['start_time']:
            update = {"$push": {"work": curr_work}}
            user_collection.update_one(filter, update)
        else:
            works = user_collection.find_one(filter)
            # if add label is not tracked then just ignore remove label
            if works is None or 'work' not in works:
                print('Starting time not available')
                return
            work_arr = works['work']
            for i in range(len(work_arr)-1, -1, -1):
                work = work_arr[i]
                # check for start_time and end_time to remove untracked label
                if work['issue_id'] == curr_work['issue_id'] and work['label'] == curr_work['label'] and work['start_time'] and not work['end_time']:
                    work_arr[i]['end_time'] = curr_work['end_time']
                    work_arr[i]['duration'] = (curr_work['end_time'] -  work['start_time']).total_seconds()
                    break
            update = {"$set": {"work": work_arr}}
            user_collection.update_one(filter, update)

def insert_issues(issue, changes,  db):
    issue_collection = db['issues']

    filter = {'id':issue['id']}
    curr_issue = issue_collection.find_one(filter)
    if not curr_issue:
        issue_collection.insert_one(issue)
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
                 
def push_milestone(issue_id, curr_milestone_id, updated_at ,db):
    
    issue_collection = db['issues']
    filter = {'id':issue_id}
    curr_milestone_info = {'milestone_id':curr_milestone_id, 'updated_at':updated_at, 'title':None}
    update = {"$push": {'milestone':curr_milestone_info}}
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
        for index in range(len(assign_arr)-1, -1, -1):
            if assign_arr[index]['user_id'] == previous_assign[0]['id']:
                
                assign_arr[index]['end_time'] = curr_time
                assign_arr[index]['duration'] = (assign_arr[index]['end_time'] - assign_arr[index]['start_time']).total_seconds()
                break
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
            'issues_id':issue_id, 
            'project_id':project_id,
            'start_time':curr_time,
            'end_time':None,
            'duration':None
            }
        filter = {'username':curr_assign[0]['username']}
        if not user_collection.find_one(filter):
            user = curr_assign[0]
            employee = {'id':user['id'],  'username':user['username'], 'name':user['name'], 'email':user['username'], 'avatar_url':user['avatar_url'], 'assign_issues':[added_issue]}
            insert_user(employee, db)
        else:
            update = {'$push':{'assign_issues':added_issue}}
            user_collection.update_one(filter, update)

    if prev_assign != []:
        filter = {'username':prev_assign[0]['username']}
        if not user_collection.find_one(filter):
            user = curr_assign[0]
            employee = {'id':user['id']  , 'username':user['username'], 'name':user['name'],
                        'email':user['username'], 'avatar_url':user['avatar_url'], 'assign_issues':[]}
            insert_user(employee, db)
        else:
            assign_issue_arr = user_collection.find_one(filter)['assign_issues']
            for index in range(len(assign_issue_arr)-1, -1, -1):
                if assign_issue_arr[index]['issues_id'] == issue_id and assign_issue_arr[index]['start_time'] and not assign_issue_arr[index]['end_time']:
                    assign_issue_arr[index]['end_time'] = curr_time
                    assign_issue_arr[index]['duration'] = (curr_time - assign_issue_arr[index]['start_time']).total_seconds()
                    update = {'$set':{'assign_issues':assign_issue_arr}}
                    user_collection.update_one(filter, update)
                    break 