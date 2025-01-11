from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail 
import random
import threading
from .middlewares import *
from templates import *
from .forms import *
from .models import *
from .tasks import *


# Create your views here.
def UserRegister(request):
    if request.method == 'POST':
        if UserAuth.objects.filter(email=request.POST.get('email')):
            return render(request, 'register.html', {'alert' : True})
        else:
            userpassword = request.POST.get('password')
            if CheckPassword(userpassword):
                return render(request, 'register.html', {'error': True}) 
            else:
                newuser = UserAuth.objects.create(
                    email = request.POST.get('email'),
                    name = request.POST.get('name'),
                    message = request.POST.get('message')
                )
                newuser.password = set_password(userpassword)
                ConfirmationMail.delay(newuser.name, newuser.email)     # Celery applied
                newuser.save()
                return redirect('login')
    else:
        success_message = False
        error_message = False
        return render(request, 'register.html', {'success':success_message, 'error': error_message})


@user_login
@never_cache
def UserLogin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                request.session['auth_token'] = 'login'
                request.session['user'] = user.email
                return redirect('home')
            else:
                request.session['auth_token'] = None
                return render(request, 'login.html', {'alert': True, 'form': form})
        else:
            return render(request, 'login.html', {'from': form})
    else:
        form = LoginForm()
        return render(request, 'login.html', {'alert': False, 'form': form})


@user_logout
@never_cache
def UserHome(request):
    useremail = request.session.get('user')
    user = UserAuth.objects.filter(email = useremail)
    return render(request, 'home.html', {'user': user[0]})


@never_cache
def ForgetPassword(request):
    if request.method == 'POST':
        if 'email' in request.POST:
            email = request.POST.get('email')
            user = UserAuth.objects.filter(email=email)

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
            get_user = UserAuth.objects.get(email=request.session.get('user_email'))
            get_user.password = set_password(password)
            get_user.save()
            request.session.pop('user_email', None)
            return redirect('login')
    return render(request, 'reset.html')


def ResendOTP(request):
    email = request.session.get('user_email')
    user = UserAuth.objects.get(email = email)
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