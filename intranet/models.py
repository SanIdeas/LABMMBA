from __future__ import unicode_literals

from django.db import models
from login.models import User, Area
from unidecode import unidecode
from django.conf import settings
from collections import Counter
import os, re, operator

# Create your models here.

class Document(models.Model):
	document = models.FileField(upload_to='uploads/documents/', max_length=500)
	category = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
	type = models.BooleanField()
	title = models.CharField(max_length=100, null=True)
	author = models.CharField(max_length=100, null=True)
	date = models.DateField(null=True)
	abstract = models.CharField(max_length=400, null=True)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	date_added = models.DateField(auto_now_add=True)
	drive_id = models.CharField(max_length=100, null=True)
	thumbnail = models.FileField(upload_to='static/thumbnails/', max_length=500)
	words = models.CharField(max_length=200, null=True)

	#Retorna el nombre del archivo pdf.
	def filename(self):
		return os.path.basename(self.document.name)
	def thumbnail_filename(self):
		return 'thumbnails/' + os.path.basename(self.thumbnail.name)

	#http://stackoverflow.com/questions/12358920/renaming-files-in-django-filefield
	def format_filename(self):
		new_filename='uploads/documents/' + 'U' + str(self.owner.id) + 'I' + str(self.id) + '.pdf'
		os.rename(self.document.path, (settings.MEDIA_ROOT + '/' + new_filename).replace('/', '\\'))
		self.document.name = new_filename
		self.save()
		return self.document.name

	def format_thumbnail_filename(self):
		new_filename='static/thumbnails/' + 'U' + str(self.owner.id) + 'I' + str(self.id) + '.jpg'
		os.rename(self.thumbnail.path, (settings.MEDIA_ROOT + '/' + new_filename).replace('/', '\\'))
		self.thumbnail.name = new_filename
		self.save()
		return self.thumbnail.name


	#Retorna el nombre completo del duenno.
	def owner_name(self):
		return self.owner.first_name + ' ' + self.owner.last_name

	
	#Dado una lista de palabras(words). Si todas coinciden con al menos un campo de la fila, retorna True.
	def match(self, words):
		for field in self._meta.fields:
			if (type(field) == models.CharField and getattr(self, field.name) is not None):
				result = True
				for word in words:
					if(not(word in unidecode(getattr(self, field.name)).lower())):
						result = False
				#print words, unidecode(getattr(self, field.name)).lower(), result
				#if result:
				#	break
			elif (type(field) == models.FileField):
				result = True
				result_owner = True
				result_content = True
				extract =  ''
				for word in words:
					if(not(word in unidecode(self.owner_name()).lower())):
						result_owner = False
				#Se revisa el texto plano.
				for word in words:
					text = open(self.document.url.replace('pdf', 'txt')).read().replace(' \n' , ' ').replace('\n', ' ').replace('  ', ' ')
					if(not(word in text)):
						result_content = False

				result = result_owner or result_content

				if result_content:
					word = words[0]
					initial_index = text.index(word)
					if initial_index - 60 < 0:
						initial_index = 0
					else:
						initial_index -= 60
						extract += '...'
					if initial_index + 200 > len(text):
						end_index = len(text) - 1
					else:
						end_index = initial_index + 200
					extract += text[initial_index:end_index] + '...'

				if result:
					break
			elif (field == self._meta.get_field('date')):
				result = True
				for word in words:
					if(not(word in unidecode(str(self.date)).lower())):
						result = False
				#if result:
				#	break
		ret = {'match': result, 'extract': extract}
		return ret

	def dictionary(self):
		dic = {}
		for field in self._meta.fields:
			if field.name not in ['owner', 'date_added', 'document', 'thumbnail']:
				dic[field.name] = getattr(self, field.name)
			elif field.name == 'thumbnail':
				dic[field.name] = self.thumbnail_filename()
		return dic

	def save_abstract(self):
		text = open(self.document.url.replace('pdf', 'txt')).read().replace(' \n' , ' ').replace('\n', ' ').replace('  ', ' ')
		initial_index = 0
		if initial_index + 400 > len(text):
			end_index = len(text) - 1
		else:
			end_index = initial_index + 400
		self.abstract = text[initial_index:end_index]
		self.save()
		return self.abstract

	def keywords(self):
		text = open(self.document.url.replace('pdf', 'txt')).read().replace(' \n' , ' ').replace('\n', ' ').replace('  ', ' ').replace('.', '').replace(',', '')
		reg = re.compile('\S{4,}')
		c = Counter(ma.group() for ma in reg.finditer(text))
		keywords = []
		for word, count in c.most_common(5):
			keywords.append(word)
		self.words = ','.join(keywords)
		self.save()
		return keywords

	def privacy(self):
		if self.type == 0:
			return 'public'
		else:
			return 'private'

