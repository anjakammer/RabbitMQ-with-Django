from django.core.files.storage import default_storage
from django.conf import settings
from django.dispatch import Signal
from rest_framework import status, generics
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer, TaskSerializerGet
import ipfsapi, os

class TaskListView(generics.ListCreateAPIView):

    TMP_FILE_PATH = 'tmp/tmp_file'
    IPFS_HOST = '127.0.0.1'
    IPFS_API_PORT = 5001

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
        is_valid = serializer.is_valid()
        task_type = serializer.initial_data.get(Task.KEY_TYPE)

        if is_valid and (task_type == Task.TYPE_OCR):
            task = serializer.save()
            response =  Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            error_message = {}
            if task_type == None or task_type == 'None':
                error_message = {Task.KEY_TYPE: ['Please choose a valid request type']}

            return Response([serializer.errors, error_message], status=status.HTTP_400_BAD_REQUEST)

        self.__process_by_type(request, task.id, task.type)

        return response

    def __request_ocr_from_resource(self, task_id, resource_stream):
        file_hash = self.__get_file_hash_from_stream(resource_stream)

        self.__update_task_resource(task_id, file_hash)
        self.request_ocr.send(sender=self.__class__, id=task_id, file_hash=file_hash)


    def __get_file_hash_from_stream(self, data):
        with default_storage.open(self.TMP_FILE_PATH, 'wb+') as destination:
            for chunk in data.chunks():
                destination.write(chunk)
        tmp_file = os.path.join(settings.MEDIA_ROOT, self.TMP_FILE_PATH)

        file_storage = ipfsapi.connect(self.IPFS_HOST, self.IPFS_API_PORT)
        res = file_storage.add(tmp_file)
        os.remove(tmp_file)

        return res.get('Hash')

    def __update_task_resource(self, id, file_hash):
        task = Task.objects.get(id=id)
        task.resource = file_hash
        task.save()

    def __process_by_type(self, request, task_id, task_type):
        if task_type == Task.TYPE_OCR:
            data = request.FILES.get(Task.KEY_RESOURCE)
            self.__request_ocr_from_resource(task_id, data)
