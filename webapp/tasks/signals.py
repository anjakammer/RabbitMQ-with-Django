import asyncio
from threading import Thread
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save
from .TaskProcessingService import TaskProcessingService
from .models import Task
from .views import TaskListView

def start_worker(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

@receiver(TaskProcessingService.task_processing, sender=TaskProcessingService)
def task_request_received(sender, **kwargs):
    id = kwargs.get('id')
    task = Task.objects.get(pk=id)
    task.status = Task.STATUS_PENDING
    task.save()

@receiver(TaskProcessingService.task_finished, sender=TaskProcessingService)
def write_result(sender, **kwargs):
    response_object = kwargs.get('response')
    id = response_object.get('id')
    result = response_object.get('result')

    task = Task.objects.get(pk=id)
    task.result = result
    task.status = Task.STATUS_DONE
    task.resolved_at = now()
    task.save()

@receiver(TaskListView.request_processing, sender=TaskListView)
def request_processing(sender, **kwargs):
    task_id = kwargs.get(Task.KEY_ID)
    task_type = kwargs.get(Task.KEY_TYPE)
    file_hash = kwargs.get('file_hash')

    task_processor = TaskProcessingService()

    request = {
        "id": task_id,
        "file_hash": file_hash
    }

    worker_loop.call_soon_threadsafe(task_processor.send, request, task_id, task_type)

worker_loop = asyncio.new_event_loop()
worker = Thread(target=start_worker, args=(worker_loop,))
worker.start()

