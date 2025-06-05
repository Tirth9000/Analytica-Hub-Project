from django.shortcuts import render, redirect, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from .middleware import with_skeleton, redo_with_skeleton, undo_with_skeleton
from .models import AnalyticaFiles
from utility.redis_utils import *
from .main_tasks import *
from templates import *
import pandas as pd
import requests, io
import io, sys

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
            df = pd.read_csv(fileObj.file)
            columns = df.columns.tolist()
            rows = df.values.tolist()
            push_data(id, rows, columns)
        if len(rows) > 10000:
            rows = rows[:10000]
        shape = df.shape
        return render(request, 'components/dataset_table.html', {"file_id": id, "columns": columns, "rows": rows, 'shape': shape})
    return render(request, 'analytic.html', {"file": fileObj})


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


# @with_skeleton()
# def PythonCodeSpace(request, id):
#     if request.method == 'GET':
#         code = request.session.get('code', '')
#         # capture_stdout = io.StringIO()
#         # sys.stdout = capture_stdout
#         # output = {"print": "", "error": ""}
#         data = get_current_node(id)
#         if data:
#             columns = data["columns"]
#             rows = data["rows"]
#             df = pd.DataFrame(rows, columns=columns)
#         try:
#             exec_env = {'df': df, 'pd': pd}
#             exec(code, {}, exec_env)
#             print(exec_env['df'])  # This will print the DataFrame to the console
#             # output["print"] = capture_stdout.getvalue()
#             rows = exec_env['df'].values.tolist()
#             columns = exec_env['df'].columns.tolist()
#             push_data(id, rows, columns)
#             if len(rows) > 10000:
#                 rows = rows[:10000]
#             shape = exec_env['df'].shape  # Updated to use exec_env['df']
#             return render(request, 'components/dataset_table.html', {"file_id": id, "rows": rows, "columns": columns, 'shape': shape})
#         except Exception as e:
#             # output["error"] = str(e)
#             return HttpResponse(f"<p id='output' hx-swap-oob='true'>{str(e)}</p>")
#         finally:
#             sys.stdout = sys.__stdout__
#     return HttpResponse("Something went wrong, please try again later.")


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
        updated_df.to_csv(f"{fileObj.file}.csv", index=False)
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

    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def UploadFile(request):
    # if request.method == "POST":
    #     random_id = random.randint(1000, 9999) 
    #     letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    #     new_file_id =  str(letters + str(random_id))
    #     new_file = AnalyticaFiles.objects.create(
    #         file_id = new_file_id,
    #         # file_name = 
    #     )
    #     pass
    clear_all()
    files = AnalyticaFiles.objects.all()
    return render(request, 'upload_file.html', {"files": files})