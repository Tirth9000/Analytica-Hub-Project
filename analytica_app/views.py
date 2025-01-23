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
    details = df.describe().to_dict()
    if request.headers.get('HX-Request'):
        return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows,  'details': details, 'desc_columns': desc_columns})
    return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows,  'details': details, 'desc_columns': desc_columns})

def Details(request, id, colName):
    df = get_dataframe_from_redis_pickle('redis_df') 
    columns = list(df.describe())
    details = df.describe().to_dict()
    nullcount = df[colName].isnull().sum()
    return render(request, 'components/details.html', {'details': details, 'columns': columns, 'nullCount': nullcount})

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


def FillNaN(request, id, colName, type):
    fileobj = AnalysisFile.objects.get(file_id=id)
    df = get_dataframe_from_redis_pickle('redis_df')

    if type =='ffill':
        df[colName] = df[colName].ffill()
    elif type == 'bfill':
        df[colName] = df[colName].bfill()
    elif type == 'mean':
        df[colName] = df[colName].fillna(df[colName].mean(numeric_only=False)[0])
    elif type == 'median':
        df[colName] = df[colName].fillna(df[colName].median()[0])
    elif type == 'mode':
        df[colName] = df[colName].fillna(df[colName].mode()[0])
    df.to_csv(fileobj.file.path, index=False)
    store_dataframe_in_redis(df, 'redis_df')
    return redirect('analytic_page', id=id)
