# from flask import Blueprint, request, jsonify
# from werkzeug.utils import secure_filename
# import os
# from .utils import  process_call, summarize_conversation
# from scipy.io import wavfile
# import io
# from . import mongo
# UPLOAD_FOLDER = 'uploads/'
# ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac'}  # Add any other formats you support


# # All the REST API endpint should be here

# create_call = Blueprint('create_call', __name__)
# # Define the 'create' route on the blueprint
# @create_call.route('/create', methods=['POST'])
# def create_call_route():
   
#     file = request.files.get('file')
#     filename= 'xxx'
#     file_content=''
#     if file:
#     # Now 'file' is a FileStorage object from Werkzeug
#     # You can read or save it
#         # or
#         filename = file.filename     # get the uploaded filename
#         # Read the file into memory
#         wav_bytes = file.read()
        
#         # Use scipy to read sample rate and audio data
#         sample_rate, audio_data = wavfile.read(io.BytesIO(wav_bytes))
        
#         res = process_call(audio_data, sample_rate)
#         # Insert into MongoDB
#         inserted = mongo.db.calls.insert_one(res)
       
#         return jsonify(res)

#     else:
#         # Handle case where no file was uploaded
#         print("No file part found")
    
#     return jsonify(filename)

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import io
from bson import ObjectId
from bson.json_util import dumps
from .utils import process_call, summarize_conversation
from scipy.io import wavfile
from . import mongo
from datetime import date
from datetime import datetime


# UPLOAD_FOLDER = 'uploads/'
# ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac'}

create_call = Blueprint('create_call', __name__)

@create_call.route('/create', methods=['POST'])
def create_call_route():
    print(" in create")
    file = request.files.get('file')
    if file:
        filename = secure_filename(file.filename)
        wav_bytes = file.read()
        sample_rate, audio_data = wavfile.read(io.BytesIO(wav_bytes))
        res = process_call(audio_data, sample_rate)
        res['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inserted = mongo.db.calls.insert_one(res)
        res['_id'] = str(inserted.inserted_id)
        
        return jsonify(res), 201 
    return jsonify({'error': 'No file provided'}), 400

@create_call.route('/calls', methods=['GET'])
def get_calls():
    print(" in ")
    calls = list(mongo.db.calls.find())
    for call in calls:
        call['_id'] = str(call['_id'])
    return jsonify(calls), 200

@create_call.route('/update/<string:call_id>', methods=['PUT'])
def update_call(call_id):
    update_data = request.json
    result = mongo.db.calls.update_one({'_id': ObjectId(call_id)}, {'$set': update_data})
    if result.matched_count:
        return jsonify({'msg': 'Call updated successfully'}), 200
    return jsonify({'error': 'Call not found'}), 404

@create_call.route('/delete/<string:call_id>', methods=['DELETE'])
def delete_call(call_id):
    result = mongo.db.calls.delete_one({'_id': ObjectId(call_id)})
    if result.deleted_count:
        return jsonify({'msg': 'Call deleted successfully'}), 200
    return jsonify({'error': 'Call not found'}), 404
