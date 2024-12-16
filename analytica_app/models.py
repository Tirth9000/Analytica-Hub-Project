from django.db import models
from mongoengine import *

# Create your models here.
class AnalysisFile(models.Model):
    file_id = models.CharField(primary_key=True, max_length=6)
    file = models.FileField(upload_to="analysis_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_id


# class User(Document):
#     file_id = StringField(primary_key=True, max_length=6)
#     file = FileField()
#     uploaded_at = DateTimeField(auto_now_add=True)
#     updated_at = DateTimeField(auto_now=True)

#     name = StringField(required=True, max_length=50)
#     email = EmailField(required=True, unique=True)
#     age = IntField(min_value=0)

#     def __str__(self):
#         return self.name