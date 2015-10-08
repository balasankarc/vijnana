# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0020_auto_20151008_0609'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='category',
        ),
    ]
