from django.shortcuts import render, redirect, HttpResponse
from templates import *
from .models import AnalyticaFiles
from utility.redis_utils import *
import io, sys
import pandas as pd
import requests, io, json

# Create your views here.
def LandingPage(request):
    return render(request, 'landing.html')


def AnalyticPage(request, id):
    reset_queue_to_current_node_only(id)
    fileObj = AnalyticaFiles.objects.get(file_id = id)
    if not check_key(id): 
        clear_all()
    data = get_current_node(id)
    if data:
        columns = data["columns"]
        rows = data["rows"]
        df = pd.DataFrame(rows, columns=columns)
    else:
        df = pd.read_csv(fileObj.file)
        columns = df.columns.tolist()
        rows = df.values.tolist()
        push_data(id, rows, columns)
    if len(rows) > 10000:
        rows = rows[:10000]
        # fileObj.file.seek(0)
        # df_iterator = pd.read_csv(fileObj.file, chunksize=10000)
        # first_chunk = next(df_iterator)
        # rows = first_chunk.values.tolist()
        # columns = first_chunk.columns.tolist()
    shape = df.shape
    if request.headers.get('HX-Request'):
        return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows, 'shape': shape})
    return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows, 'shape': shape})


def RenameFile(request, id):
    fileobj = AnalyticaFiles.objects.get(file_id = id)
    if request.method == 'GET':
        new_file_name = request.GET.get("new_name", "").strip()
        if new_file_name:
            fileobj.file_name = new_file_name
            fileobj.save()
    return redirect('analytic_page', id)


def UploadFile(request):
    clear_all()
    files = AnalyticaFiles.objects.all()
    return render(request, 'upload_file.html', {"files": files})


def Details(request, id, colName):
    data = get_current_node(id)
    if data:
        columns = data["columns"]
        rows = data["rows"]
        df = pd.DataFrame(rows, columns=columns)
    columns = list(df.describe())
    describe = df.describe().to_dict()
    nullcount = df.isnull().sum().sum()
    emptycount = (df == '').sum().sum()
    duplicatecount = df.duplicated().sum()
    uniquecount = df.nunique().sum()
    
    return render(request, 'components/details.html', {'describe': describe, 
               'columns': columns, 
               'nullcount': nullcount, 
               'emptycount': emptycount, 
               'duplicatecount': duplicatecount, 
               'uniquecount': uniquecount
               })

def DropColumn(request, id, colName):
    data = get_current_node(id)
    if data:
        columns = data['columns']
        rows = data['rows']
        df = pd.DataFrame(rows, columns=columns)
    df.drop(colName, axis=1, inplace=True)
    columns = df.columns.tolist()
    rows = df.values.tolist()
    push_data(id, rows, columns)
    if len(rows) > 10000:
        rows = rows[:10000]
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})

    
def DropNaN(request, id, colName):
    fileobj = AnalyticaFiles.objects.get(file_id = id)
    data = get_current_node(id)
    if data:
        columns = data["columns"]
        rows = data["rows"]
        df = pd.DataFrame(rows, columns=columns)
    removed_nan_df = df.dropna(subset=[colName])
    columns = removed_nan_df.columns.tolist()
    rows = removed_nan_df.values.tolist()
    push_data(id, rows, columns)
    if len(rows) > 10000:
        rows = rows[:10000]
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})


def FillNaN(request, id, colName, method):
    fileobj = AnalyticaFiles.objects.get(file_id=id)
    data = get_current_node(id)
    if data:
        columns = data["columns"]
        rows = data["rows"]
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
    push_data(id, rows, columns)
    if len(rows) > 10000:
        rows = rows[:10000]
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})


def PythonCodeSpace(request, id):
    if request.method == 'POST':
        code = request.POST.get('code')
        capture_stdout = io.StringIO()
        sys.stdout = capture_stdout
        output = {"print": "", "error": ""}
        data = get_current_node(id)
        if data:
            columns = data["columns"]
            rows = data["rows"]
            df = pd.DataFrame(rows, columns=columns)
        try:
            exec(code)
            output["print"] = capture_stdout.getvalue()
            rows = df.values.tolist()
            columns = df.columns.tolist()
            push_data(id, rows, columns)
            if len(rows) > 10000:
                rows = rows[:10000]
            return render(request, 'components/dataset_table.html', {"file_id": id, "rows": rows, "columns": columns})
            return HttpResponse(output["print"])
        except Exception as e:
            output["error"] = str(e)
            return HttpResponse(output["error"])
        finally:
            sys.stdout = sys.__stdout__
    return HttpResponse("hello")


session = requests.Session()
def ChatWithCSV(request, id):
    if request.method == "POST":
        url = "http://analytica_flask:5000/chat-response"
        client_msg = request.POST.get('msg')
        data = {'id': id, 'client_msg': client_msg}
        response = session.post(url, json=data)
        result = response.json()
        if result['type'] == 'img':
            return HttpResponse(f'<img class="message received-img" src="/{result["response"]}">')
        return HttpResponse(f'<div class="message received">{result["response"]}</div>')
    return render(request, 'live_chat.html', {"file_id": id})


def AutoCleaning(request, id):
    if request.method == "POST":
        return render(request, 'components/skeleton_table.html', {"id": id}) 
    if request.method == 'GET':
        url = f"http://analytica_flask:5000/api/autoclean/{id}" 
        response = session.get(url)
        data = response.json()
        columns = data["columns"]
        rows = data["rows"]
        push_data(id, rows, columns)
        if len(rows) > 10000:
            rows = rows[:10000]
        return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})


def save_changes(request, id):
    fileObj = AnalyticaFiles.objects.get(file_id = id) 
    if request.method == "POST":
        newFile = get_current_node()
        if newFile:
            columns = newFile["columns"]
            rows = newFile["rows"]
            updated_df = pd.DataFrame(rows, columns=columns)
        updated_df.to_csv(f"{fileObj.file}.csv", index=False)
    return HttpResponse()

def undo_action(request, id):
    data = undo(id)
    if data == None:
       return None
    rows = data["rows"]
    columns = data["columns"]
    if len(rows) > 10000:
        rows = rows[:10000]
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})

def redo_action(request, id):
    data = redo(id)
    if data == None:
        return None
    rows = data["rows"]
    columns = data["columns"]
    if len(rows) > 10000:
        rows = rows[:10000]
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows})