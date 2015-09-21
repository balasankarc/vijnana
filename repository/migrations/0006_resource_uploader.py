# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0005_auto_20150921_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='uploader',
            field=models.ForeignKey(default=1, to='repository.User'),
            preserve_default=False,
        ),
    ]
