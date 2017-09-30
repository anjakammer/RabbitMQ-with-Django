from django.apps import AppConfig
from .OcrWorker import OcrWorker

class WorkerConfig(AppConfig):
    name = 'worker'

    def ready(self):
        OcrWorker()