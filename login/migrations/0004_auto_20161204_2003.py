# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-04 23:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_auto_20161204_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='login.Area'),
        ),
    ]
