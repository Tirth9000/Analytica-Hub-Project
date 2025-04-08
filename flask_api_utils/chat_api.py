from flask import Flask, request, session, send_file, send_from_directory
from flask_cors import CORS
import pandasai as pai
import os, pandas as pd
from decouple import config
import mysql.connector
import json, shutil
from io import StringIO

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

@app.route('/upload-file', methods=['GET', 'POST'])
def FileLoader(): 
    data = request.json
    query = "SELECT file FROM AnalyticaFiles WHERE file_id = %s"
    query_data = execute_query(query, [data['id']])
    session['file_address'] = query_data[0]["file"]
    return json.dumps({'message': "session stored successfully!", "status": 200})

@app.route('/chat-response', methods=['GET', 'POST'])
def ChatResponse():
    file_address = session.get('file_address')
    df = pai.read_csv('Media/'+file_address)
    data = request.json
    if data:
        gen_response = df.chat(data+" And Provide the response as a single-line string statement instead of a structured format only. If generating plot, make proper naming with proper spacing.")
        if str(type(gen_response)) == "<class 'pandasai.core.response.chart.ChartResponse'>":
            img_name = str(gen_response).replace('exports/charts/', "")
            img_path = f'Media/plot_img/{img_name}'
            gen_response.save(img_path)
            folder_path = "exports/charts"
            shutil.rmtree(folder_path)
            response = json.dumps({"response": img_path, "type": 'img', "status": True})
            return response
        response = json.dumps({"response": str(gen_response), "type": 'text', "status": True})
    else:
        response = json.dumps({"response": "Data not found!", "type": 'error', "status": False})
    return response

@app.route('/api/autoclean/<fileId>', methods=['GET'])
def AutoClean(fileId):
    query = "SELECT file FROM AnalyticaFiles WHERE file_id = %s"
    query_data = execute_query(query, [fileId])
    df = pai.read_csv('Media/' + query_data[0]['file']) 
    print(df)
    ai_response = df.chat(f"""You are a Data Cleaning Assistant.
        TASK: Clean the given CSV/DataFrame and return the CLEANED DATA as raw CSV (No explanation, No charts).
        
        BASIC CLEANING STEPS:
        1. Standardize Column Names:
        - Convert all column names to lowercase.
        - Replace spaces & special characters with underscores.

        2. Remove Duplicates:
        - Drop fully duplicate rows.

        3. Handle Missing Values:
        - Drop columns with >50% missing values.
        - Fill nulls:
        - Numerical Columns → Mean or Median.
        - Categorical Columns → Mode.
        - Datetime Columns → Forward Fill → Backward Fill.

        4. Convert Data Types:
        - Convert numeric-looking strings to numbers.
        - Convert date strings to datetime.

        5. Final Step:
        - Strip spaces from strings.
        - Return cleaned DataFrame as raw CSV in StringResponse.""")
    formated_response = StringIO(str(ai_response))
    cleaned_df = pd.read_csv(formated_response)
    columns = cleaned_df.columns.tolist()
    rows = cleaned_df.values.tolist()
    response = json.dumps({'columns': columns, 'rows': rows})
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    