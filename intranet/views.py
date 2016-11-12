# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.db.models.functions import Lower
from django.core.files import File
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _ # Para traducir un string se usa: _("String a traducir")
from django.core.paginator import Paginator
from intranet.forms import DocumentForm
from intranet.models import Document
from login.models import Area, User
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from PyPDF2 import PdfFileWriter, PdfFileReader
from unidecode import unidecode
from cStringIO import StringIO
from datetime import date, timedelta
from collections import Counter
from itertools import chain
import os, sys, json, operator, unicodedata, tempfile, httplib2


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
		elif key == 'page' or key == 'kw':
			continue
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
		# Se obtiene la cantidad de documentos de los ultimos 6 meses
		# Fecha de inicio
		start_date = (date.today() - timedelta(5*365/12))
		# Todos los documentos de los ultimos 6 meses
		dates = Document.objects.filter(date_added__gte=start_date.strftime('%Y-%m-1'))
		months = []

		# Se almacena el nombre de los meses de cada documento en dates
		for i in dates:
			months.append(i.date_added.strftime('%B'))
		# Se cuentan la cantidad de repeticiones de cada mes
		months_counts =  dict(Counter(months))
		months_map = {0: 'January', 1: 'February', 2: 'March', 3: 'April', 4: 'May', 5: 'June', 6: 'July', 7: 'August', 8: 'September',9: 'October', 10: 'November',11: 'December'}
		current_month = date.today().month
		months = []
		counts = []
		# Se recorren los ultimos 6 meses y se va comprobando la cantidad de documentos de cada uno
		for i in reversed(range(current_month-1,current_month - 7, -1)):
			months.append(_(months_map[i%12]))
			if months_map[i%12] in months_counts:
				counts.append(str(months_counts[months_map[i%12]]))
			else:
				counts.append('0')
		names_months = '"' + '" ,"'.join(months) + '"'
		count_months = ','.join(counts)

		# Se cuenta la cantidad de documentos por categoria
		names=[]
		count=[]
		categories = Document.objects.values('category').annotate(count=Count('category'))
		for a in categories:
			try:
				names.append(_(Area.objects.get(id=a['category']).name))
				count.append(str(a['count']))
			except:
				None
		if len(names):
			names_categories = '"' + '","'.join(names) + '"'
			count_categories = ','.join(count)
		else:
			names_categories = None
			count_categories = None

		# Se obtienen un preview de los usuarios en el sistema
		users = User.objects.filter(is_admin=False).order_by('last_activity')
		return render(request, 'intranet/home.html', {
													'names_categories': names_categories,
													'count_categories': count_categories,
													'number_categories': len(names),
												 	'names_months':names_months,
												  	'count_months': count_months,
												  	'users_preview': users[:5],
												  	'users_count': len(users) - 5 if len(users) > 5 else 0,
												  	'last_five_documents': Document.objects.all().order_by(Lower('date_added').desc())[:5],
												  	'documents_count': Document.objects.all().count()
												  	})
	elif request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))

