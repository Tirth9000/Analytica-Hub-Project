from django.shortcuts import render, redirect
from templates import *

# Create your views here.
def LandingPage(request):
    return render(request, 'landing1.html')
