from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail 
import random
import threading
from .middlewares import *
from templates import *
from .models import *
from .tasks import *


# Create your views here.
def UserRegister(request):
    if request.method == "POST":
        email = request.POST.get('email')
        found_email = UserModel.objects.filter(email = email)
        if found_email:
            return HttpResponse()
        
        SendOTP(otp, email)
    return render(request, 'signup.html')


# @user_login
# @never_cache
def UserLogin(request):
    return render(request, 'login.html')


# @user_logout
# @never_cache
def UserHome(request):
    useremail = request.session.get('user')
    user = UserModel.objects.filter(email = useremail)
    return render(request, 'home.html', {'user': user[0]})


@never_cache
def ForgetPassword(request):
    if request.method == 'POST':
        if 'email' in request.POST:
            email = request.POST.get('email')
            user = UserModel.objects.filter(email=email)

            if user:
                request.session['user_email'] = email
                global otp
                otp = random.randint(100000, 999999)
                OTPMail.delay(otp, user[0].name, user[0].email)          # Celery applied
                change_otp_timer = threading.Timer(40.0, ChangeOTP)
                change_otp_timer.start()
                return render(request, 'forget.html', {'alert': 'valid', 'otp_send': True, 'email': email})

            else:
                return render(request, 'forget.html', {'alert': 'invalid', 'email': email})

        elif 'otp' in request.POST:
            get_otp = int(request.POST.get('otp'))
            print("forget",otp)
            try:
                if otp == get_otp:
                    return redirect('reset_password')
                else:
                    return render(request, 'forget.html', {'invalid_otp': True})

            except NameError:
                return render(request, 'forget.html', {'invalid_otp': True})
              
    return render(request, 'forget.html')



def ResetPassword(request):
    if request.method == "POST":
        password = request.POST.get('new-password')
        confirmPassword = request.POST.get('confirm-password')
        if CheckPassword(password):
            return render(request, 'reset.html', {'invalid_password': True})

        elif password != confirmPassword:
            return render(request, 'reset.html', {'confirm_password': True})

        else:
            get_user = UserModel.objects.get(email=request.session.get('user_email'))
            get_user.password = set_password(password)
            get_user.save()
            request.session.pop('user_email', None)
            return redirect('login')
    return render(request, 'reset.html')


def ResendOTP(request):
    email = request.session.get('user_email')
    user = UserModel.objects.get(email = email)
    global otp
    otp = random.randint(100000, 999999)
    OTPMail.delay(otp, user.name, user.email)       # Celery applied
    change_otp_timer = threading.Timer(40.0, ChangeOTP)
    change_otp_timer.start()
    return render(request, 'forget.html', {'alert': 'valid', 'otp_send': True, 'email': email})


def UserSignout(request):
    request.session['auth_token'] = 'logout'
    request.session.pop('user', None)
    return redirect('login')




def ChangeOTP():
    global otp
    otp = 0

def error_404_view(request, exception):
    return render(request, '404.html')