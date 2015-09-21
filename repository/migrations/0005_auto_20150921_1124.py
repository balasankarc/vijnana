# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import repository.models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0004_resource'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='resourcefile',
            field=models.FileField(upload_to=repository.models.set_filename),
            preserve_default=True,
        ),
    ]
