# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-08 16:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_auto_20171008_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='resource',
            field=models.CharField(default='ocr', max_length=250),
        ),
    ]
