# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-11-14 03:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=80, null=True)),
                ('last_name', models.CharField(max_length=80, null=True)),
                ('institution', models.CharField(max_length=80, null=True)),
                ('country', models.CharField(max_length=80, null=True)),
                ('career', models.CharField(max_length=80, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('profile_picture', models.FileField(max_length=500, null=True, upload_to='static/profile_pictures/')),
                ('doc_count', models.IntegerField(default=0)),
                ('drive_credentials', models.BinaryField(null=True)),
                ('drive_email', models.CharField(max_length=100, null=True)),
                ('access_token', models.CharField(max_length=128, null=True)),
                ('is_registered', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='login.Area'),
        ),
    ]
