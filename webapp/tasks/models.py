from django.db import models

class Task(models.Model):
    STATUS = (
        ('0', 'Requested'),
        ('1', 'Progressing'),
        ('2', 'Done'),
    )
    status = models.CharField(max_length=1, choices=STATUS)
    type = models.CharField(max_length=100)
    resource = models.URLField()
    result = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)