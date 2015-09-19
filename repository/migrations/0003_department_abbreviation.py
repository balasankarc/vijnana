# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0002_auto_20150919_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='abbreviation',
            field=models.CharField(default='Null', max_length=10),
            preserve_default=False,
        ),
    ]
