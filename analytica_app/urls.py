from django.urls import path
from .views import *

urlpatterns = [
    path('', LandingPage, name='landing_page'),

    path('upload-file/', UploadFile, name='upload_file'),
    path('upload-file/<str:id>/delete', DeleteFile, name='delete_file'),
    path('analytic-page/<str:id>', AnalyticPage, name='analytic_page'),
    path('analytic-page/<str:id>/rename-file', RenameFile, name='rename_file'),
    path('analytic-page/<str:id>/details/<str:colName>', Details, name='details'),
    path('analytic-page/<str:id>/datails/<str:colName>/drop-column', DropColumn, name="drop_column"),
    path('analytic-page/<str:id>/detials/<str:colName>/drop-nan', DropNaN, name='dropna'),
    path('analytic-page/<str:id>/detials/<str:colName>/fill-nan/<str:method>', FillNaN, name='fillna'),

    # path('analytic-page/<str:id>/python-codespace', PythonCodeSpace, name='codespace'),
    path('analytic-page/<str:id>/live-chat', ChatWithCSV, name='chatwithCSV'),
    path('analytic-page/<str:id>/auto-clean', AutoCleaning, name='autoclean'),

    path('analytic-page/<str:id>/undo', undo_action, name="undoAction"),
    path('analytic-page/<str:id>/redo', redo_action, name="redoAction"),

    path('analytic-page/<str:id>/save', save_changes, name="save"),
    path('analytic-page/<str:id>/export', Export, name="export_data"),
]