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
            documents = []
            high_acc_result = []
            low_acc_result = []
            for document in all_docs:
                result = document.match(search)
                if result['match']:
                    if result['extract'] != '':
                        setattr(document, 'extract', result['extract'])
                    if result['exact']:
                        high_acc_result.append(document)
                    else:
                        low_acc_result.append(document)
            documents = high_acc_result + low_acc_result
        parameters = {'current_view': 'publications', 'documents': documents}
        if search is not None:
            parameters['search'] = search
        return render(request, 'public_search/search.html',parameters)