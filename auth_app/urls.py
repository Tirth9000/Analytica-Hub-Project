from django.urls import path
from .views import *

urlpatterns = [
    path('analytica-hub/login', Login, name="login"),
    path('analytica-hub/signup', Signup, name="signup"),
]