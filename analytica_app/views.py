from django.shortcuts import render, redirect
from templates import *
from .models import AnalysisFile

# Create your views here.
def LandingPage(request):
    return render(request, 'landing.html')

def AnalyticPage(request, id):
    dataFile = AnalysisFile.objects.get(file_id = id)
    return render(request, 'analytic.html', {"file": dataFile})

def UploadFile(request):
    files = AnalysisFile.objects.all()
    return render(request, 'upload_file.html', {"files": files})

