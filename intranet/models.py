from __future__ import unicode_literals

from django.db import models
from login.models import User
from unidecode import unidecode
import os

# Create your models here.

class Document(models.Model):
	document = models.FileField(upload_to='uploads/documents/', max_length=500)
	category = models.CharField(max_length=50)
	type = models.BooleanField()
	title = models.CharField(max_length=100)
	author = models.CharField(max_length=100)
	date = models.DateField()
	abstract = models.CharField(max_length=200, null=True)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	date_added = models.DateField(auto_now_add=True)

	#Retorna el nombre del archivo pdf.
	def filename(self):
		return os.path.basename(self.document.name)

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
				if result:
					break
			elif (type(field) == models.FileField):
				result = True
				result_owner = True
				result_content = True
				extract =  ''
				for word in words:
					if(not(word in unidecode(self.owner_name()).lower())):
						result_owner = False
				#Se revisa el texto plano.
				print '------------------------------------'
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
				if result:
					break

		print 'termina', result
		ret = {'match': result, 'extract': extract}
		return ret
