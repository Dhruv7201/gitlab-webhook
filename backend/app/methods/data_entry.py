from app.models  import user_model, issue_model, project_model
from datetime import datetime



def check_if_user(username, db):
    user_collection = db['user']
    if user_collection.find_one({'username':username}):
        return False
    return True

def update_work_of_employee(curr_work_arr, username, db):
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
            if 'work' not in works:
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

def insert_user(employee:user_model, db):
    collection = db['users']
    if collection.find_one({'username':employee['username']}):
        return 
    collection.insert_one(employee)
    return 

def insert_issues(issue:issue_model, db):
    issue_collection = db['issue']

    if issue_collection.find_one({'id':issue['id']}):
        issue_collection.delete_one({'id':issue['id']})
    issue_collection.insert_one(issue)

def insert_project(project:project_model, db):
    project_collection = db['projects']
    if project_collection.find_one({'id':project['id']}):
        if project_collection.find_one({'id':project['id']})['description'] != project['description']:
            filter = {'id':project['id']}
            newvalues = {'$set':{'description':project['description'], 'updated_at' : datetime.now()}}
            project_collection.update_one(filter, newvalues)
    else:
        project['updated_at'] = datetime.now()
        project['created_at'] = datetime.now()
        project_collection.insert_one(project)

def insert_logs(data, db):
    logs_collection = db['logs']
    data['inserted_at'] = datetime.now()
    logs_collection.insert_one(data)
