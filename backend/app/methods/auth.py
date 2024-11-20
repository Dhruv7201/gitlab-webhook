from app.db import get_connection
from datetime import datetime, timedelta
import os
from jose import JWTError, jwt
import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_user(collection, user):
    user["password"] = hash_password(user["password"])
    collection.insert_one(user.dict())


def authenticate_user(username, password):
    db = next(get_connection())
    user_collection = db["login"]
    users = user_collection.find({"username": username})
    for user in users:
        print(user)
        if verify_password(password, user["password"]):
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
        token = request["token"]
        if token.startswith("Bearer "):
            token = token[len("Bearer ") :]

        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return True
    except JWTError as e:
        print(e)
        return False
