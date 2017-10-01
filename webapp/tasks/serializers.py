from rest_framework import serializers
from tasks.models import Task


class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    resolved_at = serializers.DateTimeField(read_only=True)
    result = serializers.CharField(read_only=True)
    resource = serializers.URLField(required=True)

    def create(self, validated_data):
        return Task.objects.create(**validated_data)
