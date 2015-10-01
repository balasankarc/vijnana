# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import repository.models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0013_auto_20150926_1520'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.TextField()),
                ('picture', models.ImageField(upload_to=repository.models.set_profilepicturename)),
                ('bloodgroup', models.CharField(max_length=5)),
                ('user', models.OneToOneField(to='repository.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
