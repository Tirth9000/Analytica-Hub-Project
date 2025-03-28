from flask import Flask, request, session
from flask_cors import CORS
import pandasai as pai
import os, pandas as pd
from decouple import config
import mysql.connector
import json

pai.api_key.set("PAI-4e571b7d-528f-4954-927b-3ee59683b9ce")

app = Flask(__name__)
CORS(app, origins="*")

app.config["SESSION_PERMANENT"] = False
app.secret_key = "csv_client_key"

import logging
import sys
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)


DB_config = {
    "host": config("DB_HOST"),
    "user": config("DB_USER"),
    "password": config("DB_PASSWORD"),
    "database": config("DB_NAME")
}

def execute_query(query, params=None):
    connection = mysql.connector.connect(**DB_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@app.route('/upload-file', methods=['POST'])
def FileLoader(): 
    data = request.json
    query = "SELECT file FROM AnalyticaFiles WHERE file_id = %s"
    query_data = execute_query(query, [data['id']])
    session['file_address'] = query_data[0]["file"]
    return json.dumps({'message': "session stored successfully!", "status": 200})

@app.route('/chat-response', methods=['GET', 'POST'])
def ChatResponse():
    file_add = session.get('file_address')
    df = pai.read_csv('Media/'+file_add)
    data = request.json
    json_str = str(df.chat(data.get("msg", "")))
    response = json.dumps({"response": json_str})
    return {"status": True, "message": response}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
