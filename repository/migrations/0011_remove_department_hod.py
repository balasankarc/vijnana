# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0010_department_hod'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='hod',
        ),
    ]
