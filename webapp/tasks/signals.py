import asyncio
from threading import Thread
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save
from .OcrRequester import OcrRequester
from .models import Task

def start_worker(loop):
    """Switch to new event loop and run forever"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

@receiver(OcrRequester.ocr_finished, sender=OcrRequester)
def write_result(sender, **kwargs):
    id = kwargs.get('id')
    result = kwargs.get('result')
    print('for task id:', id)
    print(" [.] Got", result)
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

        ocr_request = {
            "id": task.id,
            "image_url": task.resource
        }

        worker_loop.call_soon_threadsafe(ocr_requester.send, ocr_request)

# Create the new loop and worker thread
worker_loop = asyncio.new_event_loop()
worker = Thread(target=start_worker, args=(worker_loop,))
# Start the thread
worker.start()

