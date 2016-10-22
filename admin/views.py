# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import BadHeaderError, get_connection, EmailMultiAlternatives
from login.models import User, Area, UserManager
from intranet.models import Document
from unidecode import unidecode
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt # SOLO PARA TESTING
from django.utils.translation import ugettext as _ # Para traducir un string se usa: _("String a traducir")


from intranet.forms import DocumentForm
from django.db.models import Q, Count
from unidecode import unidecode
import os, sys, json, operator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from django.core.files import File 
from pdfminer.pdfdocument import PDFDocument
from PyPDF2 import PdfFileWriter, PdfFileReader
from cStringIO import StringIO
import unicodedata, tempfile
from datetime import date, timedelta
from django.utils import timezone
from collections import Counter
from itertools import chain
#import Levenshtein, random
from django.db import connection
from django.conf import settings


# Create your views here.

def home(request):
	if request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('admin:users'))
	else:
		return HttpResponseRedirect(reverse('webpage:home'))



def get_filters(rqst):
	dict = {}
	for key in rqst.GET:
		if key == 'date':
			str = '__year__in'
		else:
			str = '__in'
		if len(rqst.GET.getlist(key)) > 0:
			dict[key + str] = rqst.GET.getlist(key)
	return dict

def filters_selected(list, request, name):
	count = 0
	for val in list:
		if val[0] != None:
			if unicode(val[0]) in request.GET.getlist(name):
				list[count] = val + (True,)
			elif name == 'owner' or name == 'category':
				if unicode(val[0].id) in request.GET.getlist(name):
					list[count] = val + (True,)
				else:
					list[count] = val + (False,)
					break
			else:
				list[count] = val + (False,)
		count += 1
	return list

def documents(request, search=None):
	if request.user.is_admin:
		kwargs = get_filters(request)
		all_docs = Document.objects.filter(**kwargs)
		if search is None: #Si no es una busqueda
			documents = all_docs
		else:
			documents = []
			high_acc_result = []
			low_acc_result = []
			authors = []
			years = []
			owners = []
			categories = []
			for document in all_docs:
				result = document.match(search)
				if result['match']:
					if result['extract'] != '':
						setattr(document, 'extract', result['extract'])
					if result['exact']:
						high_acc_result.append(document)
					else:
						low_acc_result.append(document)
					authors.append(document.author)
					years.append(document.date.year)
					owners.append(document.owner)
					categories.append(document.category)
			documents = high_acc_result + low_acc_result
			authors = filters_selected(Counter(authors).most_common(), request, 'author')
			years = filters_selected(Counter(years).most_common(), request, 'date')
			owners = filters_selected(Counter(owners).most_common(), request, 'owner')
			categories = filters_selected(Counter(categories).most_common(), request, 'category')
		parameters = {'current_view': 'admin', 'documents': documents}
		if search is not None:
			parameters['authors'] = authors
			parameters['years'] = years
			parameters['categories'] = categories
			parameters['owners'] = owners
			parameters['search'] = search
		return render(request, 'admin/documents.html',parameters)
	else:
		return HttpResponseRedirect(reverse('login'))


def users(request, user_id=None, delete=False, activate=False, block=False, unblock=False, profile=False):
	if request.user.is_authenticated() and request.user.is_admin:
		if request.method == "GET":
			if activate:
				user = User.objects.get(id=user_id)
				user.is_active = True
				user.save()
				return JsonResponse({'error': False})
			elif delete:
				User.objects.get(id=user_id).delete()
				return JsonResponse({'error': False})
			elif block:
				user = User.objects.get(id=user_id)
				user.is_blocked = True
				user.save()
				return JsonResponse({'error': False})
			elif unblock:
				user = User.objects.get(id=user_id)
				user.is_blocked = False
				user.save()
				return JsonResponse({'error': False})
			elif profile:
				profile = User.objects.get(id=user_id)
				documents = Document.objects.filter(owner=user_id)
				return render(request, 'admin/profile.html', {'profile_user': profile, 'documents': documents})
			else:
				return render(request, 'admin/users.html')

		elif request.method == "POST":
			args = {
				'not_registered': User.objects.filter(is_registered=False, is_admin=False),
				'registered': User.objects.filter(is_registered=True, is_blocked=False, is_admin=False),
				'blocked': User.objects.filter(is_registered=True, is_blocked=True, is_admin=False)
			}
			return render(request, 'admin/users_ajax.html', args)

	else:
		return HttpResponseRedirect(reverse('login'))

def sendInvitation(request):
	if request.user.is_authenticated():
		if request.user.is_admin and request.method == "POST":
			error = False
			emails = request.POST["email"].split(',') # Recibe los correos electronicos separados por coma

			from_email = "LABMMBA <dev.sanideas@gmail.com>"
			subject = "[Registro] Invitación a la intranet de LABMMBA"
			text = "..."

			# Se utilizan las configuraciones SMTP de settings.py
			connection = get_connection()
			connection.open()

			# Se lee la plantilla de correos electronicos
			body = open(settings.MEDIA_ROOT + "/static/email_template/invitation_template.html", 'r')
			html = body.read().decode('UTF-8')
			body.close()

			for email in emails:
				token = ""
				while True: #Crea tokens hasta que no se repitan en la base de datos
					token = get_random_string(length=128)
					try:
						User.objects.get(access_token=token)
					except Exception:
						break
				# Crear usuario en la base de datos con su respectivo token, correo electronico y nombre
				user = User.objects.filter(email=email).first()
				if user is None or not user.is_registered:
					message = EmailMultiAlternatives(subject, text, from_email, [email])
					message.attach_alternative(html.replace('$token', token), 'text/html')

					try:
						message.send()
						if user is None:
							User.objects.precreate_user(email, token)
						else:		# Actualizar token si el usuario ya existe
							user.access_token = token
							user.save()
					except Exception:
						error = True
				else:
					error = True
			connection.close()

			if error:
				return JsonResponse({'error': True, 'message': _(u'Uno o más correos son inválidos o ya se encuentran registrados')})
			else:
				return JsonResponse({'error': False, 'message': _('')})
		elif not request.user.is_admin:
			return HttpResponseRedirect(reverse('webpage:home'))

	else:
		return HttpResponseRedirect(reverse('webpage:home'))