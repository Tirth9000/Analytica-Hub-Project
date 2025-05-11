from celery import shared_task
import pandas as pd


@shared_task
def ConvertDataframe(file_path):
    df = pd.read_csv(file_path)
    return df

@shared_task
def currentNodetoDf(rows, columns):
    df = pd.DataFrame(rows, columns=columns)
    return df