# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils.text import slugify
from django.conf import settings
from django.db import models
from login.models import User, Area, SubArea
from unidecode import unidecode
from collections import Counter
import os, re, operator, unicodedata, datetime, time, pytz
from django.utils.translation import ugettext as _ # Para traducir un string se usa: _("String a traducir")
# Herramientas PDF
from PyPDF2 import PdfFileWriter, PdfFileReader
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from django.core.files import File 
from cStringIO import StringIO

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# Utilidades

#Recibe un stream y retorna un diccionario con los metadatos.
def get_metadata(stream):
	pdf = PdfFileReader(stream)
	return pdf.getDocumentInfo()

def strip_accents(str):
	str = str.decode("cp1252")  # decode from cp1252 encoding instead of the implicit ascii encoding used by unicode()
	str = unicodedata.normalize('NFKD', str).encode('ascii', 'ignore')
	return str

def pdf_to_str(path):
	rsrcmgr = PDFResourceManager()
	retstr = StringIO()
	codec = 'cp1252'
	laparams = LAParams()
	device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
	fp = file(path, 'rb')
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	password = ""
	maxpages = 0
	caching = True
	pagenos=set()
	for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
		interpreter.process_page(page)
	fp.close()
	device.close()
	str = retstr.getvalue()
	retstr.close()
	return str

def date(date):
	if date[0] == 'D':
		year = date[2:6]
		month = date[6:8]
		day = date[8:10]
		return day, month, year
	else:
		month, day, year = re.match('([0-9])*\/([0-9]*)\/([0-9]*)', date).groups()
		return day, month, year



# Create your models here.

class Document(models.Model):
	document = models.FileField(upload_to='uploads/documents/', max_length=500)
	category = models.ForeignKey(SubArea, on_delete=models.SET_NULL, null=True)
	title = models.CharField(max_length=300, null=True)
	title_slug = models.SlugField(max_length=300, null=True)
	author = models.CharField(max_length=300, null=True)
	author_slug = models.SlugField(max_length=300, null=True)
	date = models.DateField(null=True)
	content = models.TextField(null=True)
	abstract = models.CharField(max_length=1000, null=True)
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	date_added = models.DateTimeField(auto_now_add=True)
	drive_id = models.CharField(max_length=100, null=True)
	thumbnail = models.FileField(upload_to='static/thumbnails/', max_length=500)
	words = models.CharField(max_length=200, null=True)
	issn = models.CharField(max_length=20, null=True)
	doi = models.CharField(max_length=50, null=True)
	pages = models.CharField(max_length= 25, null=True)
	is_available = models.BooleanField(default=False)
	first_save_flag = models.BooleanField(default=False)
	is_public = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if self.title:
			self.title_slug = slugify(self.title)
		if self.author:
			self.author_slug = slugify(self.author)

		self.owner.update_activity()

		super(Document, self).save(*args, **kwargs)

		# Solo cuando se guarda por primera vez
		if not self.first_save_flag:
			self.owner.doc_number('+')

			# Se arregla el nombre de archivo documento
			# http://stackoverflow.com/questions/12358920/renaming-files-in-django-filefield
			new_filename = settings.DOC_ROOT + 'U' + str(self.owner.id) + 'I' + str(self.id) + '.pdf'
			os.rename(self.document.path, (new_filename))
			self.document.name = new_filename

			# Se arregla el nombre de la imagen miniatura (solo si aplica)
			if self.thumbnail:
				new_filename = settings.THUMBNAILS_ROOT + 'U' + str(self.owner.id) + 'I' + str(self.id) + '.jpg'
				os.rename(self.thumbnail.path, (new_filename))
				self.thumbnail.name = new_filename

			# Si es un documento de Google Drive, se extraen los metadatos
			if self.drive_id is not None:
				meta = get_metadata(self.document)
				print "-------------Funciona"
				try:
					day, month, year = date(meta['/CreationDate'])
					self.title = meta['/Title'] if '/Title' in meta and meta['/Title']  else 'Titulo temporal' + str(datetime.datetime.now())
					self.author = meta['/Author'] if  '/Author' in meta else owner.first_name + ' ' + owner.last_name
					self.abstract = meta['/Subject'] if  '/Subject' in meta else None
					self.words = meta['/Keywords'].replace('; ', ',') if  '/Keywords' in meta else None
					self.date = year + '-' + month + '-' + day if '/CreationDate' in meta else '2000-01-01'
				except:
					self.title = 'Titulo temporal ' + str(datetime.datetime.now())
					self.date = '2000-01-01'
			# Si no es de Google Drive, se declara disponible inmediatamente, ya que el usuario ya comprobo los datos
			else:
				self.is_available = True

			# Finalmente, se extrae el contenido del archivo PDF y sus palabras clave solo si no es un archivo de Google Drive
			if self.drive_id is None:
				content = " ".join(strip_accents(pdf_to_str(self.document.path)).lower().split())
				self.content = content

				# Se guarda el resumen
				if 400 > len(content):
					end_index = len(content) - 1
				else:
					end_index =  400
				self.abstract = content[0:end_index]

				# Se guardan la palabras clave
				reg = re.compile('\S{4,}')
				c = Counter(ma.group() for ma in reg.finditer(content))
				keywords = []
				for word, count in c.most_common(5):
					keywords.append(word)
				self.words = ','.join(keywords)
			self.first_save_flag = True
			self.save()

	#Retorna el nombre del archivo pdf.
	def filename(self):
		return os.path.basename(self.document.name)

	def thumbnail_filename(self):
		return 'thumbnails/' + os.path.basename(self.thumbnail.name)


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
				# Si la frase completa coincide:
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
				if words in unidecode(str(self.date)).lower():
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
		text = self.content if self.content is not None else "Documento sin contenido"
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
			if field.name not in ['owner', 'date_added', 'document', 'thumbnail', 'date']:
				dic[field.name] = getattr(self, field.name)
			elif field.name == 'thumbnail':
				dic[field.name] = self.thumbnail_filename()
			elif field.name == 'date':
				date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
				dic[field.name] = date.strftime('%d-%m-%Y')
		return dic


	def get_keywords(self):
		if(len(self.words) == 0):
			return None
		else:
			list = self.words.split(',')
			return list

	def privacy(self):
		if self.is_public == 0:
			return _(u'Laboratorio')
		else:
			return _(u'Público')

	def get_doi_url(self):
		return 'http://dx.doi.org/' + self.doi

	def save_abstract_and_content(self):
		text = content = " ".join(strip_accents(pdf_to_str(self.document.path)).lower().split())
		self.content = text
		if 400 > len(text):
			end_index = len(text) - 1
		else:
			end_index = 400
		self.abstract = text[0:end_index]
		self.save()

	def keywords(self):
		reg = re.compile('\S{4,}')
		c = Counter(ma.group() for ma in reg.finditer(self.content))
		keywords = []
		for word, count in c.most_common(5):
			keywords.append(word)
		self.words = ','.join(keywords)
		self.save()

