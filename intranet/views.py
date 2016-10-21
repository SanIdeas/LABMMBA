# -*- coding: utf-8 -*-
from django.shortcuts import render
from login.models import Area
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
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
from datetime import date, timedelta
from django.utils import timezone
from collections import Counter
from itertools import chain
from django.utils.translation import ugettext as _ # Para traducir un string se usa: _("String a traducir")
#import Levenshtein, random
from django.db import connection
from django.conf import settings


#Retorna el porcentaje de similitud entre dos strings.
#Se utiliza el algoritmo de Levenshtein ya que tiene mejor rendimiento. Fuente:
#http://stackoverflow.com/questions/6690739/fuzzy-string-comparison-in-python-confused-with-which-library-to-use
#def similar(a, b):
#	return Levenshtein.ratio(a, b)

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

def home(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		start_date = (date.today() - timedelta(5*365/12))
		n = start_date.month#Initial Month
		categories = Document.objects.values('category').annotate(count=Count('category'))
		dates = Document.objects.filter(date_added__gte=start_date.strftime('%Y-%m-1'))
		months = []

		for i in dates:
			months.append(i.date_added.strftime('%B'))
		months_counts =  dict(Counter(months))
		months_map = {0: 'January', 1: 'February', 2: 'March', 3: 'April', 4: 'May', 5: 'June', 6: 'July', 7: 'August', 8: 'September',9: 'October', 10: 'November',11: 'December'}
		actual_month = date.today().month
		months = []
		counts = []
		for i in reversed(range(actual_month-1,actual_month - 7, -1)):
			months.append(_(months_map[i%12]))
			if months_map[i%12] in months_counts:
				counts.append(str(months_counts[months_map[i%12]]))
			else:
				counts.append('0')
		names_months = '"' + '" ,"'.join(months) + '"'
		count_months = ','.join(counts)
		names=[]
		count=[]
		for a in categories:
			try:
				names.append(_(Area.objects.get(id=a['category']).name))
				count.append(str(a['count']))
			except:
				None
		names_categories = '"' + '","'.join(names) + '"'
		count_categories = ','.join(count)
		return render(request, 'intranet/home.html', {'names_categories': names_categories, 'count_categories': count_categories, 'number_categories': len(names), 'names_months':names_months, 'count_months': count_months })
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))

def documents(request, search=None):
	if request.user.is_authenticated() and not request.user.is_admin:
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
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))

def profile(request, user_id):
	if request.user.is_authenticated():
		try:
			if request.user.is_admin:
				profile = User.objects.get(id=user_id)
			else:
				profile = User.objects.get(id=user_id, is_admin=request.user.is_admin)
			documents = Document.objects.filter(owner=user_id)
			return render(request, 'intranet/profile.html', {'current_view': 'intranet', 'profile_user': profile, 'documents': documents})
		except:
			return HttpResponseRedirect(reverse('intranet:users'))
	else:
		return HttpResponseRedirect(reverse('login'))

