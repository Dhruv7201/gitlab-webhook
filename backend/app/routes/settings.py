from fastapi import APIRouter, Depends, HTTPException
from app.db import get_connection
import os
import requests
from pydantic import BaseModel
from pymongo import ReturnDocument


router = APIRouter()


class UserSchema(BaseModel):
    username: str
    name: str
    email: str
    password: str
    level: str


@router.get("/labels", tags=["settings"])
async def get_labels(db=Depends(get_connection)):
    secret_key = os.getenv("GITLAB_KEY")
    url = "https://code.ethicsinfotech.in/api/v4/groups/39/labels"
    headers = {"Private-Token": secret_key}
    params = {"per_page": 100}
    
    labels = []
    current_page = 1
    while True:
        params["page"] = current_page
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch labels from GitLab API")
        
        data = response.json()
        labels_collection = db["labels"]

        for label in data:
            # Check if label is enabled for user and issue tracking
            user_label = labels_collection.find_one({"name": label["name"], "type": "user", "enabled": True})
            issue_label = labels_collection.find_one({"name": label["name"], "type": "issue", "enabled": True})

            # Set user and issue enabled flags based on the database values
            label['user_enabled'] = True if user_label else False
            label['issue_enabled'] = True if issue_label else False

        labels.extend(data)
        
        total_pages = int(response.headers.get("X-Total-Pages", 1))
        if current_page >= total_pages:
            break
        
        current_page += 1

    return labels

@router.post("/toggle-label", tags=["settings"])
async def toggle_label(request: dict, db=Depends(get_connection)):
    label = request.get('label')
    tracking_type = request.get('type')
    enabled = request.get('enabled')

    if not label or not tracking_type or enabled is None:
        raise HTTPException(status_code=400, detail="Invalid request payload")

    db['labels'].update_one(
        {'name': label, 'type': tracking_type},
        {"$set": {'enabled': enabled}},
        upsert=True
    )
    
    return {"status": True, "message": "Label updated successfully"}


@router.get("/users", tags=["settings"])
async def get_users(db=Depends(get_connection)):
    users_collection = db["login"]
    users = users_collection.find({}, {"_id": 0})
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    users = list(users)
    return {"status": True, "data": users, "message": "Users fetched successfully"}


@router.post("/login_users", tags=["settings"])
async def add_edit_user(user: UserSchema, db=Depends(get_connection)):
    users_collection = db["login"]

    existing_user = users_collection.find_one({"username": user.username})
    
    if existing_user:
        # Edit existing user
        updated_user = users_collection.find_one_and_update(
            {"username": user.username},
            {"$set": user.dict()},
            {"_id": 0},
            return_document=ReturnDocument.AFTER
        )
        if updated_user:
            return {"status": True, "data": updated_user, "message": "User updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="User update failed")
    else:
        if not user.email:
            # take email from gitlab api
            secret_key = os.getenv("GITLAB_KEY")
            url = f"https://code.ethicsinfotech.in/api/v4/users?username={user.username}"
            headers = {"Private-Token": secret_key}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch user details from GitLab API")
            data = response.json()
            user.email = data[0]['email']
        users_collection.insert_one(user.dict())
        return {"status": True, "data": user.dict(), "message": "User added successfully"}


@router.delete("/login_users/{username}", tags=["settings"])
async def delete_user(username: str, db=Depends(get_connection)):
    users_collection = db["login"]
    deleted_user = users_collection.find_one_and_delete({"username": username}, {"_id": 0})
    if deleted_user:
        return {"status": True, "data": deleted_user, "message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    


@router.get("/suggestions", tags=["settings"])
async def get_suggestions(db=Depends(get_connection)):
    suggestions_collection = db["users"]
    # get all the usernames email name from the db
    suggestions = suggestions_collection.find({}, {"_id": 0, "username": 1, "email": 1, "name": 1})
    if not suggestions:
        raise HTTPException(status_code=404, detail="No suggestions found")
    suggestions = list(suggestions)
    return {"status": True, "data": suggestions, "message": "Suggestions fetched successfully"}
