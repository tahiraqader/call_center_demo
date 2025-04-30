
import os
from dotenv import load_dotenv


class Config:
    load_dotenv()  # looks for .env in the current dir
    #MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/call_center'
    MONGO_URI = os.environ.get("MONGO_URI")
