# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0014_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.EmailField(default='test@test.com', max_length=75),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='phone',
            field=models.CharField(default=111, max_length=15),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(default=b'student', max_length=20),
            preserve_default=True,
        ),
    ]
