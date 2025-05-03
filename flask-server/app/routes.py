from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import io
from bson import ObjectId
from bson.json_util import dumps
from .utils import process_call,  extract_action_items_from_transcript
from scipy.io import wavfile
from . import mongo
from datetime import date
from datetime import datetime
from .types import Call


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
        print(" ======== data writen to db ", res)
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
    #normally used for summary in current implementation
    # update the action items as well.
    summary = update_data['summary']
    if (summary):
        action_items = extract_action_items_from_transcript(summary)
        update_data['action_items'] = action_items
    result = mongo.db.calls.update_one({'_id': ObjectId(call_id)}, {'$set': update_data})
    print("============result", result)
    if result.matched_count:
        return jsonify({'msg': 'Call updated successfully'}), 200
    return jsonify({'error': 'Call not found'}), 404

@create_call.route('/delete/<string:call_id>', methods=['DELETE'])
def delete_call(call_id):
    result = mongo.db.calls.delete_one({'_id': ObjectId(call_id)})
    if result.deleted_count:
        return jsonify({'msg': 'Call deleted successfully'}), 200
    return jsonify({'error': 'Call not found'}), 404
