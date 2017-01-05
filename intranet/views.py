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
from intranet.forms import DocumentForm, ForumForm
from intranet.models import Document, Forum, ForumComment
from login.models import SubArea, Area, User
from webpage.models import Section, News, Image
from webpage.forms import NewsForm
from unidecode import unidecode
from datetime import date, timedelta, datetime
from django_countries import countries
from collections import Counter
from itertools import chain
import os, sys, json, operator, tempfile, httplib2


#Retorna el porcentaje de similitud entre dos strings.
#Se utiliza el algoritmo de Levenshtein ya que tiene mejor rendimiento. Fuente:
#http://stackoverflow.com/questions/6690739/fuzzy-string-comparison-in-python-confused-with-which-library-to-use
#def similar(a, b):
#	return Levenshtein.ratio(a, b)

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
				names.append(_(SubArea.objects.get(id=a['category']).area.name))
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
		users = User.objects.filter(is_admin=False, is_registered=True).order_by('last_activity')
		return render(request, 'intranet/home.html', {
													'names_categories': names_categories,
													'count_categories': count_categories,
													'number_categories': len(names),
												 	'names_months':names_months,
												  	'count_months': count_months,
												  	'users_preview': users[:5],
												  	'users_count': len(users) - 5 if len(users) > 5 else 0,
												  	'last_five_documents': Document.objects.all().order_by(Lower('date_added').desc())[:5],
												  	'documents_count': Document.objects.all().count(),
													'intranet': Section.objects.get(slug='intranet')
												  	})
	elif request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))

