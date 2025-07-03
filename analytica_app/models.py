from django.db import models

# Create your models here.
class AnalyticaFiles(models.Model):
    # user = models.ForeignKey('user', ondelete=models.CASCADE, null=True, blank=True)
    file_id = models.CharField(
        primary_key=True, 
        null=False, 
        blank=False, 
        max_length=6
        )
    file_name = models.CharField(max_length=40, default="New Document")
    file_path = models.FileField(upload_to="analysis_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "AnalyticaFiles"

    def __str__(self):
        return self.file_id
