# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0003_department_abbreviation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=50)),
                ('resourcefile', models.FileField(upload_to=b'resources')),
                ('subject', models.ForeignKey(to='repository.Subject')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
