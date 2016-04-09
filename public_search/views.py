from django.shortcuts import render
from intranet.models import Document
from unidecode import unidecode
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.

def search(request, search=None):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('intranet'))
	else:
		all_docs = Document.objects.filter(type=False)#Solo documentos publicos
		if search is None: #Si no es una busqueda
			documents = all_docs
		else:
			split_search = unidecode(search.lower()).split(' ')
			print '.................', split_search
			documents = []
			for document in all_docs:
				if document.match(split_search)['match']:
					if document.match(split_search)['extract'] != '':
						setattr(document, 'extract', document.match(split_search)['extract'])
					documents.append(document)
		parameters = {'current_view': 'publications', 'documents': documents}
		if search is not None:
			parameters['search'] = search
		return render(request, 'public_search/search.html',parameters)