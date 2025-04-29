from flask import Flask
from flask_pymongo import PyMongo
from .config import Config
#from .routes import create_call # this was working before might need to uncomment
from .utils import transcribe_stereo_file_dialog


# Create mongo instance but don't bind it yet
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
     # Initialize the MongoDB connection
    mongo.init_app(app)
    # Register the routes from routes.py with a prefix '/create' //TQ add other here
    # Import routes AFTER mongo.init_app(app)
    from .routes import create_call
    app.register_blueprint(create_call)
    return app
