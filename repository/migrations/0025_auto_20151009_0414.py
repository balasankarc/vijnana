# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import repository.models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0024_auto_20151008_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(upload_to=repository.models.set_profilepicturename, blank=True),
            preserve_default=True,
        ),
    ]
