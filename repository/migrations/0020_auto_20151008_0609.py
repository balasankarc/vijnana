# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0019_auto_20151006_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='subject',
            field=models.ForeignKey(default=1, to='repository.Subject'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exam',
            name='time',
            field=models.CharField(default=datetime.datetime(2015, 10, 8, 6, 9, 38, 389396, tzinfo=utc), max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exam',
            name='totalmarks',
            field=models.CharField(default=10, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='mark',
            field=models.CharField(default=10, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='question',
            name='exam',
            field=models.ManyToManyField(to='repository.Exam'),
            preserve_default=True,
        ),
    ]
