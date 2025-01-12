from django.shortcuts import render, redirect
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
    
    return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows,  'details': details, 'desc_columns': desc_columns})

def Details(request, id):
    df = get_dataframe_from_redis_pickle('redis_df')
    columns = list(df.describe())
    details = df.describe().to_dict()
    return render(request, 'details.html', {'details': details, 'columns': columns})

def UploadFile(request):
    files = AnalysisFile.objects.all()
    return render(request, 'upload_file.html', {"files": files})

