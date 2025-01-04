from django.shortcuts import render, redirect
from templates import *
from .models import AnalysisFile
import pandas as pd

# Create your views here.
def LandingPage(request):
    return render(request, 'landing.html')

def AnalyticPage(request, id):
    fileObj = AnalysisFile.objects.get(file_id = id)
    df = pd.read_csv(fileObj.file)
    print(df)
    columns = df.columns.tolist()
    rows = df.values.tolist()
    return render(request, 'analytic.html', {"file": fileObj, "columns": columns, "rows": rows})

def Details(request, id):
    fileObj = AnalysisFile.objects.get(file_id = id)
    df = pd.read_csv(fileObj.file)
    columns = list(df.describe())
    details = df.describe().to_dict()
    return render(request, 'details.html', {'details': details, 'columns': columns})

def UploadFile(request):
    files = AnalysisFile.objects.all()
    return render(request, 'upload_file.html', {"files": files})

