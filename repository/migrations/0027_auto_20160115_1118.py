# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-15 11:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0026_auto_20160115_1029'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='mark',
            new_name='part',
        ),
    ]
