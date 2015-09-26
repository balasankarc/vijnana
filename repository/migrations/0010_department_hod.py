# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0009_subject_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='hod',
            field=models.OneToOneField(related_name='department_hod', default=1, to='repository.User'),
            preserve_default=False,
        ),
    ]
