# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0007_auto_20150924_0737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='staff',
            field=models.ManyToManyField(related_name='teachingsubjects', to='repository.User'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='subject',
            name='students',
            field=models.ManyToManyField(related_name='subscribedsubjects', to='repository.User'),
            preserve_default=True,
        ),
    ]
