from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser
)
import json, os
from django.utils import timezone

# Create your models here.


class UserManager(BaseUserManager):
	def create_user(self, email, first_name, last_name, institution, country, area, career, password=None):
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
			area=area,
			career=career,
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
			area=area,
			career=career,
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
	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	institution = models.CharField(max_length=50)
	country = models.CharField(max_length=20)
	area = models.ForeignKey(Area, on_delete=models.CASCADE)
	career = models.CharField(max_length=40)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	last_activity = models.DateField(auto_now=True)
	profile_picture = models.FileField(upload_to='static/profile_pictures/', max_length=500, null=True)
	doc_count = models.IntegerField(default=0)


	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name', 'institution', 'country', 'area', 'career']

	def update_activity(self):
		self.last_activity = timezone.now()
		self.save()
		return self

	def doc_number(self, operator):
		if operator == '+':
			self.doc_count =self.doc_count + 1
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

