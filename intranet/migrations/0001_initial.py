# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-22 07:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(max_length=500, upload_to='uploads/documents/')),
                ('title', models.CharField(max_length=300, null=True)),
                ('title_slug', models.SlugField(max_length=300, null=True)),
                ('author', models.CharField(max_length=300, null=True)),
                ('author_slug', models.SlugField(max_length=300, null=True)),
                ('date', models.DateField(null=True)),
                ('content', models.TextField(null=True)),
                ('abstract', models.CharField(max_length=1000, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('drive_id', models.CharField(max_length=100, null=True)),
                ('thumbnail', models.FileField(max_length=500, upload_to='static/thumbnails/')),
                ('words', models.CharField(max_length=200, null=True)),
                ('issn', models.CharField(max_length=20, null=True)),
                ('doi', models.CharField(max_length=50, null=True)),
                ('pages', models.CharField(max_length=25, null=True)),
                ('is_available', models.BooleanField(default=False)),
                ('first_save_flag', models.BooleanField(default=False)),
                ('is_public', models.BooleanField(default=False)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='login.SubArea')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('slug', models.SlugField(max_length=300)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('type', models.CharField(max_length=50)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ForumComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType')),
                ('forum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='intranet.Forum')),
            ],
        ),
    ]
