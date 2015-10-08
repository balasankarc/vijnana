# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import repository.models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0023_exam_questionpaper'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='questionpaper',
            field=models.FileField(upload_to=repository.models.set_questionpapername),
            preserve_default=True,
        ),
    ]
