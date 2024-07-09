import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
        self.BACKEND_HOST = os.getenv("BACKEND_HOST")
        self.BACKEND_PORT = os.getenv("BACKEND_PORT")
        self.RELOAD = self.str_to_bool(os.getenv("RELOAD"))
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.SECRET_KEY = os.getenv("SECRET_KEY")


    @staticmethod
    def str_to_bool(value):
        return value.lower() in ('true', '1', 't', 'y', 'yes')
