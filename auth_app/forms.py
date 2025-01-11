from django import forms
from auth_app.models import *

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class RegisterForm(forms.ModelForm):
    class Meta: 
        model = UserAuth
        fields = '__all__'

class VerifyEmail(forms.Form):
    email = forms.EmailField(
        max_length=200, 
        #  required=True,
        required=False,
        label = '',
        widget=forms.EmailInput(attrs={'id': 'email', 'placeholder': 'Enter your email'})
                             
    )

class VerifyOTP(forms.Form):
    otp = forms.IntegerField(
         #  required=True,
        required=False,
        label = '',
        widget=forms.TextInput(attrs={'id': 'otp', 'placeholder': 'Enter 6-digit OTP'})
    )
