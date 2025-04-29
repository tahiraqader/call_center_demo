from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from .utils import  process_call, summarize_conversation
from scipy.io import wavfile
import io
from . import mongo
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac'}  # Add any other formats you support


# Create a Blueprint for the 'create_call' endpoint
create_call = Blueprint('create_call', __name__)

# Define the 'create' route on the blueprint
@create_call.route('/create', methods=['POST'])
def create_call_route():
   
    file = request.files.get('file')
    filename= 'xxx'
    file_content=''
    if file:
    # Now 'file' is a FileStorage object from Werkzeug
    # You can read or save it
        # or
        filename = file.filename     # get the uploaded filename
        # Read the file into memory
        wav_bytes = file.read()
        
        # Use scipy to read sample rate and audio data
        sample_rate, audio_data = wavfile.read(io.BytesIO(wav_bytes))
        
        res = process_call(audio_data, sample_rate)
        # Insert into MongoDB
        inserted = mongo.db.calls.insert_one(res)
       
        return jsonify(res)

    else:
        # Handle case where no file was uploaded
        print("No file part found")
    
    return jsonify(filename)