def documents(request, search=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		kwargs = get_filters(request)
		parameters = {'intranet': Section.objects.get(slug='intranet')}

		try:
			all_docs = Document.objects.filter(is_available=True, **kwargs).exclude(title__isnull=True, author__isnull=True)
		except:
			all_docs = Document.objects.filter(is_available=True).exclude(title__isnull=True, author__isnull=True)


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
				for category in Document.objects.filter(is_available=True, category__isnull=False).values('category').distinct():
					parameters['categories'].append(SubArea.objects.get(id=category['category']))

				# Se extrae el numero de pagina
				if request.GET.get('page'):
					try: parameters['documents'] = paginator.page(request.GET.get('page'))
					except: parameters['documents'] = paginator.page(1)
				else:
					parameters['documents'] = paginator.page(1)

		# Si es una busqueda
		else:
			documents = []
			high_acc_result = [] # Resultados de alta precision
			low_acc_result = [] # Resultados de baja precision

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
			


		return render(request, 'intranet/documents.html', parameters)
	elif request.user.is_authenticated() and request.user.is_admin:
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
				documents = Document.objects.filter(owner=user_id).order_by('-date_added')

				return render(request, 'intranet/profile.html', {'intranet': Section.objects.get(slug='intranet'), 'profile_user': profile, 'documents': documents, 'areas': Area.objects.all(), 'countries': list(countries)})
			except Exception as error:
				print error
				return HttpResponseRedirect(reverse('intranet:users'))
		elif request.method == 'POST':
			# Si el metodo es POST
			request.user.first_name = request.POST['first_name']
			request.user.last_name = request.POST['last_name']
			request.user.institution = request.POST['institution']
			request.user.career = request.POST['career']
			request.user.area = SubArea.objects.get(id=request.POST['area'])
			request.user.first_name = request.POST['first_name']
			request.user.country = request.POST['country']
			request.user.facebook = request.POST.get('facebook')
			request.user.twitter = request.POST.get('twitter')
			request.user.linkedin = request.POST.get('linkedin')
			request.user.bio = request.POST.get('bio')
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
			return render(request, 'intranet/upload.html', {'intranet': Section.objects.get(slug='intranet')})
		else:
			# En este caso se esta modificando la informacion de un documento
			if 'id' in request.POST:
				ids = request.POST['id'].split(',')
				for id in ids:
					document = Document.objects.get(id=id,owner=request.user)
					document.title = request.POST.get('title' + id)
					document.author = request.POST.get('author' + id)
					document.date = datetime.strptime(request.POST.get('date' + id), "%d-%m-%Y")
					document.category = SubArea.objects.get(id=request.POST.get('category' + id))
					document.is_public = int(request.POST.get('type' + id))
					document.abstract = request.POST.get('abstract' + id)
					document.issn = request.POST.get('issn' + id)
					document.doi = request.POST.get('doi' + id)
					document.pages = request.POST.get('pages' + id)
					document.is_available = True
					document.save()
				return JsonResponse({'error': False, 'message': _(u'Actualizado con éxito.')})

			# Aqui se esta creando un documento desde los archivos locales del usuario
			# user_side_ids son las ids de los archivos locales del usuario
			elif 'user_side_ids' in request.POST:
				user_side_ids = request.POST.get('user_side_ids').split(',')
				local_ids=[]
				for id in user_side_ids:
					
					# Si el tamaño supera los 30 mb, se muestra un mensaje de error
					if request.FILES['document'+id].size/1000 > 30720:
						return JsonResponse({'error': True, 'message': _(u'El archivo %(name)s no debe superar los 2 Mb') % {'name': request.FILES['document'+id].name}})

					# Si el documento ya existe, se muestra un mensaje de error
					if Document.objects.filter(title=request.POST['title'+id], author=request.POST['author'+id]).exists():
						message = _(u'El documento <span style="text-transform: uppercase; font-size:14px"> %(title)s </span> del autor <span style="text-transform: uppercase; font-size:14px"> %(author)s </span> ya existe.') % {'title': request.POST['title'+id], 'author': request.POST['author'+id]}
						return JsonResponse({'error': True, 'message': message})

					# Se almacenan los datos
					fields = {
						'title': request.POST.get('title'+id),
						'author': request.POST.get('author'+id),
						'date': request.POST.get('date'+id),
						'is_public': int(request.POST.get('type'+id)),
						'category': int(request.POST.get('category' + id)),
						'owner': request.user.id,
						'issn': request.POST.get('issn' + id),
						'doi': request.POST.get('doi' + id),
						'pages': request.POST.get('pages' + id),
						}
					files = {
							'document': request.FILES.get('document'+id)
						}

					print fields
					print files
					form = DocumentForm(fields, files)
					print form.errors
					if form.is_valid():
						form.save()
					else:
						return JsonResponse({'error': True, 'message': _(u'Ocurrió un problema: %(error)s') % {'error': str(form.errors)}})
				return JsonResponse({'error': False, 'message': _('Subida exitosa'), 'local_ids': local_ids})
	elif request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return JsonResponse({'error': True, 'message': _(u'Debes iniciar sesión.')})

def upload_local(request):
	return render(request, 'intranet/upload_sections/local.html')

def upload_drive(request):
	return render(request, 'intranet/upload_sections/drive.html')

def local_form(request):
	return render(request, 'intranet/upload_sections/local_upload_form_template.html', {'areas': Area.objects.all()})

def drive_form(request):
	return render(request, 'intranet/upload_sections/drive_upload_form_template.html', {'areas': Area.objects.all()})

# Extrae el contenido de los documentos identificados por las id recibidas
# Se usa al momento de subir archivos por Google Drive. El cliente llama a esta funcion explicitamente
def extract_content_and_keywords(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.POST['ids']:
			abstracts = []
			for id in request.POST['ids'].split(','):
				document = Document.objects.get(id=id) 
				document.save_abstract_and_content()
				document.keywords()
				abstracts.append({'id': document.id, 'abstract': document.abstract})
			return JsonResponse({'error': False, 'abstracts': abstracts})
		else:
			return JsonResponse({'error': True})
	elif request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return JsonResponse({'error': True, 'message': _(u'Debes iniciar sesión.')})

def pdf_viewer(request, title=None, author=None, id=None):
	try:
		if title is None and author is None and id is not None:
			# Solo usuarios dueños de un archivo o administradores pueden visualizarlo solo con la id
			if request.user.is_authenticated():
				document = Document.objects.get(id=id, owner=request.user)
			elif request.user.is_authenticated() and request.user.is_admin:
				document = Document.objects.get(id=id)
			else: 
				document = None
		else:			
			document = Document.objects.get(title_slug=title, author_slug=author, is_available=True)
	except Document.DoesNotExist:
		document = None
	if document is not None:
		if ((not document.is_public and request.user.is_authenticated()) or document.is_public):
			#Informacion por 'rb': http://stackoverflow.com/questions/11779246/how-to-show-a-pdf-file-in-a-django-view
			with open(document.document.path, 'rb') as pdf:
				response =  HttpResponse(pdf.read(), content_type='application/pdf')
				response['Content-Disposition'] = 'inline;filename="some_file.pdf"'.replace('some_file', document.title)
				response['Content-Length'] = os.stat(document.document.path).st_size
				return response
			pdf.close()
		else:
			return HttpResponseRedirect(reverse('login'))
	else:
		return HttpResponseRedirect(reverse('intranet:documents'))

def users(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		users = User.objects.filter(is_admin=False, is_registered=True)
		for user in users:
			user.last_activity = (timezone.localtime(timezone.now()) - user.last_activity).days
		return render(request, 'intranet/users.html', {'users': users, 'intranet': Section.objects.get(slug='intranet')})
	elif request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))


def document(request, title=None, author=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		try:
			document = Document.objects.get(title_slug=title, author_slug=author)
		except Document.DoesNotExist:
			document = None
		if document is not None:
			return render(request, 'intranet/document_information.html', {'intranet': Section.objects.get(slug='intranet'), 'document': document})
		else:
			return HttpResponseRedirect(reverse('intranet:documents'))
	elif request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))


