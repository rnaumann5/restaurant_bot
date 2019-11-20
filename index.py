# /index.py
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os
import dialogflow
import requests
import json
import pusher

client = MongoClient ("mongodb+srv://shotgunwillie_420:admin@restaurants-0thxz.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.get_database('arden_db')
records = db.nyc_restaurants

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    # build GET request
    data = request.get_json(silent=True)
    # pull city parameter from payload
    side = data['queryResult']['outputContexts'][0]['parameters']['nyc_neighborhoods']
    # build query object using city from payload
    query_request = records.find_one({"neighborhood": side}, {"restaurant_name": 1})
    # extract result from query request into correct format
    query_response = query_request['restaurant_name']
    if data is not "":
        reply = {
            "fulfillmentText": "Here are some options: {}".format(query_response)
            }
        return jsonify(reply)


    else:
        reply = {
            "fulfillmentText": "please enter a response",
        }
        return jsonify(reply)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }
    return jsonify(response_text)

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        return response.query_result.fulfillment_text

# run Flask app
if __name__ == "__main__":
    app.run()
