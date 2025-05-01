from flask import Flask
from flask_pymongo import PyMongo
from .config import Config
#from .routes import create_call # TQ this was working before might need to uncomment
from .utils import transcribe_stereo_file_dialog
from flask_cors import CORS



# Create mongo instance but don't bind it yet
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Enable CORS for all routes and origins
    CORS(app)
    # Initialize the MongoDB connection
    mongo.init_app(app)
    # Register the routes 
    from .routes import create_call
    app.register_blueprint(create_call)
    
    return app
