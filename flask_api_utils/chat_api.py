from flask import Flask, request, session, send_file, send_from_directory
from flask_cors import CORS
import pandasai as pai
import os, pandas as pd
from decouple import config
import json, shutil
from io import StringIO

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from utility.redis_utils import get_current_node

pai.api_key.set("PAI-4e571b7d-528f-4954-927b-3ee59683b9ce")

app = Flask(__name__)
CORS(app, origins="*")

app.config["SESSION_PERMANENT"] = False
app.secret_key = "csv_client_key"

import logging
import sys
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)


@app.route('/chat-response', methods=['GET', 'POST'])
def ChatResponse():
    client_data = request.json
    data = get_current_node(client_data["id"])
    if data:
        columns = data["columns"]
        rows = data["rows"]
        df = pai.DataFrame(rows, columns=columns)
    if client_data:
        gen_response = df.chat(client_data["client_msg"] + "And Provide the response as a single-line string statement instead of a structured format only. If generating plot, make proper naming with proper spacing.")
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



@app.route('/api/autoclean/<id>', methods=['POST', 'GET'])
def AutoClean(id):
    data = get_current_node(id)
    if data:
        columns = data["columns"]
        rows = data["rows"]
        df = pai.DataFrame(rows, columns=columns)
    ai_response = df.chat(f"""You are a Data Cleaning Assistant.

TASK: Clean the given CSV/DataFrame and return the CLEANED DATA as raw CSV (No explanation, No charts).

=> First of all perform this step then go for Basic Cleaning: 
-> Replace Dirty Values (case-insensitive) across all columns:
  Replace these values (in any case variation like 'ERROR', 'Error', 'error', 'Unknown', 'UNKNOWN' etc.) with np.nan:

BASIC CLEANING STEPS:

1. Standardize Column Names:
- Convert all column names to lowercase.
- Replace spaces & special characters with underscores.

2. Convert Data Types:
- Convert numeric-looking strings to numbers.
- Convert date strings to datetime.

3. Handle Missing Values:
- Drop columns with >50% missing values.
- Fill nulls:
  - Numerical Columns → Mean or Median.
  - Categorical Columns → Mode.
  - Datetime Columns → Forward Fill → Backward Fill.

4. Remove Duplicates:
- Drop fully duplicate rows.

5. Final Step:
- Strip spaces from strings.
- STRICKLY - Beforing responding check all above steps properly even after performing on the dataset.
- Return cleaned DataFrame as raw CSV in StringResponse, but don't create new file strickly.""")

    formated_response = StringIO(str(ai_response))
    cleaned_df = pd.read_csv(formated_response)
    columns = cleaned_df.columns.tolist()
    rows = cleaned_df.values.tolist()
    response = json.dumps({'columns': columns, 'rows': rows})
    return response




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    