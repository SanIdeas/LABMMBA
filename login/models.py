from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser
)
import json, os
from django.utils import timezone
from django.conf import settings
import oauth2client, base64, cPickle, re

# Create your models here.


class UserManager(BaseUserManager):
	def precreate_user(self, email, access_token,):
		if not email:
			raise ValueError('Users must have an email address')

		user = self.model(
			email=self.normalize_email(email),
			access_token=access_token
		)
		user.save(using=self._db)
		return user

	def create_user(self, email, first_name=None, last_name=None, institution=None, country=None, area=None, career=None, password=None, is_admin=False):
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
		)
		user.save(using=self._db)
		return user

class Area(models.Model):
	name = models.CharField(max_length=150, unique=True)

	def get_sub_areas(self):
		return SubArea.objects.filter(area=self)
	def add_sub_area(self, name):
		return SubArea.objects.create(name=name, area=self)

class SubArea(models.Model):
	name  = models.CharField(max_length=150, unique=True)
	area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)

class User(AbstractBaseUser):
	email = models.EmailField(
		verbose_name='email address',
		max_length=255,
		unique=True,
	)
	first_name = models.CharField(max_length=80, null=True)
	last_name = models.CharField(max_length=80, null=True)
	institution = models.CharField(max_length=80, null=True)
	country = models.CharField(max_length=80, null=True)
	area = models.ForeignKey(SubArea, on_delete=models.SET_NULL, null=True)
	career = models.CharField(max_length=80, null=True)
	is_active = models.BooleanField(default=True)
	is_blocked = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	last_activity = models.DateTimeField(auto_now=True)
	profile_picture = models.FileField(upload_to='static/profile_pictures/', max_length=500, null=True)
	doc_count = models.IntegerField(default=0)
	drive_credentials = models.BinaryField(null=True)
	drive_email = models.CharField(max_length=100, null=True)
	access_token = models.CharField(max_length=128, null=True)
	is_registered = models.BooleanField(default=False)
	facebook = models.CharField(max_length=100, null=True)
	twitter = models.CharField(max_length=100, null=True)
	linkedin = models.CharField(max_length=100, null=True)


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
		# Si existe una foto, se elimina
		if self.profile_picture:
			os.remove(self.profile_picture.path)
			self.save()

		self.profile_picture.save('U' + str(self.id) + '.jpg', picture)
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

	def complete_registration(self, first_name=None, last_name=None, institution=None, country=None, area=None, career=None, password=None):
		if not first_name and not last_name and not institution and not country and not area and not career and not password:
			return False
		self.first_name = first_name
		self.last_name = last_name
		self.institution = institution
		self.country = country
		self.area = SubArea.objects.get(id=area)
		self.career = career
		self.set_password(password)
		self.is_registered = True
		self.is_active = True
		self.save()
		return True

