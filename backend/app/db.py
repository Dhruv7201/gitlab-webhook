import os
import pymongo


def get_connection():
    db_url = os.getenv('DATABASE_URL')
    client = pymongo.MongoClient(db_url)
    db = client['GitlabDemo']
    yield db

