# Copyright (C) 2010 Google Inc. 
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#      http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.  
# OAuth 2.0 utilities for Django. 
# Utilities for using OAuth 2.0 in conjunction with the Django datastore. 

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import json, os
from django.utils import timezone
import oauth2client, base64, cPickle, re

# Create your models here.

class CredentialsField(models.Field): 
    
    def __init__(self, *args, **kwargs): 
        if 'null' not in kwargs: 
            kwargs['null'] = True 
        super(CredentialsField, self).__init__(*args, **kwargs) 
    
    def get_internal_type(self): 
        return "TextField" 
 
    def to_python(self, value): 
        if value is None: 
            return None 
        if isinstance(value, oauth2client.client.Credentials): 
            return value 
        return cPickle.loads(base64.b64decode(value)) 
    def get_db_prep_value(self, value, connection, prepared=False): 
        if value is None: 
            return None 
        return base64.b64encode(cPickle.dumps(value)) 

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, institution, country, area, career, password=None, is_active=True, is_admin=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            institution=institution,
            country=country,
            is_admin = is_admin if is_admin else False,
            area=area,
            career=career,
            is_active=False,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, institution, country, area, career, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            institution=institution,
            country=country,
            area=None,
            is_admin=True,
            career=career,
            is_active=True,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Area(models.Model):
    name = models.CharField(max_length=30)

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    drive_credentials = CredentialsField(null=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    institution = models.CharField(max_length=50)
    country = models.CharField(max_length=20)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    career = models.CharField(max_length=40)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    last_activity = models.DateField(auto_now=True)
    profile_picture = models.FileField(upload_to='static/profile_pictures/', max_length=500, null=True)
    doc_count = models.IntegerField(default=0)
    drive_credentials = models.BinaryField(null=True)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'institution', 'country', 'area', 'career']

    def update_activity(self):
        self.last_activity = timezone.localtime(timezone.now())
        self.save()
        return self

    def doc_number(self, operator):
        current = self.doc_count + 1
        if operator == '+':
            self.doc_count = current
        else:
            self.doc_count =self.doc_count - 1
        self.save()
        return self

    def update_picture(self, picture):
        self.profile_picture = picture
        self.save()
        return True

    def filename(self):
        return 'profile_pictures/' + os.path.basename(self.profile_picture.name)

    def credentials(self):
        return cPickle.loads(base64.b64decode(self.drive_credentials))

    def simplify_institution(self):
        count = len(re.findall(r'\w+', self.institution))
        if count <= 2:
            return self.institution
        else:
            output = ''
            for i in self.institution.upper().split():
                output += i[0]
            return output

