# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0021_remove_question_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='subject',
            field=models.ForeignKey(default=1, to='repository.Subject'),
            preserve_default=False,
        ),
    ]
