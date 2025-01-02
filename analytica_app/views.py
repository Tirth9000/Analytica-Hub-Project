from django.shortcuts import render, redirect
from templates import *
from .models import AnalysisFile
import pandas as pd

# Create your views here.
def LandingPage(request):
    return render(request, 'landing.html')

def AnalyticPage(request, id):
    # dataFile = AnalysisFile.objects.get(file_id = id)
    dataFile = 'hello'
    datafile = pd.read_csv('shopping_trends.csv')
    columns = datafile.columns.tolist()
    rows = datafile.values.tolist()
    return render(request, 'analytic.html', {"file": dataFile, "columns": columns, "rows": rows})

def UploadFile(request):
    files = AnalysisFile.objects.all()
    return render(request, 'upload_file.html', {"files": files})