def documents(request, search=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		kwargs = get_filters(request)
		parameters = {'current_view': 'intranet'}

		try:
			all_docs = Document.objects.filter(is_available=True, **kwargs)
		except:
			all_docs = Document.objects.filter(is_available=True)


		#Si no es una busqueda
		if search is None:
			# Se obtiene la palabra clave si es que la hay
			# Si no hay, se obtienen las paginas
			if request.GET.get('kw'):
				parameters['keyword'] = request.GET.get('kw')
				parameters['documents'] = []
				for document in all_docs:
					if request.GET.get('kw') in document.get_keywords():
						parameters['documents'].append(document)
			else:
				paginator = Paginator(all_docs, 5);
				# Se obtienen las categorias disponibles
				parameters['categories'] = []
				for category in Document.objects.values('category').distinct():
					parameters['categories'].append(Area.objects.get(id=category['category']))

				# Se extrae el numero de pagina
				if request.GET.get('page'):
					try: parameters['documents'] = paginator.page(request.GET.get('page'))
					except: parameters['documents'] = paginator.page(1)
				else:
					parameters['documents'] = paginator.page(1)

		# Si es una busqueda
		else:
			documents = []
			high_acc_result = [] # Resultados de alta presicion
			low_acc_result = [] # Resultados de baja presicion

			# Lista con los authores, años, dueños y categorias, y sus contadores.
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

			# Se obtiene los datos del filtro
			documents = high_acc_result + low_acc_result
			authors = filters_selected(Counter(authors).most_common(), request, 'author')
			years = filters_selected(Counter(years).most_common(), request, 'date')
			owners = filters_selected(Counter(owners).most_common(), request, 'owner')
			categories = filters_selected(Counter(categories).most_common(), request, 'category')

			# Se almacenan los documentos en los parametros
			parameters['documents'] = documents

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

def profile(request, user_id = None):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.method == 'GET':
			try:
				if request.user.is_admin:
					profile = User.objects.get(id=user_id)
				else:
					profile = User.objects.get(id=user_id, is_admin=request.user.is_admin)
				documents = Document.objects.filter(owner=user_id)
				return render(request, 'intranet/profile.html', {'current_view': 'intranet', 'profile_user': profile, 'documents': documents, 'areas': Area.objects.all()})
			except Exception as error:
				print error
				return HttpResponseRedirect(reverse('intranet:users'))
		elif request.method == 'POST':
			# Si el metodo es POST
			request.user.first_name = request.POST['first_name']
			request.user.last_name = request.POST['last_name']
			request.user.institution = request.POST['institution']
			request.user.career = request.POST['career']
			request.user.area = Area.objects.get(id=request.POST['area'])
			request.user.first_name = request.POST['first_name']
			request.user.country = request.POST['country']
			request.user.save()
			return HttpResponseRedirect(reverse('intranet:profile', kwargs={'user_id': request.user.id}))
		else:
			# Si el metodo no es ni POST ni GET
			return HttpResponseRedirect(reverse('intranet:home'))
	else:
		# Si el usuario no ha iniciado sesion o es administrador
		return HttpResponseRedirect(reverse('login'))

def update_profile_picture(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		User.objects.get(id=request.user.id).update_picture(request.FILES['picture'])
		return JsonResponse({'error': False})

def upload(request):
	#request.user.credentials().revoke(httplib2.Http())
	#request.user.credentials().refresh(httplib2.Http())
	#print '---------------------------------------', request.user.credentials()._expires_in()
	#print request.user.is_authenticated()
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
					#document.abstract = request.POST['abstract' + id] POR MIENTRAS
					document.issn = request.POST['issn' + id]
					document.doi = request.POST['doi' + id]
					document.pages = request.POST['pages' + id]
					document.is_available = True
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
						'is_available': True,
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
							text_file = open(document.document.path.replace('pdf', 'txt'), 'w')
							text_from_file = strip_accents(convert_pdf_to_txt(document.document.path))
							text_file.write(text_from_file.lower())
							text_file.close()
						except:
							text_file =  open(document.document.path.replace('pdf', 'txt'), 'w')
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

# Extrae el contenido de los documentos identificados por las id recibidas
# Se usa al momento de subir archivos por Google Drive. El cliente llama a esta funcion explicitamente
def extract_content_and_keywords(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.POST['ids']:
			abstracts = []
			for id in request.POST['ids'].split(','):
				document = Document.objects.get(id=id) 
				try:
				    text_file = open(document.document.path.replace('pdf', 'txt'), 'w')
				    text_from_file = strip_accents(convert_pdf_to_txt(document.document.path))
				    text_file.write(text_from_file.lower())
				    text_file.close()
				except:
				    text_file = open(document.document.path.replace('pdf', 'txt'), 'w')
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
		document = Document.objects.get(title=title, author=author, is_available=True)
	except Document.DoesNotExist:
		document = None
	if document is not None:
		if ((document.type and request.user.is_authenticated()) or not document.type):
			#Informacion por 'rb': http://stackoverflow.com/questions/11779246/how-to-show-a-pdf-file-in-a-django-view
			with open(document.document.path, 'rb') as pdf:
				response =  HttpResponse(pdf.read(), content_type='application/pdf')
				response['Content-Disposition'] = 'inline;filename="some_file.pdf"'.replace('some_file',title)
				response['Content-Length'] = os.stat(document.document.path).st_size
				return response
			pdf.close()
		else:
			return HttpResponse(_('Debes tener una cuenta para visualizar este archivo.'))
	else:
		return HttpResponse(_('No se encontraron documentos disponibles con el nombre: %(title)s') % {'title': title})

def users(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		users = User.objects.filter(is_admin=False)
		for user in users:
			user.last_activity = (timezone.localtime(timezone.now()) - user.last_activity).days
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