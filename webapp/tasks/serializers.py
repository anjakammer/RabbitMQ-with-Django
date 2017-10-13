from collections import OrderedDict
from rest_framework import serializers
from tasks.models import Task

class TaskSerializerGet(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    resolved_at = serializers.DateTimeField(read_only=True)
    result = serializers.CharField(read_only=True)
    resource = serializers.CharField(read_only=True)

class TaskSerializer(serializers.Serializer):
    type = serializers.ChoiceField(Task.TYPE_OCR)

    resource = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)

    def create(self, validated_data):
        validated_data['resource'] = str(validated_data['resource'])
        return Task.objects.create(**validated_data)

    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except:
                continue
            if field.field_name == 'resource':
                resource = self.fields['resource']
                ret[field.field_name] = resource.get_attribute(instance)
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret