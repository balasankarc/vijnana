# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0012_auto_20150926_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='credit',
            field=models.CharField(max_length=5),
            preserve_default=True,
        ),
    ]
