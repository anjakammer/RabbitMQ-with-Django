from .models import Task
from .serializers import TaskSerializer
from rest_framework import generics

class TaskListView(generics.ListCreateAPIView):

    model = Task
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
