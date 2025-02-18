from django.shortcuts import render, redirect, HttpResponse
from templates import *
from .models import AnalysisFile
from .redis_utils import *
import pandas as pd


# Create your views here.
def LandingPage(request):
    return render(request, 'landing.html')

def AnalyticPage(request, id):
    fileObj = AnalysisFile.objects.get(file_id = id)
    df = pd.read_csv(fileObj.file)
    store_dataframe_in_redis(df, 'redis_df')
    columns = df.columns.tolist()
    rows = df.values.tolist()
    desc_columns = list(df.describe())
    describe = df.describe().to_dict()
    if request.headers.get('HX-Request'):
        return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows,  'describe': describe, 'desc_columns': desc_columns})
    return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows,  'describe' : describe, 'desc_columns': desc_columns})

def RenameFile(request, id):
    fileobj = AnalysisFile.objects.get(file_id = id)
    print('hello')
    if request.method == 'GET':
        print('world')
        new_file_name = request.GET.get("new_name", "").strip()
        if new_file_name:
            print(new_file_name)
            fileobj.file_name = new_file_name
            fileobj.save()
    return redirect('analytic_page', id)

def Details(request, id, colName):
    df = get_dataframe_from_redis_pickle('redis_df') 
    columns = list(df.describe())
    describe = df.describe().to_dict()
    nullcount = df[colName].isnull().sum()
    return render(request, 'components/details.html', {'describe': describe, 'columns': columns, 'nullCount': nullcount})

def UploadFile(request):
    files = AnalysisFile.objects.all()
    return render(request, 'upload_file.html', {"files": files})


def DropNaN(request, id, colName):
    fileobj = AnalysisFile.objects.get(file_id = id)
    df = get_dataframe_from_redis_pickle('redis_df')
    removed_nan_df = df.dropna(subset=[colName])
    print(type(removed_nan_df))
    removed_nan_df.to_csv(fileobj.file.path, index=False)
    store_dataframe_in_redis(removed_nan_df, 'redis_df')
    return redirect('analytic_page', id=id)


def FillNaN(request, id, colName, method):
    fileobj = AnalysisFile.objects.get(file_id=id)
    df = get_dataframe_from_redis_pickle('redis_df')
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
    df.to_csv(fileobj.file.path, index=False)
    store_dataframe_in_redis(df, 'redis_df')
    return redirect('analytic_page', id=id)