def update_profile_picture(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		User.objects.get(id=request.user.id).update_picture(request.FILES['picture'])
		return HttpResponseRedirect(reverse('intranet:profile', args={request.user.id}))

def upload(request):
	print request.user.is_authenticated()
	if request.user.is_authenticated() and not request.user.is_admin:
		#Document.objects.all().delete()
		#User.objects.all().delete()
		if request.method == "GET":
			return render(request, 'intranet/upload.html', {'current_view': 'intranet'})
		else:
			if 'id' in request.POST:
				ids = request.POST['id'].split(',')
				for id in ids:
					document = Document.objects.get(id=id,owner=request.user)
					document.title = request.POST['title' + id]
					document.author = request.POST['author' + id]
					document.date = request.POST['date' + id]
					document.category = Area.objects.get(id=request.POST['category' + id])
					document.type = int(request.POST['type' + id])
					document.abstract = request.POST['abstract' + id]
					document.issn = request.POST['issn' + id]
					document.doi = request.POST['doi' + id]
					document.url = request.POST['url' + id]
					document.pages = request.POST['pages' + id]
					document.save()
				return JsonResponse({'error': False, 'message':_('Actualizado con exito.')})
			#Local_ids son las ids de los archivos locales del usuario
			elif 'local_ids' in request.POST:
				local_ids = request.POST['local_ids'].split(',')
				real_ids=[]
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
						'issn': request.POST['issn' + id],
						'doi': request.POST['doi' + id],
						'url': "http://dx.doi.org/" + request.POST['doi' + id],
						'pages': request.POST['pages' + id],
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
						real_ids.append(document.id)
						try:
							text_file = open(settings.MEDIA_ROOT + document.document.url.replace('pdf', 'txt'), 'w')
							text_from_file = strip_accents(convert_pdf_to_txt(document.document.url))
							text_file.write(text_from_file.lower())
							text_file.close()
						except:
							text_file =  open(settings.MEDIA_ROOT + document.document.url.replace('pdf', 'txt'), 'w')
							text_file.close()
						document.save_abstract()
						document.keywords()
					else:
						return JsonResponse({'error': True, 'message':_('Ocurrio un problema: %(error)s') % {'error':str(form.errors)}})
				return JsonResponse({'error': False, 'message':_('Subida exitosa'), 'real_ids': real_ids})
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return JsonResponse({'error': True, 'message':_('Debes iniciar sesion.')})

def upload_local(request):
	return render(request, 'intranet/upload_sections/local.html')

def upload_drive(request):
	return render(request, 'intranet/upload_sections/drive.html')

def extract_content_and_keywords(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.POST['ids']:
			abstracts = []
			for id in request.POST['ids'].split(','):
				document = Document.objects.get(id=id) 
				try:
				    text_file = open(document.document.url.replace('pdf', 'txt'), 'w')
				    text_from_file = strip_accents(convert_pdf_to_txt(document.document.url))
				    text_file.write(text_from_file.lower())
				    text_file.close()
				except:
				    text_file = open(document.document.url.replace('pdf', 'txt'), 'w')
				    text_file.close()
				document.save_abstract()
				document.keywords()
				abstracts.append({'id': document.id, 'abstract': document.abstract})
			return JsonResponse({'error': False, 'abstracts': abstracts})
		else:
			return JsonResponse({'error': True})
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
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
			with open(settings.MEDIA_ROOT + document.document.url, 'rb') as pdf:
				response =  HttpResponse(pdf.read(), content_type='application/pdf')
				response['Content-Disposition'] = 'inline;filename="some_file.pdf"'.replace('some_file',title)
				response['Content-Length'] = os.stat(settings.MEDIA_ROOT + document.document.url).st_size
				return response
			pdf.close()
		else:
			return HttpResponse(_('Debes tener una cuenta para visualizar este archivo.'))
	else:
		return HttpResponse(_('No se encontraron documentos con el nombre: %(title)s') % {'title': title})

def users(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		users = User.objects.filter(is_admin=False)
		for user in users:
			user.last_activity = (timezone.localtime(timezone.now()).date() - user.last_activity).days
		return render(request, 'intranet/users.html', {'users': users})
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))


def document(request, title=None, author=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		try:
			document = Document.objects.get(title=title, author=author)
		except Document.DoesNotExist:
			document = None
		if document is not None:
			return render(request, 'intranet/document_information.html', {'current_view': 'intranet', 'document': document})
		else:
			return HttpResponse(_('No se encontro el documento %(title)s del autor %(author)s') % {'title': title, 'author': author})
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))
def edit_document(request, title=None, author=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		try:
			if request.user.is_admin:
				document = Document.objects.get(title=title, author=author)
			else:
				document = Document.objects.get(title=title, author=author, owner=request.user)
		except:
			document = None
		if document:
			if request.method == "GET":
				return render(request, 'intranet/edit_document_information.html', {'current_view': 'intranet', 'document': document})
			elif request.method == "POST":
					document.title = request.POST['title']
					document.author = request.POST['author']
					document.date = request.POST['date']
					document.category = Area.objects.get(id=request.POST['category'])
					document.abstract = request.POST['abstract']
					document.issn = request.POST['issn']
					document.doi = request.POST['doi']
					document.words = request.POST['words']
					document.url = "http://dx.doi.org/" + request.POST['doi']
					document.pages = request.POST['pages']
					document.save()
					return HttpResponseRedirect(reverse('intranet:document', kwargs={'title': request.POST['title'], 'author': request.POST['author']}))
			elif request.method == "DELETE":
				document.owner.doc_number('-')
				document.delete()
				return JsonResponse({'error': False})
		else:
			return HttpResponseRedirect(reverse('intranet:document', kwargs={'title': title, 'author': author})) #Se redirecciona a la ultima pagina visitada.
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))



def search_helper(request, search=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		doc = Document.objects.values('title', 'author').filter(reduce(operator.and_, (Q(title__contains=x) for x in search.split(' '))))
		response = {'error': False, 'list': list(doc)}
		return JsonResponse(response)
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))