from app.db import get_connection
from datetime import datetime, timedelta
import os
from jose import JWTError, jwt



def authenticate_user(username, password):
    db = next(get_connection())
    user_collection = db['login']
    user = user_collection.find_one(
        {'username': username, 'password': password}
    )
    if user:
        return user
    return None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=3)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm="HS256")
    return encoded_jwt


def validate_token(request: dict):
    try:
        token = request['token']
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]
        
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return True
    except JWTError as e:
        print(e)
        return False
