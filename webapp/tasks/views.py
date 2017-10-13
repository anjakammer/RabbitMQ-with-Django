from django.core.files.storage import default_storage
from django.conf import settings
from django.dispatch import Signal
from rest_framework import status, generics
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer, TaskSerializerGet
import ipfsapi, os

class TaskListView(generics.ListCreateAPIView):

    model = Task
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    request_ocr = Signal(providing_args=["id", "file_hash"])

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskSerializerGet
        return TaskSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task_id = serializer.data.get('id')
        data = request.FILES.get('resource')
        self.__request_ocr_from_resource(task_id, data)

        return response

    def __request_ocr_from_resource(self, task_id, resource_stream):
        file_hash = self.__get_file_hash_from_stream(resource_stream)

        self.__update_task_resource(task_id, file_hash)
        self.request_ocr.send(sender=self.__class__, id=task_id, file_hash=file_hash)


    def __get_file_hash_from_stream(self, data):
        with default_storage.open('tmp/tmp.png', 'wb+') as destination:
            for chunk in data.chunks():
                destination.write(chunk)

        tmp_file = os.path.join(settings.MEDIA_ROOT, 'tmp/tmp.png')
        api = ipfsapi.connect('127.0.0.1', 5001)
        res = api.add(tmp_file)
        os.remove(tmp_file)

        return res.get('Hash')

    def __update_task_resource(self, id, file_hash):
        task = Task.objects.get(id=id)
        task.resource = file_hash
        task.save()

