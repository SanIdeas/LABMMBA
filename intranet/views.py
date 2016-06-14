# -*- coding: utf-8 -*-
from django.shortcuts import render
from login.models import Area
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from intranet.forms import DocumentForm
from intranet.models import Document
from django.db.models import Q, Count
from login.models import User
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
from datetime import date
from django.utils import timezone
from collections import Counter
from itertools import chain
from django.utils.translation import ugettext as _

# Create your views here.

def strip_accents(s):
	s = s.decode("cp1252")  # decode from cp1252 encoding instead of the implicit ascii encoding used by unicode()
	s = unicodedata.normalize('NFKD', s).encode('ascii','ignore')
	return s

#Recibe un stream y retorna un diccionario con los metadatos.
def get_metadata(stream):
	pdf = PdfFileReader(stream)
	return pdf.getDocumentInfo()


def convert_pdf_to_txt(path):
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

def get_filters(rqst):
	dict = {}
	for key in rqst.GET:
		print key
		if key == 'date':
			str = '__year__in'
		else:
			str = '__in'
		if len(rqst.GET.getlist(key)) > 0:
			print key + str
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

def home(request):
	return render(request, 'intranet/home.html')

def documents(request, search=None):
	if request.user.is_authenticated() == True:
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
		parameters = {'current_view': 'intranet', 'documents': documents}
		if search is not None:
			parameters['authors'] = authors
			parameters['years'] = years
			parameters['categories'] = categories
			parameters['owners'] = owners
			parameters['search'] = search
		return render(request, 'intranet/documents.html',parameters)
	else:
		print request.get_full_path
		return HttpResponseRedirect(reverse('login'))

def profile(request, user_id):
	if request.user.is_authenticated() == True:
		try:
			profile = User.objects.get(id=user_id, is_admin=request.user.is_admin)
			documents = Document.objects.filter(owner=user_id)
			return render(request, 'intranet/profile.html', {'current_view': 'intranet', 'profile_user': profile, 'documents': documents})
		except:
			return HttpResponseRedirect(reverse('intranet:users'))			
	else:
		return HttpResponseRedirect(reverse('login'))

def update_profile_picture(request):
	if request.user.is_authenticated() == True:
		User.objects.get(id=request.user.id).update_picture(request.FILES['picture'])
		return HttpResponseRedirect(reverse('intranet:profile', args={request.user.id}))

def upload(request):
	if request.user.is_authenticated() == True:
		#Document.objects.all().delete()
		#User.objects.all().delete()
		if request.method == "GET":
			return render(request, 'intranet/upload.html', {'current_view': 'intranet'})
		else:
			if 'id' in request.POST:
				ids = request.POST['id'].split(',')
				print ids
				for id in ids:
					document = Document.objects.get(id=id,owner=request.user)
					document.title = request.POST['title' + id]
					document.author = request.POST['author' + id]
					document.date = request.POST['date' + id]
					document.category = Area.objects.get(id=request.POST['category' + id])
					document.type = int(request.POST['type' + id])
					document.abstract = request.POST['abstract' + id]
					document.save()
				return JsonResponse({'error': False, 'message':_('Actualizado con exito.')})
			elif 'local_ids' in request.POST:
				local_ids = request.POST['local_ids'].split(',')
				for id in local_ids:
					if request.FILES['document'+id].size/1000 > 2048:
						return JsonResponse({'error': True, 'message':_('El archivo %(name)s no debe superar los 2 Mb') % {'name': request.FILES['document'+id].name}})

					if Document.objects.filter(title=request.POST['title'+id], author=request.POST['author'+id]).exists():
						message = _('El documento <span style="text-transform: uppercase; font-size:14px"> %(title)s </span> del autor <span style="text-transform: uppercase; font-size:14px"> %(author)s </span> ya existe.') % {'title': request.POST['title'+id],'author': request.POST['author'+id]}
						return JsonResponse({'error': True, 'message':message})

					request.POST['owner'] = User.objects.get(email=request.user.email)
					fields = {
						'title': request.POST['title'+id],
						'author': request.POST['author'+id],
						'date': request.POST['date'+id],
						'type': int(request.POST['type'+id]),
						'category': Area.objects.get(id=request.POST['category' + id]).id,
						'owner': request.user.id,
						}
					files = {
							'document': request.FILES['document'+id]
						}
					form = DocumentForm(fields, files)
					print form.errors
					if form.is_valid():
						document = form.save()
						document.owner.update_activity().doc_number('+')
						document.format_filename()
						try:
							text_file = open(document.document.url.replace('pdf', 'txt'), 'w')
							text_from_file = strip_accents(convert_pdf_to_txt(document.document.url))
							text_file.write(text_from_file.lower())
							text_file.close()
						except:
							text_file =  open(document.document.url.replace('pdf', 'txt'), 'w')
							text_file.close()
						document.save_abstract()
						document.keywords()
					else:
						return JsonResponse({'error': True, 'message':_('Ocurrio un problema: %(error)s') % {'error':str(form.errors)}})
				return JsonResponse({'error': False, 'message':_('Subida exitosa')})
	else:
		return JsonResponse({'error': True, 'message':_('Debes iniciar sesion.')})


def pdf_viewer(request, title=None, author=None):
	try:
		document = Document.objects.get(title=title, author=author)
	except Document.DoesNotExist:
		document = None
	if document is not None:
		if ((document.type and request.user.is_authenticated()) or not document.type):
			#Informacion por 'rb': http://stackoverflow.com/questions/11779246/how-to-show-a-pdf-file-in-a-django-view
			with open(document.document.url, 'rb') as pdf:
				response =  HttpResponse(pdf.read(), content_type='application/pdf')
				response['Content-Disposition'] = 'inline;filename="some_file.pdf"'.replace('some_file',title)
				response['Content-Length'] = os.stat(document.document.url).st_size
				return response
			pdf.close()
		else:
			return HttpResponse(_('Debes tener una cuenta para visualizar este archivo.'))
	else:
		return HttpResponse(_('No se encontraron documentos con el nombre: %(title)s') % {'title': title})

def users(request):
	if request.user.is_authenticated() == True:
		users = User.objects.filter(is_admin=False)
		for user in users:
			user.last_activity = (timezone.localtime(timezone.now()).date() - user.last_activity).days
		return render(request, 'intranet/users.html', {'users': users})
	else:
		return HttpResponseRedirect(reverse('login'))


def document(request, title=None, author=None):
	if request.user.is_authenticated() == True:
		try:
			document = Document.objects.get(title=title, author=author)
			related = Document.objects.values('title', 'author').filter(reduce(operator.or_, (Q(title__contains=x) for x in document.words.split(','))))
			print '----'
			print document.document
		except Document.DoesNotExist:
			document = None
		if document is not None:
			return render(request, 'intranet/document_information.html', {'current_view': 'intranet', 'document': document, 'related': related})
		else:
			return HttpResponse(_('No se encontró el documento %(title)s del autor %(author)s') % {'title': title, 'author': author})
	else:
		return HttpResponseRedirect(reverse('login'))

def new_ui(request):
	return render(request, 'intranet/shared.html')

def search_helper(request, search=None):
	if request.user.is_authenticated() == True:
		doc = Document.objects.values('title', 'author').filter(reduce(operator.and_, (Q(title__contains=x) for x in search.split(' '))))
		response = {'error': False, 'list': list(doc)}
		return JsonResponse(response)
	else:
		return HttpResponseRedirect(reverse('login'))

def admin(request):
	if request.user.is_authenticated() == True and request.user.is_admin:
		return render(request, 'intranet/admin.html')
	else:
		return HttpResponseRedirect(reverse('login'))