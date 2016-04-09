from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
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
from cStringIO import StringIO
import unicodedata

# Create your views here.
def strip_accents(s):
	s = s.decode("cp1252")  # decode from cp1252 encoding instead of the implicit ascii encoding used by unicode()
	s = unicodedata.normalize('NFKD', s).encode('ascii','ignore')
	return s
	
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

def profile(request):
	if request.user.is_authenticated() == True:
		return render(request, 'intranet/profile.html', {'current_view': 'intranet'})
	else:
		return HttpResponseRedirect(reverse('login'))

def upload(request):
	if request.user.is_authenticated() == True:
		#Document.objects.all().delete()
		if request.method == "GET":
			return render(request, 'intranet/upload.html', {'current_view': 'intranet'})
		else:
			if request.FILES['document'].size/1000 > 2048:
				return render(request, 'intranet/upload.html', {'current_view': 'intranet', 'message': 'El archivo no debe superar los 2 Mb'})
			request.POST['owner'] = User.objects.get(email=request.user.email)
			form = DocumentForm(request.POST, request.FILES)
			print form.errors
			if form.is_valid():
				final_form = form.save(commit=False)
				final_form.owner = request.user
				document = form.save()
				try:
					text_file = open(document.document.url.replace('pdf', 'txt'), 'w')
					text_from_file = strip_accents(convert_pdf_to_txt(document.document.url))
					text_file.write(text_from_file.lower())
					text_file.close()
				except:
					None
				return render(request, 'intranet/upload.html', {'current_view': 'intranet'})
			else:
				return render(request, 'intranet/upload.html', {'current_view': 'intranet'})
	else:
		return HttpResponseRedirect(reverse('login'))


def pdf_viewer(request, title=None, author=None):
	try:
		document = Document.objects.get(title=title, author=author)
	except Document.DoesNotExist:
		document = None
	if document is not None:
		if ((document.type and request.user.is_authenticated()) or not document.type):
			print '----------------', document.document.url
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