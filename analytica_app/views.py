from django.shortcuts import render, redirect, HttpResponse
from templates import *
from .models import AnalyticaFiles
from .redis_utils import *
import io, sys
import pandas as pd
import requests, io, json

# Create your views here.
def LandingPage(request):
    return render(request, 'landing.html')


def AnalyticPage(request, id):
    session_id = get_session_id(request)
    reset_queue_to_current_node_only(session_id)
    data = get_current_node(session_id)
    fileObj = AnalyticaFiles.objects.get(file_id = id)
    if data:
        columns = data["column"]
        rows = data["row"]
        df = pd.DataFrame(rows, columns=columns)
    else:
        df = pd.read_csv(fileObj.file)
        store_dataframe_in_redis(df, 'redis_df')
        columns = df.columns.tolist()
        rows = df.values.tolist()
        push_data(session_id, rows, columns)
        
    desc_columns = list(df.describe())
    describe = df.describe().to_dict()
    if request.headers.get('HX-Request'):
        return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows,  'describe': describe, 'desc_columns': desc_columns})
    return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows,  'describe' : describe, 'desc_columns': desc_columns})


def RenameFile(request, id):
    fileobj = AnalyticaFiles.objects.get(file_id = id)
    if request.method == 'GET':
        new_file_name = request.GET.get("new_name", "").strip()
        if new_file_name:
            fileobj.file_name = new_file_name
            fileobj.save()
    return redirect('analytic_page', id)


def UploadFile(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    clear_user_session_data(session_id)
    files = AnalyticaFiles.objects.all()
    return render(request, 'upload_file.html', {"files": files})


def Details(request, id, colName):
    session_id = get_session_id(request)
    data = get_current_node(session_id)
    if data:
        columns = data["column"]
        rows = data["row"]
        df = pd.DataFrame(rows, columns=columns)
    columns = list(df.describe())
    describe = df.describe().to_dict()
    nullcount = df[colName].isnull().sum()
    return render(request, 'components/details.html', {'describe': describe, 'columns': columns, 'nullCount': nullcount})


def DropNaN(request, id, colName):
    fileobj = AnalyticaFiles.objects.get(file_id = id)
    session_id = get_session_id(request)
    data = get_current_node(session_id)
    if data:
        columns = data["column"]
        rows = data["row"]
        df = pd.DataFrame(rows, columns=columns)
    removed_nan_df = df.dropna(subset=[colName])
    columns = removed_nan_df.columns.tolist()
    rows = removed_nan_df.values.tolist()
    push_data(session_id, rows, columns)
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})


def FillNaN(request, id, colName, method):
    fileobj = AnalyticaFiles.objects.get(file_id=id)
    session_id = get_session_id(request)
    data = get_current_node(session_id)
    if data:
        columns = data["column"]
        rows = data["row"]
        df = pd.DataFrame(rows, columns=columns)
    if method =='ffill':
        df[colName] = df[colName].ffill()
    elif method == 'bfill':
        df[colName] = df[colName].bfill()
    elif (method == 'mean') and (df[colName].dtype != object):
        df[colName] = df[colName].fillna(df[colName].mean().round(2))
    elif (method == 'median') and (df[colName].dtype != object):
        df[colName] = df[colName].fillna(df[colName].median().round(2))
    elif method == 'mode':
        df[colName] = df[colName].fillna(df[colName].mode()[0])
    else:
        df
    columns = df.columns.tolist()
    rows = df.values.tolist()
    push_data(session_id, rows, columns)
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})


def PythonCodeSpace(request, id):
    if request.method == 'POST':
        code = request.POST.get('code')
        capture_stdout = io.StringIO()
        sys.stdout = capture_stdout
        output = {"print": "", "error": ""}
        file_address = AnalyticaFiles.objects.get(file_id = id).file
        df = pd.read_csv(f"Media/{file_address}")
        try:
            exec(code)
            output["print"] = capture_stdout.getvalue()
            return HttpResponse(output["print"])
        except Exception as e:
            output["error"] = str(e)
            return HttpResponse(output["error"])
        finally:
            sys.stdout = sys.__stdout__
    return HttpResponse("hello")


session = requests.Session()
def ChatWithCSV(request, id):
    url = "http://analytica_flask:5000/upload-file"
    data = {'id': id}
    res = session.post(url, json=data)
    if request.method == "POST":
        url = "http://analytica_flask:5000/chat-response"
        client_msg = request.POST.get('msg')
        data = session.post(url, json=client_msg)
        result = data.json()
        if result['type'] == 'img':
            return HttpResponse(f'<img class="message received-img" src="/{result["response"]}">')
        return HttpResponse(f'<div class="message received">{result["response"]}</div>')
    return render(request, 'live_chat.html', {"file_id": id})


def AutoCleaning(request, id):
    session_id = get_session_id(request)
    if request.method == "POST":
        return render(request, 'components/skeleton_table.html', {"id": id}) 
    if request.method == 'GET':
        url = f"http://analytica_flask:5000/api/autoclean/{id}" 
        response = session.get(url)
        data = response.json()
        columns = data["columns"]
        rows = data["rows"]
        push_data(session_id, rows, columns)
        return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})


def get_session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def undo_action(request, id):
    session_id = get_session_id(request)
    data = undo(session_id)
    rows = data["row"]
    columns = data["column"]
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})

def redo_action(request, id):
    session_id = get_session_id(request)
    data = redo(session_id)
    rows = data["row"]
    columns = data["column"]
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})