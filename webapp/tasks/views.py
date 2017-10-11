from .models import Task
from .serializers import TaskSerializer, TaskSerializerGet
from rest_framework import generics
from django.core.files.storage import default_storage
from django.conf import settings
import ipfsapi, os
from rest_framework import status
from rest_framework.response import Response
from django.dispatch import Signal

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
        response = None
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = request.FILES.get('resource')

        api = ipfsapi.connect('127.0.0.1', 5001)

        with default_storage.open('tmp/tmp.png', 'wb+') as destination:
            for chunk in data.chunks():
                destination.write(chunk)


        tmp_file = os.path.join(settings.MEDIA_ROOT, 'tmp/tmp.png')
        res = api.add(tmp_file)
        os.remove(tmp_file)

        task_id = serializer.data.get('id')
        file_hash = res.get('Hash')
        self.request_ocr.send(sender=self.__class__, id=task_id, file_hash=file_hash)
        task = Task.objects.get(id=task_id)
        task.resource = file_hash
        task.save()

        return response
