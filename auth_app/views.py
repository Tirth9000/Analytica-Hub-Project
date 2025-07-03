from django.shortcuts import render
from templates import *

# Create your views here.
def Login(request):
    return render(request, 'login.html')

def Signup(request):
    return render(request, 'signup.html')
    