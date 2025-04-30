from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from auth_app.models import *

class CustomUserBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(email=email)
            if user and check_password(password, user.password):
                return user
        except UserModel.DoesNotExist:
            return None
    
    def get_user(self, email):
        try:
            return UserModel.objects.get(pk=email)
        except UserModel.DoesNotExist:
            return None