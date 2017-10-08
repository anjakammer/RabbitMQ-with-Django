from django.db import models

class Task(models.Model):
    STATUS_REQUESTED = 'requested'
    STATUS_PROGRESSING = 'progressing'
    STATUS_DONE = 'done'
    STATUS = (
        (STATUS_REQUESTED, 'Requested'),
        (STATUS_PROGRESSING, 'Progressing'),
        (STATUS_DONE, 'Done'),
    )

    status = models.CharField(max_length=32, choices=STATUS, default=STATUS_REQUESTED)
    type = models.CharField(max_length=100, default='ocr')
    resource = models.CharField(max_length=250)
    result = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
