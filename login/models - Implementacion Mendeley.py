from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser
)
import json

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
	institution = models.CharField(max_length=20)
	country = models.CharField(max_length=20)
	area = models.ForeignKey(Area, on_delete=models.CASCADE)
	career = models.CharField(max_length=40)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name', 'institution', 'country', 'area', 'career']

class Mendeley_credentials(models.Model):
	state = models.CharField(max_length=100)
	token_type = models.CharField(max_length=50) 
	refresh_token = models.CharField(max_length=400)
	msso = models.CharField(max_length=400)
	access_token = models.CharField(max_length=400)
	scope = models.CharField(max_length=10)
	expires_in = models.IntegerField()
	expires_at = models.DecimalField(max_digits=15, decimal_places=4)

	def get_token(self):
		token = {}
		for field in self._meta.fields:
			if field.name == 'scope':
				scope_list = []
				scope_list.append(getattr(self, field.name))
				token[field.name] = scope_list
			else:
				token[field.name] = getattr(self, field.name)
		return token