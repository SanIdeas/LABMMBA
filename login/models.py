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
    def create_user(self, email, first_name=None, last_name=None, institution=None, country=None, area=None, career=None, password=None, is_active=False, is_admin=False):
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
            is_admin = is_admin,
            area=area,
            career=career,
            is_active=is_active,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,password = None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
            is_admin=True,
            is_active=True,
        )
        user.save(using=self._db)
        return user

class Area(models.Model):
    name = models.CharField(max_length=100)

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=20, null=True)
    institution = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=20, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    career = models.CharField(max_length=40, null=True)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    last_activity = models.DateField(auto_now=True)
    profile_picture = models.FileField(upload_to='static/profile_pictures/', max_length=500, null=True)
    doc_count = models.IntegerField(default=0)
    drive_credentials = models.BinaryField(null=True)
    access_token = models.CharField(max_length=128, null=True)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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