def edit_document(request, id=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		try:
			if request.user.is_admin:
				document = Document.objects.get(id=id)
			else:
				document = Document.objects.get(id=id, owner=request.user)
		except:
			document = None
		if document:
			if request.method == "GET":
				return render(request, 'intranet/edit_document_information.html', {'intranet': Section.objects.get(slug='intranet'), 'document': document, 'areas': Area.objects.all()})
			elif request.method == "POST":
					document.title = request.POST['title']
					document.author = request.POST['author']
					document.date = datetime.strptime(request.POST['date'], "%d-%m-%Y")
					document.category = SubArea.objects.get(id=request.POST['category'])
					document.abstract = request.POST['abstract']
					document.issn = request.POST['issn']
					document.doi = request.POST['doi']
					document.words = request.POST['words']
					document.url = "http://dx.doi.org/" + request.POST['doi']
					document.pages = request.POST['pages']
					document.save()
					return HttpResponseRedirect(reverse('intranet:document', kwargs={'title': document.title_slug, 'author': document.author_slug}))
			elif request.method == "DELETE":
				document.owner.doc_number('-')
				document.delete()
				return JsonResponse({'error': False})
		else:
			return HttpResponseRedirect(reverse('intranet:documents')) #Se redirecciona a Documentos.
	elif request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))


