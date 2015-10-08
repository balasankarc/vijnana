# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import repository.models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0022_question_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='questionpaper',
            field=models.FileField(upload_to=repository.models.set_questionpapername, blank=True),
            preserve_default=True,
        ),
    ]
