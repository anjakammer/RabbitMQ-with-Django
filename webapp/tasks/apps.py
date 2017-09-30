from django.apps import AppConfig
from .OcrClient import OcrClient


class TasksConfig(AppConfig):
    name = 'tasks'

    def ready(self):
        ocr_client = OcrClient()
        ocr_client.connect()