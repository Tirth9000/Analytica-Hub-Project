from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from .middleware import with_skeleton, redo_with_skeleton, undo_with_skeleton
from .models import AnalyticaFiles
from utility.redis_utils import *
from .main_tasks import *
from templates import *
import pandas as pd
import requests, random
from uuid import uuid4


# Create your views here.
def LandingPage(request):
    return render(request, 'landing.html')


def AnalyticPage(request, id):
    reset_queue_to_current_node_only(id)
    fileObj = AnalyticaFiles.objects.get(file_id = id)
    if not check_key(id): 
        clear_all()
    if request.headers.get('HX-Request'):
        data = get_current_node(id)
        if data:
            columns = data["columns"]
            rows = data["rows"]
            df = pd.DataFrame(rows, columns=columns)
        else:
            df = pd.read_csv(fileObj.file_path)
            columns = df.columns.tolist()
            rows = df.values.tolist()
            push_data(id, rows, columns)
        if len(rows) > 10000:
            rows = rows[:10000]
        shape = df.shape
        return render(request, 'components/dataset_table.html', {"file_id": id, "columns": columns, "rows": rows, 'shape': shape})
    return render(request, 'analytic.html', {"file": fileObj})


def UploadFile(request):
    if request.method == "POST":
        file = request.FILES.get('dataFile')
        newId = uuid4().hex[:6].upper() 
        while AnalyticaFiles.objects.filter(file_id=newId).exists():
            newId = uuid4().hex[:6].upper()
        if file:
            file_name = file.name
            new_file = AnalyticaFiles.objects.create(
                file_id = newId,
                file_name=file_name, 
                file_path=file
                )
            new_file.save()
            return JsonResponse({"status": "success", "message": f"File '{file_name}' uploaded successfully."})
        return JsonResponse({"status": "error", "message": "No file provided."}, status=400)
    clear_all()
    files = AnalyticaFiles.objects.all()
    return render(request, 'upload_file.html', {"files": files})

def DeleteFile(request, id):
    file = AnalyticaFiles.objects.get(file_id = id)
    file.delete()
    return redirect('upload_file')


def RenameFile(request, id):
    fileobj = AnalyticaFiles.objects.get(file_id = id)
    if request.method == 'GET':
        new_file_name = request.GET.get("new_name", "").strip()
        if new_file_name:
            fileobj.file_name = new_file_name
            fileobj.save()
    return redirect('analytic_page', id)


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


@with_skeleton()
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
    shape = df.shape
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows, 'shape': shape})


@with_skeleton()    
def DropNaN(request, id, colName):
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
    shape = removed_nan_df.shape
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows, 'shape': shape})


@with_skeleton()
def FillNaN(request, id, colName, method):
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
    shape = df.shape
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows, 'shape': shape})


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


@with_skeleton()
def AutoCleaning(request, id):
    url = f"http://analytica_flask:5000/api/autoclean/{id}" 
    response = session.get(url)
    data = response.json()
    columns = data["columns"]
    rows = data["rows"]
    push_data(id, rows, columns)
    df = pd.DataFrame(rows, columns=columns)
    if len(rows) > 10000:
        rows = rows[:10000]
    shape = df.shape
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows, 'shape': shape})


def save_changes(request, id):
    fileObj = AnalyticaFiles.objects.get(file_id = id) 
    if request.method == "POST":
        newFile = get_current_node()
        if newFile:
            columns = newFile["columns"]
            rows = newFile["rows"]
            updated_df = pd.DataFrame(rows, columns=columns)
        updated_df.to_csv(f"{fileObj.file_path}.csv", index=False)
    return HttpResponse()


def Export(request, id):
    if request.method == "GET":
        file_name = AnalyticaFiles.objects.get(file_id=id).file_name
        data = get_current_node(id)
        if data:
            columns = data["columns"]
            rows = data["rows"]
            df = pd.DataFrame(rows, columns=columns)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'
            df.to_csv(response, index=False)
            return response


@undo_with_skeleton()
def undo_action(request, id):
    data = undo(id)
    if data:
        rows = data["rows"]
        columns = data["columns"]
        df = pd.DataFrame(rows, columns=columns)
        if len(rows) > 10000:
            rows = rows[:10000]
        shape = df.shape
        return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows, 'shape': shape})
    

@redo_with_skeleton()
def redo_action(request, id):
    data = redo(id)
    if data == None:
        return None
    rows = data["rows"]
    columns = data["columns"]
    df = pd.DataFrame(rows, columns=columns)
    if len(rows) > 10000:
        rows = rows[:10000]
    shape = df.shape
    return render(request, 'components/dataset_table.html', {'file_id': id, 'columns': columns, 'rows': rows, 'shape': shape})