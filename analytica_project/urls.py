"""
URL configuration for analytica_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from analytica_app.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPage, name='landing_page'),
    path('upload-file/', UploadFile, name='upload_file'),
    path('analytic-page/<str:id>', AnalyticPage, name='analytic_page'),
    path('analytic-page/<str:id>/rename-file', RenameFile, name='rename_file'),
    path('analytic-page/<str:id>/details/<str:colName>', Details, name='details'),
    path('analytic-page/<str:id>/detials/<str:colName>/drop-nan', DropNaN, name='dropna'),
    path('analytic-page/<str:id>/detials/<str:colName>/fill-nan/<str:method>', FillNaN, name='fillna'),

    path('analytic-page/<str:id>/python-codespace', PythonCodeSpace, name='codespace'),
    path('analytic-page/<str:id>/live-chat', ChatWithCSV, name='chatwithCSV'),
    path('analytic-page/<str:id>/auto-clean', AutoCleaning, name='autoclean'),

    path('analytic-page/<str:id>/undo', undo_action, name="undoAction"),
    path('analytic-page/<str:id>/redo', redo_action, name="redoAction"),

    path('analytic-page/<str:id>/save', save_changes, name="save"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
