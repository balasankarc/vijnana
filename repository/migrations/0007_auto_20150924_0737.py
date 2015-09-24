# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0006_resource_uploader'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='staff',
            field=models.ManyToManyField(related_name='staff', to='repository.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subject',
            name='students',
            field=models.ManyToManyField(related_name='students', to='repository.User'),
            preserve_default=True,
        ),
    ]
