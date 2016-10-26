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
	category = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
	type = models.BooleanField()
	title = models.CharField(max_length=300, null=True)
	author = models.CharField(max_length=300, null=True)
	date = models.DateField(null=True)
	abstract = models.CharField(max_length=1000, null=True)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	date_added = models.DateField(auto_now_add=True)
	drive_id = models.CharField(max_length=100, null=True)
	thumbnail = models.FileField(upload_to='static/thumbnails/', max_length=500)
	words = models.CharField(max_length=200, null=True)
	issn = models.CharField(max_length=20, null=True)
	doi = models.CharField(max_length=50, null=True)
	url = models. CharField(max_length= 50, null=True)
	pages = models. CharField(max_length= 25, null=True)

	#Retorna el nombre del archivo pdf.
	def filename(self):
		return os.path.basename(self.document.name)

	def thumbnail_filename(self):
		return 'thumbnails/' + os.path.basename(self.thumbnail.name)

	#http://stackoverflow.com/questions/12358920/renaming-files-in-django-filefield
	def format_filename(self):
		new_filename= settings.DOC_ROOT + 'U' + str(self.owner.id) + 'I' + str(self.id) + '.pdf'
		print settings.MEDIA_ROOT + new_filename
		os.rename(self.document.path, (new_filename))
		self.document.name = new_filename
		self.save()
		return self.document.name

	def format_thumbnail_filename(self):
		new_filename= settings.THUMBNAILS_ROOT + 'U' + str(self.owner.id) + 'I' + str(self.id) + '.jpg'
		os.rename(self.thumbnail.path, (new_filename))
		self.thumbnail.name = new_filename
		self.save()
		return self.thumbnail.name


	#Retorna el nombre completo del duenno.
	def owner_name(self):
		return self.owner.first_name + ' ' + self.owner.last_name

	
	#Dado una string de palabras(words). Si todas coinciden con al menos un campo de la fila, retorna True.
	def match(self, words):
		splitted_words = unidecode(words.lower()).split(' ')
		words = words.lower()
		result = True
		exact = False
		for field in self._meta.fields:
			#Si es un campo de texto y no esta vacio:
			if (type(field) == models.CharField and getattr(self, field.name) is not None):
				if words in unidecode(getattr(self, field.name)).lower():
					exact = True
				else:
					for word in splitted_words:
						if(not(word in unidecode(getattr(self, field.name)).lower())):
							result = False
							break
				if result:
					break

			#Si es la fecha:
			elif (field == self._meta.get_field('date')):
				if word in unidecode(str(self.date)).lower():
					exact = True
				for word in splitted_words:
					if(not(word in unidecode(str(self.date)).lower())):
						result = False
						break
				if result:
					break
		#Si el campo contiene el archivo:
		result_owner = True
		result_content = True
		exact_content = False
		extract =  ''
		if not exact and not result:
			if words in unidecode(self.owner_name()).lower():
				exact = True
			else:
				for word in splitted_words:
					if(not(word in unidecode(self.owner_name()).lower())):
						result_owner = False

		#Se revisa el texto plano.
		text = open(self.document.path.replace('pdf', 'txt')).read().replace(' \n' , ' ').replace('\n', ' ').replace('  ', ' ')
		print words
		if words in text:
			exact_content = True
		else:
			for word in splitted_words:
				if(not(word in text)):
					result_content = False

		if result_content:
			if exact_content:
				initial_index = text.index(words)
			else:
				initial_index = text.index(splitted_words[0])
			
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
		if not result:
			result = result_owner or result_content
		if exact_content and not exact:
			exact = True
		print 'exact ',exact_content
		print 'no exact', result_content
		ret = {'match': result, 'extract': extract, 'exact': exact}
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
		text = open(self.document.path.replace('pdf', 'txt')).read().replace(' \n' , ' ').replace('\n', ' ').replace('  ', ' ')
		initial_index = 0
		if initial_index + 400 > len(text):
			end_index = len(text) - 1
		else:
			end_index = initial_index + 400
		self.abstract = text[initial_index:end_index]
		self.save()
		return self.abstract

	def keywords(self):
		text = open(self.document.path.replace('pdf', 'txt')).read().replace(' \n' , ' ').replace('\n', ' ').replace('  ', ' ').replace('.', '').replace(',', '')
		reg = re.compile('\S{4,}')
		c = Counter(ma.group() for ma in reg.finditer(text))
		keywords = []
		for word, count in c.most_common(5):
			keywords.append(word)
		self.words = ','.join(keywords)
		self.save()
		return keywords

	def get_keywords(self):
		if(len(self.words) == 0):
			return None
		else:
			list = self.words.split(',')
			return list

	def privacy(self):
		if self.type == 0:
			return 'public'
		else:
			return 'private'