class Forum(models.Model):
	title = models.CharField(max_length=300, null=False)
	slug = models.SlugField(max_length=300, null=False)
	date = models.DateTimeField(auto_now_add=True)
	content = models.TextField(null=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	type = models.CharField(max_length=50, null=False)

	def save(self, *args, **kwargs):
		slug = slugify(self.title)
		forum = Forum.objects.filter(title=self.title).exclude(id=self.id)
		count = 0
		# Si existe una noticia con el mismo nombre
		# Se agrega un numero al final del slug
		if forum:
			while True:
				count += 1
				slug_temp = slug + '-' + str(count)
				if not Forum.objects.filter(slug=slug_temp).exclude(id=self.id):
					break
			slug += '-' + str(count)
		self.slug = slug
		super(Forum, self).save(*args, **kwargs)

	def get_comments(self):
		return ForumComment.objects.filter(forum=self.id)

	def can_remove(self):
		delta = datetime.datetime.now(pytz.UTC) - self.date
		if delta.total_seconds()/60 < 5:
			return True
		return False

	def get_last_comment(self):
		return ForumComment.objects.filter(forum=self.id).last()

class ForumComment(models.Model):
	forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
	content = models.TextField(null=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
	object_id = models.PositiveIntegerField(null=True)
	content_object = GenericForeignKey('content_type', 'object_id')

	def can_remove(self):
		delta = datetime.datetime.now(pytz.UTC) - self.date
		if delta.total_seconds()/60 < 5:
			return True
		return False

	def get_time_ago(self):
		delta = datetime.datetime.now(pytz.UTC) - self.date
		minutes = delta.total_seconds()/60
		hours = delta.total_seconds()/3600
		days = delta.days
		if minutes < 1:
			return _(u'Recién')
		elif minutes > 1 and minutes < 2:
			return _(u'Hace %s minuto') % (str(int(minutes)))
		elif minutes > 2 and minutes < 60:
			return _(u'Hace %s minutos') % (str(int(minutes)))
		elif hours >= 1 and hours < 2:
			return _(u'Hace %s hora') % (str(int(hours)))
		elif hours >= 2 and hours < 24:
			return _(u'Hace %s horas') % (str(int(hours)))
		elif days >= 1 and hours < 2:
			return _(u'Hace %s día') % (str(int(days)))
		else:
			return _(u'Hace %s días') % (str(int(days)))


@receiver(post_delete, sender=Document)
def document_delete(sender, instance, **kwargs):
	instance.document.delete(False)
	instance.thumbnail.delete(False)
