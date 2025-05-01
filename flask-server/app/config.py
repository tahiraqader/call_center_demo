
import os
from dotenv import load_dotenv


class Config:
    load_dotenv()  # looks for .env in the current dir
    MONGO_URI = os.environ.get("MONGO_URI")
