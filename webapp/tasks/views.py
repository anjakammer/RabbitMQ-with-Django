from .models import Task
from .serializers import TaskSerializer, TaskSerializerGet
from rest_framework import generics
from django.core.files.storage import default_storage


class TaskListView(generics.ListCreateAPIView):

    model = Task
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskSerializerGet
        return TaskSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)

        data = request.FILES.get('resource')

        with default_storage.open('tmp/test_1.png', 'wb+') as destination:
            for chunk in data.chunks():
                destination.write(chunk)

        return response
