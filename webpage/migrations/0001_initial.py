# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-11-14 03:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('slug', models.SlugField(max_length=20, unique=True)),
                ('spanish_title', models.CharField(max_length=200)),
                ('spanish_body', models.TextField(null=True)),
                ('english_title', models.CharField(max_length=200)),
                ('english_body', models.TextField(null=True)),
            ],
        ),
    ]
