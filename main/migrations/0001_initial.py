# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=16)),
                ('created_dt', models.DateTimeField(auto_now_add=True)),
                ('expire_dt', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=15)),
                ('ua', models.TextField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('visits', models.IntegerField(default=0)),
                ('access_code', models.ForeignKey(to='main.AccessCode')),
            ],
        ),
    ]
