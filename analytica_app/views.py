from django.shortcuts import render, redirect
from templates import *

# Create your views here.
def LandingPage(request):
    return render(request, 'landing.html')


def AnalyticPage(request):
    return render(request, 'analytic.html')

def UploadFile(request):
    return render(request, 'upload_file.html')

