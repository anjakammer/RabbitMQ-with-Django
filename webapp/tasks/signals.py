import asyncio
from threading import Thread
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save
from .OcrRequester import OcrRequester
from .models import Task

def start_worker(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

@receiver(OcrRequester.ocr_progressing, sender=OcrRequester)
def ocr_request_received(sender, **kwargs):
    id = kwargs.get('id')
    task = Task.objects.get(pk=id)
    task.status = Task.STATUS_PROGRESSING
    task.save()

@receiver(OcrRequester.ocr_finished, sender=OcrRequester)
def write_result(sender, **kwargs):
    response_object = kwargs.get('response')
    id = response_object.get('id')
    result = response_object.get('result')

    task = Task.objects.get(pk=id)
    task.result = result
    task.status = Task.STATUS_DONE
    task.resolved_at = now()
    task.save()

@receiver(post_save, sender=Task)
def request_ocr(sender, **kwargs):
    task = kwargs.get('instance')

    if task.status == Task.STATUS_REQUESTED:
        ocr_requester = OcrRequester()

        request = {
            "id": task.id,
            "image_url": task.resource
        }

        worker_loop.call_soon_threadsafe(ocr_requester.send, request, task.id)

worker_loop = asyncio.new_event_loop()
worker = Thread(target=start_worker, args=(worker_loop,))
worker.start()

