# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0017_question'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.CharField(unique=True, max_length=5000),
            preserve_default=True,
        ),
    ]
