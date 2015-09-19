# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('credit', models.IntegerField()),
                ('course', models.CharField(max_length=10)),
                ('semester', models.CharField(max_length=10)),
                ('department', models.ForeignKey(to='repository.Department')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=25)),
                ('password', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=20)),
                ('department', models.ForeignKey(to='repository.Department')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
