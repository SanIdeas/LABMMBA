from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from intranet.forms import DocumentForm
from intranet.models import Document
from django.db.models import Q
from login.models import User
from unidecode import unidecode
import os, sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from PyPDF2 import PdfFileWriter, PdfFileReader
from cStringIO import StringIO
import unicodedata
from datetime import date
from django.utils import timezone

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

def home(request, search=None):
	if request.user.is_authenticated() == True:
		all_docs = Document.objects.all()
		if search is None: #Si no es una busqueda
			documents = all_docs
		else:
			split_search = unidecode(search.lower()).split(' ')
			documents = []
			for document in all_docs:
				result = document.match(split_search)
				if result['match']:
					if result['extract'] != '':
						setattr(document, 'extract', result['extract'])
					documents.append(document)
		parameters = {'current_view': 'intranet', 'documents': documents}
		if search is not None:
			parameters['search'] = search
		return render(request, 'intranet/home.html',parameters)
	else:
		print request.get_full_path
		return HttpResponseRedirect(reverse('login'))

def profile(request, user_id):
	if request.user.is_authenticated() == True:
		profile = User.objects.get(id=user_id)
		documents = Document.objects.filter(owner=user_id)
		return render(request, 'intranet/profile.html', {'current_view': 'intranet', 'profile_user': profile, 'documents': documents})
	else:
		return HttpResponseRedirect(reverse('login'))

def update_profile_picture(request):
	if request.user.is_authenticated() == True:
		User.objects.get(id=request.user.id).update_picture(request.FILES['picture'])
		return HttpResponseRedirect(reverse('profile', args={request.user.id}))

def upload(request):
	if request.user.is_authenticated() == True:
		#Document.objects.all().delete()
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
					document.category = request.POST['category' + id]
					document.type = request.POST['type' + id]
					document.abstract = request.POST['abstract' + id]
					document.save()
				return JsonResponse({'error': False, 'message':'Actualizado con exito.'})
			elif 'local_ids' in request.POST:
				local_ids = request.POST['local_ids'].split(',')
				for id in local_ids:
					if request.FILES['document'+id].size/1000 > 2048:
						return JsonResponse({'error': True, 'message':'El archivo ' + request.FILES['document'+id].name + ' no debe superar los 2 Mb'})

					if Document.objects.filter(title=request.POST['title'+id], author=request.POST['author'+id]).exists():
						return JsonResponse({'error': True, 'message':'El documento <span style="text-transform: uppercase; font-size:14px">' + request.POST['title'+id] + '</span> del autor <span style="text-transform: uppercase; font-size:14px">' + request.POST['author'+id] + '</span style="font-size:100%"> ya existe.'})

					request.POST['owner'] = User.objects.get(email=request.user.email)
					fields = {
						'title': request.POST['title'+id],
						'author': request.POST['author'+id],
						'date': request.POST['date'+id],
						'type': int(request.POST['type'+id]),
						'category': request.POST['category'+id],
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
							text_file =	 open(document.document.url.replace('pdf', 'txt'), 'w')
							text_file.close()
						document.save_abstract()
					else:
						return JsonResponse({'error': True, 'message':'Ocurrio un problema: ' + str(form.errors)})
				return JsonResponse({'error': False, 'message':'Subida exitosa'})
	else:
		return JsonResponse({'error': True, 'message':'Debes iniciar sesion.'})


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
			return HttpResponse('Debes tener una cuenta para visualizar este archivo.')
	else:
		return HttpResponse('No se encontraron documentos con el nombre: ' + title)

def users(request):
	if request.user.is_authenticated() == True:
		users = User.objects.all()
		for user in users:
			user.last_activity = (timezone.localtime(timezone.now()).date() - user.last_activity).days
		return render(request, 'intranet/users.html', {'users': users})
	else:
		return HttpResponseRedirect(reverse('login'))