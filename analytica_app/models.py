from django.db import models

# Create your models here.
class AnalysisFile(models.Model):
    file_id = models.CharField(primary_key=True, max_length=6)
    file = models.FileField(upload_to="analysis_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_id
