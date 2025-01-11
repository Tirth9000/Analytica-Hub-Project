from django.shortcuts import render, redirect
from .forms import *


def user_logout(request_function):
    def inner_function(request, *args, **kwargs):
        if request.session.get('auth_token') == 'logout':
            return redirect('login')
        return request_function(request, *args, **kwargs)
    return inner_function

def user_login(view_function):
    def inner_function(request, *args, **kwargs):
        if request.session.get('auth_token') == 'login':
            return redirect('home')
        return view_function(request, *args, **kwargs)
    return inner_function 

    