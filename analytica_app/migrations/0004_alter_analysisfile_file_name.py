# Generated by Django 5.1.4 on 2025-01-02 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytica_app', '0003_analysisfile_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysisfile',
            name='file_name',
            field=models.CharField(default='New Document', max_length=40),
        ),
    ]