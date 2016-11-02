from __future__ import unicode_literals
from django.utils.text import slugify

from django.db import models


# Create your models here.
class Section(models.Model):
	name = models.CharField(max_length=20, unique=True, null=False)
	slug = models.SlugField(max_length=20, unique=True, null=False)
	spanish_title = models.CharField(max_length=100, null=False)
	spanish_body = models.TextField(null=True)
	english_title = models.CharField(max_length=100, null=False)
	english_body = models.TextField(null=True)

	def save(self, *args, **kwargs):
		if not self.id:
			if not self.slug:
				self.slug = slugify(self.name)
			if not self.english_title:
				self.english_title = self.spanish_title
			if not self.english_body:
				self.english_body = self.spanish_body

		super(Section, self).save(*args, **kwargs)
