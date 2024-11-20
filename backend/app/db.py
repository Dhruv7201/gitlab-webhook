import os
import pymongo
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    db_url = os.getenv("DATABASE_URL")
    client = pymongo.MongoClient(db_url)
    db = client["GitlabReports"]
    yield db