def search_helper(request, search=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		doc = Document.objects.values('title', 'author').filter(reduce(operator.and_, (Q(title__contains=x) for x in search.split(' '))))
		response = {'error': False, 'list': list(doc)}
		return JsonResponse(response)
	elif request.user.is_authenticated() and request.user.is_admin:
		return HttpResponseRedirect(reverse('webpage:home'))
	else:
		return HttpResponseRedirect(reverse('login'))


def news(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		return render(request, 'intranet/news.html', {'intranet': Section.objects.get(slug='intranet'), 'user_news': News.objects.filter(author=request.user).order_by('-date')})
	else:
		return HttpResponseRedirect(reverse('login'))


def news_create(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.method == "GET":
			return render(request, 'intranet/news_create.html', {'intranet': Section.objects.get(slug='intranet'), 'today': date.today()})
		elif request.method == "POST":
			request.POST['author'] = request.user.id
			request.POST['title'] = _(u"Noticia sin título")
			request.POST['title_html'] = '<h1 class="c12">' + _(u"Noticia sin título") + '</h1>'
			form = NewsForm(request.POST, request.FILES)
			if form.is_valid():
				news = form.save()
				news.set_thumbnail_filename()
				if news.header:
					news.set_header_filename()
				return JsonResponse({'error': False, 'id': news.id})	
			else:
				return JsonResponse({'error': True, 'message': form.errors})	
	else:
		return HttpResponseRedirect(reverse('login'))

def news_edit(request, id):
	if request.user.is_authenticated() and not request.user.is_admin:
		news = News.objects.filter(id=id, author=request.user)
		if news:
			news = news[0]
			if request.method == "GET":
				if news.is_external:
					return render(request, 'intranet/news_edit_link.html', {'intranet': Section.objects.get(slug='intranet'), 'news_': news})
				else:
					return render(request, 'intranet/news_edit.html', {'intranet': Section.objects.get(slug='intranet'), 'news_': news})
			elif request.method == "POST":
					if news.is_external and (request.POST.get('source_url') is None and request.POST.get('source_url') == ""):
						return JsonResponse({'error': True, 'message': 'form.errors'})
					news.date = datetime.strptime(request.POST.get('date'), "%d-%m-%Y")
					news.source_text = request.POST.get('source_text')
					news.source_url = request.POST.get('source_url')
					news.in_header = False
					news.is_published = False
					if request.POST.get('title'):
						news.title = request.POST.get('title') if request.POST.get('title') != "" and request.POST.get('title') != "undefined"  else _(u"Noticia sin título")
					if request.FILES.get('thumbnail'):
						news.update_thumbnail(request.FILES.get('thumbnail'))
					if request.FILES.get('header'):
						news.update_header(request.FILES.get('header'))
					news.save()				
					return JsonResponse({'error': False, 'id': news.id})	
		else:
			return HttpResponseRedirect(reverse('intranet:news'))	
	else:
		if request.user.is_admin:
			return HttpResponseRedirect(reverse('admin:news'))
		return HttpResponseRedirect(reverse('login'))


def news_create_link(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.method == "GET":
			return render(request, 'intranet/news_create_link.html', {'intranet': Section.objects.get(slug='intranet'), 'today': date.today()})
		elif request.method == "POST":
			request.POST['author'] = request.user.id
			request.POST['is_external'] = '1'
			form = NewsForm(request.POST, request.FILES)
			if form.is_valid():
				news = form.save()
				news.set_thumbnail_filename()
				if news.header:
					news.set_header_filename()
				return JsonResponse({'error': False, 'id': news.id})	
			else:
				return JsonResponse({'error': True, 'message': form.errors})	
	else:
		return HttpResponseRedirect(reverse('login'))


def news_delete(request, id):
	if request.user.is_authenticated():
		news = News.objects.filter(id=id)
		if news:
			news = news[0]
			if news.author == request.user or request.user.is_admin:
				news.delete()

		if request.is_ajax():
			return JsonResponse({'error': False})
		else:
			return HttpResponseRedirect(reverse('intranet:news'))

	else:
		if request.is_ajax():
			return JsonResponse({'redirect': reverse('login')})
		else:
			return HttpResponseRedirect(reverse('login'))

def forum_list(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		paginator = Paginator(Forum.objects.all().order_by('-date'), 8)

		# Se extrae el numero de pagina
		if request.GET.get('page'):
			try: forum = paginator.page(request.GET.get('page'))
			except: forum = paginator.page(1)
		else:
			forum = paginator.page(1)
		return render(request, 'intranet/forums.html', {'intranet': Section.objects.get(slug='intranet'), 'forum_list': forum})	
	else:
		return HttpResponseRedirect(reverse('login'))

def forum(request, title=None):
	if request.user.is_authenticated() and not request.user.is_admin:
		forum = Forum.objects.filter(slug=title)
		if forum:
			forum = forum[0]
			paginator = Paginator(forum.get_comments(), 8)
			# Se extrae el numero de pagina
			if request.GET.get('page'):
				try: comments = paginator.page(request.GET.get('page'))
				except: comments = paginator.page(1)
			else:
				comments = paginator.page(1)
			return render(request, 'intranet/forum.html', {'intranet': Section.objects.get(slug='intranet'), 'forum': forum, 'comments': comments})	
		else:
			return HttpResponseRedirect(reverse('intranet:forum'))
	else:
		return HttpResponseRedirect(reverse('login'))

def forum_create(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.method == 'GET':
			return render(request, 'intranet/forum_create.html', {'intranet': Section.objects.get(slug='intranet')})	

		elif request.method == 'POST':
			mutable = request.POST._mutable
			request.POST._mutable = True
			request.POST['author'] = request.user.id
			request.POST._mutable = mutable
			form = ForumForm(request.POST)
			print form.errors
			if form.is_valid():
				forum = form.save()
				return HttpResponseRedirect(reverse('intranet:forum', kwargs={'title': forum.slug}))
			return HttpResponseRedirect(reverse('intranet:forum'))	
		
	return HttpResponseRedirect(reverse('login'))

def forum_new_comment(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.method == 'GET':
			return HttpResponseRedirect(reverse('intranet:forum'))	

		elif request.method == 'POST':
			mutable = request.POST._mutable
			request.POST._mutable = True
			request.POST['author'] = request.user.id
			request.POST._mutable = mutable
			if request.POST.get('content') and request.POST.get('forum'):
				forum = Forum.objects.filter(id=request.POST.get('forum'))
				if forum:
					forum = forum[0]
					comment = ForumComment(author=request.user, content=request.POST.get('content'), forum=forum)
					cite = None
					if request.POST.get('cite_comment'):
						cite = ForumComment.objects.filter(id=request.POST.get('cite_comment'))
					if request.POST.get('cite_forum'):
						cite = Forum.objects.filter(id=request.POST.get('cite_forum'))
					if cite:
						comment.content_object = cite[0]
					comment.save()
					paginator = Paginator(forum.get_comments(), 8)
					count = 0
					for p in paginator.page_range:
						count += 1
					print count
					return HttpResponseRedirect(reverse('intranet:forum', kwargs={'title': forum.slug}) + '?page=' + str(count) + '#comment')
			return HttpResponseRedirect(reverse('intranet:forum'))	
		
	return HttpResponseRedirect(reverse('login'))

def forum_remove(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.GET.get('id'):
			forum = Forum.objects.filter(id=request.GET.get('id'), author=request.user)
			if forum and forum[0].can_remove():
				forum = forum[0]
				forum.delete()
		return HttpResponseRedirect(reverse('intranet:forum'))
		
	return HttpResponseRedirect(reverse('login'))

def forum_remove_comment(request):
	if request.user.is_authenticated() and not request.user.is_admin:
		if request.GET.get('id'):
			comment = ForumComment.objects.filter(id=request.GET.get('id'), author=request.user)
			if comment and comment[0].can_remove():
				comment = comment[0]
				slug = comment.forum.slug
				comment.delete()
		return HttpResponseRedirect(reverse('intranet:forum', kwargs={'title': slug}))
		
	return HttpResponseRedirect(reverse('login'))