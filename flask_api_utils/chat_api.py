from flask import Flask, request, session, send_file, send_from_directory
from flask_cors import CORS
import pandasai as pai
import os, pandas as pd
from decouple import config
import mysql.connector
import json, shutil

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
    file_add = session.get('file_address')
    df = pai.read_csv('Media/'+file_add)
    data = request.json
    if data:
        gen_response = df.chat(data+" And Provide the response as a single-line string statement instead of a structured format only. If generating plot, make proper naming with proper spacing.")
        if str(type(gen_response)) == "<class 'pandasai.core.response.chart.ChartResponse'>":
            img_name = str(gen_response).replace('exports/charts/', "")
            img_path = f'Media/plot_img/{img_name}'
            gen_response.save(img_path)
            folder_path = "exports/charts"
            shutil.rmtree(folder_path)
            print(img_path)
            response = json.dumps({"response": img_path, "type": 'img', "status": True})
            return response
        response = json.dumps({"response": str(gen_response), "type": 'text', "status": True})
    else:
        response = json.dumps({"response": "Data not found!", "type": 'error', "status": False})
    return response

@app.route('/api-autoclean', methods=['GET'])
def AutoClean():
    pass 
    data = request.json
    query = "SELECT file FROM AnalyticaFiles WHERE file_id = %s"
    query_data = execute_query(query, [data['id']])
    
    new_df = df.chat(f"""You are a professional data cleaning assistant. Your task is to clean a given tabular dataset (CSV or DataFrame) and return a cleaned version for data analysis and modeling. 
                Follow the steps below with intelligent, context-aware logic.
                OBJECTIVE:
                Clean the dataset thoroughly and return the cleaned version as a raw CSV format (no explanations, no charts).
                ---
                CLEANING STEPS:
                1.  Standardize Column Names:
                - Convert all column names to lowercase and snake_case.
                - Remove special characters, trim whitespace.
                2. Handle Special & Uncertain Values:
                - Convert uncertain strings like:
                    - `"unknown"`, `"n/a"`, `"na"`, `"error"`, `"null"`, `"missing"`, `"not available"`, `"--"` etc.
                    - To standard missing values (`np.nan` or `None`) for all data types.
                - Apply this for **all** column types: numeric, categorical, date, etc.
                3. Remove Duplicate Rows:
                - Drop rows that are fully duplicated.
                - Drop duplicates conditionally if specific key columns exist.
                4. Handle Missing Data:
                - Drop columns with more than 50% missing values.
                - For **numerical columns**:
                    - Use mean (if normally distributed), median (if skewed).
                - For **categorical columns**:
                    - Use mode or most frequent category.
                - For **datetime columns**:
                    - Use forward/backward fill or infer based on sequence.
                - For special columns (e.g., country from email): infer logically if possible.
                5. Outlier Detection & Treatment:
                - Use IQR and/or Z-score method to identify outliers.
                - Do **not** remove valid but extreme values (e.g., age 99, sales 10000).
                - Remove/cap outliers if:
                    - Z > 3 or falls outside 1.5×IQR,
                    - They distort distribution,
                    - Count of such points is low.
                - Apply log/box-cox transformation if highly skewed.
                - Do **not** create extra outlier columns unless explicitly required.
                6. Convert Data Types Appropriately:
                - Convert object-type numerics to actual numeric (remove `$`, `%`, `,`).
                - Convert valid date strings to datetime.
                - Convert suitable columns to `category` dtype.
                7. Clean Strings and Categorical Values:
                - Strip leading/trailing spaces.
                - Convert to lowercase or title case consistently.
                - Normalize similar categories (e.g., “Cash ”, “cash”, “CASH” → “cash”).
                - Remove noise characters (e.g., special symbols in names or categories).
                8. Numeric & Logic Checks:
                - Ensure numeric fields like price, quantity, or scores are non-negative unless valid negatives (like returns).
                - Validate rating scales (e.g., clip to 0–5).
                - Remove or fix non-parsable numbers.
                9. Final Output:
                - Ensure every column is usable for analysis.
                - Dataset must be free of messy values, uncertainty terms, and type inconsistencies.
                - Return the cleaned DataFrame **only** as CSV.
                ---
                DO NOT:
                - Leave uncertain values untreated.
                - Add additional columns unless required for fixing.
                - Return any description, explanation, or plots.
                Treat values with real-world and statistical understanding — act like a human data analyst cleaning a business-critical dataset.""")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    